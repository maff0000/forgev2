"""ForgeV2 shared helpers: repository identity, ledger, session pointers.

Standard library only. Every state change goes through the ledger file under
an exclusive lock so concurrent hook invocations cannot double-count.
"""
import fcntl
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone

ROLES = ("engineer", "auditor", "tester", "devsecops")
REVIEWERS = ("auditor", "tester", "devsecops")
LIMIT = 4  # executions per specialist per Work Order, including the first (FV2-D008)
PLUGIN = "forgev2"
WO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,62}$")
SESSION_RE = re.compile(r"^[A-Za-z0-9-]{8,128}$")
OWNER_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")


class ForgeError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise ForgeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


# --- repository identity -------------------------------------------------

_URL_FORMS = (
    re.compile(r"^https://(?:[^@/]+@)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"),
    re.compile(r"^ssh://git@github\.com(?::22)?/([^/]+)/([^/]+?)(?:\.git)?/?$"),
    re.compile(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$"),
)


def parse_github_remote(url):
    """Return 'owner/name' (lower-case) for an exact github.com remote, else None.

    Only the three canonical GitHub URL forms are accepted. Look-alike hosts
    (github.com.evil, evilgithub.com), extra path segments and local paths
    are rejected rather than pattern-matched on the string 'github.com'.
    """
    url = url.strip()
    for form in _URL_FORMS:
        m = form.match(url)
        if m:
            slug = f"{m.group(1)}/{m.group(2)}"
            if OWNER_NAME_RE.match(slug) and ".." not in slug:
                return slug.lower()
    return None


def check_repo(path, expect, known_commit=None):
    """Verify path is the top level of the expected repository. Returns facts dict."""
    if not OWNER_NAME_RE.match(expect or ""):
        raise ForgeError(f"expected repository must be OWNER/NAME, got {expect!r}")
    path = os.path.realpath(path)
    if not os.path.isdir(path):
        raise ForgeError(f"project root does not exist: {path}")
    top = git("rev-parse", "--show-toplevel", cwd=path, check=False)
    if not top:
        raise ForgeError(f"not a git repository: {path}")
    if os.path.realpath(top) != path:
        raise ForgeError(f"{path} is not the repository top level ({top})")
    for kind, flag in (("fetch", []), ("push", ["--push"])):
        url = git("remote", "get-url", *flag, "origin", cwd=path, check=False)
        got = parse_github_remote(url) if url else None
        if got != expect.lower():
            raise ForgeError(
                f"repository identity mismatch: origin {kind} URL resolves to "
                f"{got or 'an unrecognised remote'}, expected {expect}")
    if known_commit:
        if git("cat-file", "-t", known_commit, cwd=path, check=False) != "commit":
            raise ForgeError(f"known commit {known_commit} is not in this repository's history")
    return {"root": path, "repo": expect.lower(),
            "common_dir": os.path.realpath(os.path.join(path, git("rev-parse", "--git-common-dir", cwd=path)))}


# --- state locations -----------------------------------------------------

def state_dir():
    d = os.environ.get("FORGE_STATE_DIR") or os.path.join(
        os.path.expanduser("~"), ".local", "state", "forgev2")
    os.makedirs(os.path.join(d, "sessions"), mode=0o700, exist_ok=True)
    return d


def session_pointer(session_id):
    if not session_id or not SESSION_RE.match(session_id):
        raise ForgeError("missing or invalid Claude session id")
    return os.path.join(state_dir(), "sessions", session_id)


def ledger_for_session(session_id):
    try:
        with open(session_pointer(session_id)) as f:
            p = f.read().strip()
    except (FileNotFoundError, ForgeError):
        return None
    return p if os.path.isfile(p) else None


def bind_session(session_id, ledger_path):
    p = session_pointer(session_id)
    with open(p, "w") as f:
        f.write(ledger_path + "\n")
    os.chmod(p, 0o600)


# --- ledger ---------------------------------------------------------------

def new_ledger(wo, repo, root, worktree, branch, base_sha, scratch):
    return {"wo": wo, "repo": repo, "root": root, "worktree": worktree,
            "branch": branch, "base_sha": base_sha, "scratch": scratch,
            "limit": LIMIT, "created": now(), "counts": {r: 0 for r in ROLES},
            "candidate": None, "round": 0, "events": [], "outcome": None}


@contextmanager
def locked_ledger(path, write=True):
    fd = os.open(path, os.O_RDWR)
    with os.fdopen(fd, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        data = json.load(f)
        yield data
        if write:
            f.seek(0)
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
            f.truncate()


def write_new_ledger(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "x") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def spawn(data, role):
    """Count one execution of role. Raises ForgeError if not permitted."""
    if role not in ROLES:
        raise ForgeError(f"unknown role {role}")
    if data["outcome"]:
        raise ForgeError(f"Work Order {data['wo']} is closed ({data['outcome']}); no further dispatch")
    if data["counts"][role] >= data["limit"]:
        raise ForgeError(
            f"{role} has used {data['counts'][role]}/{data['limit']} executions for {data['wo']}. "
            "A further execution is prohibited: close the Work Order as ESCALATED with the open findings.")
    if role in REVIEWERS:
        if not data["candidate"]:
            raise ForgeError("no committed candidate: commit the Engineer's work with forge-commit before review")
        head = git("rev-parse", "HEAD", cwd=data["worktree"])
        dirty = git("status", "--porcelain", "--", ".", ":!.forge", cwd=data["worktree"])
        if head != data["candidate"] or dirty:
            raise ForgeError("worktree does not match the recorded candidate (uncommitted or newer changes); "
                             "commit with forge-commit before review")
    if role == "engineer":
        data["round"] += 1
    data["counts"][role] += 1
    data["events"].append({"t": now(), "type": "spawn", "role": role,
                           "n": data["counts"][role], "round": data["round"],
                           "candidate": data["candidate"]})


def record(data, role, outcome, findings=(), note=""):
    valid = {"engineer": ("completed", "blocked", "failed")}.get(role, ("pass", "findings", "inconclusive"))
    if role not in ROLES or outcome not in valid:
        raise ForgeError(f"{role} outcome must be one of {valid}")
    parsed = []
    for f in findings:
        key, _, sev = f.partition(":")
        sev = sev or "blocking"
        if not SLUG_RE.match(key) or sev not in ("blocking", "advisory", "rejected"):
            raise ForgeError(f"finding must be KEY[:blocking|advisory|rejected], got {f!r}")
        parsed.append({"key": key, "severity": sev})
    if role in REVIEWERS and outcome == "findings" and not parsed:
        raise ForgeError("a findings outcome needs at least one --finding")
    if role in REVIEWERS and outcome == "pass" and any(p["severity"] == "blocking" for p in parsed):
        raise ForgeError("a pass outcome cannot carry blocking findings")
    if data["counts"][role] == 0:
        raise ForgeError(f"{role} has not been dispatched")
    data["events"].append({"t": now(), "type": "result", "role": role, "outcome": outcome,
                           "findings": parsed, "note": note, "round": data["round"],
                           "candidate": data["candidate"]})


def decide(data):
    """Return (decision, reason). Decisions: REVIEW, CORRECT, DELIVER, ESCALATE, BLOCKED, BUILD."""
    if data["outcome"]:
        return data["outcome"], "Work Order closed"
    results = [e for e in data["events"] if e["type"] == "result"]
    eng = [e for e in results if e["role"] == "engineer"]
    if not eng:
        return "BUILD", "dispatch the Engineer"
    if eng[-1]["outcome"] != "completed":
        return "BLOCKED", f"Engineer reported {eng[-1]['outcome']}: {eng[-1]['note']}"
    cand = data["candidate"]
    current = {e["role"]: e for e in results if e["role"] in REVIEWERS and e["candidate"] == cand}
    missing = [r for r in REVIEWERS if r not in current]
    if missing:
        return "REVIEW", f"candidate {str(cand)[:12]} still needs: {', '.join(missing)}"
    blocking = sorted({f["key"] for r in current.values() for f in r["findings"] if f["severity"] == "blocking"})
    inconclusive = [r for r, e in current.items() if e["outcome"] == "inconclusive"]
    if not blocking and not inconclusive:
        return "DELIVER", "Auditor, Tester and DevSecOps PASS on the current candidate"
    # Anti-loop: the same blocking finding surviving a correction means no progress.
    prior = {f["key"] for e in results if e["role"] in REVIEWERS and e["candidate"] != cand
             for f in e["findings"] if f["severity"] == "blocking"}
    repeated = sorted(set(blocking) & prior)
    if repeated:
        return "ESCALATE", f"no progress: blocking finding(s) survived a correction: {', '.join(repeated)}"
    prev_inc = [e for e in results if e["role"] in REVIEWERS and e["outcome"] == "inconclusive"
                and e["candidate"] != cand]
    if inconclusive and prev_inc:
        return "ESCALATE", "INCONCLUSIVE on two consecutive candidates; resolve the environment"
    if data["counts"]["engineer"] >= data["limit"] or any(
            data["counts"][r] >= data["limit"] for r in REVIEWERS):
        return "ESCALATE", f"execution limit reached with open items: {', '.join(blocking + inconclusive)}"
    if inconclusive and not blocking:
        return "REVIEW", f"re-run after resolving environment for: {', '.join(inconclusive)}"
    return "CORRECT", f"route to Engineer: {', '.join(blocking)}"


def emit(obj):
    json.dump(obj, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
