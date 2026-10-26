"""ForgeV2 shared helpers: repository identity, ledger, Git, gitleaks and dispatch wrappers.

Standard library only. The ledger and delivery records live in the PL's private
state directory, never in a worktree, and every change to the ledger is made
under an exclusive lock with an atomic replace. Specialists run as separate,
fresh Claude processes under the PL's own account (one Claude login), inside
Claude Code's sandbox: bubblewrap for their commands and permission rules for
their file tools. That is weaker than a separate Unix account; see README.md.
"""
import fcntl
import hashlib
import json
import os
import pwd
import re
import stat
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone

ROLES = ("engineer", "auditor", "tester", "devsecops")
REVIEWERS = ("auditor", "tester", "devsecops")
LIMIT = 4  # executions per specialist per Work Order, including the first (FV2-D008)
PLUGIN = "forgev2"
LIB = os.path.dirname(os.path.realpath(__file__))
WO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,62}$")
SESSION_RE = re.compile(r"^[A-Za-z0-9-]{8,128}$")
OWNER_NAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")
PROTECTED_BRANCHES = ("main", "master")

# Specialists: fresh `claude -p` processes in Claude Code's sandbox (bubblewrap + socat).
CLAUDE = "/usr/local/bin/claude"
SANDBOX_DEPS = ("/usr/bin/bwrap", "/usr/bin/socat")
PLUGIN_ROOT = os.path.dirname(LIB)
SPECIALIST_TOOLS = {"Read", "Grep", "Glob", "Edit", "Write", "Bash"}
MAX_PROMPT = 256 * 1024

# gitleaks binaries accepted for the commit and push scans (requirement 5).
# Add a digest only after verifying the release checksum; see INSTALL.md.
GITLEAKS_PATHS = ("/usr/local/bin/gitleaks", "/usr/bin/gitleaks")
GITLEAKS_SHA256 = {
    "88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509": "8.30.1 linux x64",
}


class ForgeError(Exception):
    pass


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def require_non_root():
    """Delivery runs as a non-root account (FV2-D019). Returns True if a dev override is in use."""
    if os.geteuid() != 0:
        return False
    if os.environ.get("FORGE_ALLOW_ROOT") == "1":
        return True
    raise ForgeError("ForgeV2 delivery must not run as root; run the PL as its service account "
                     "(FORGE_ALLOW_ROOT=1 is for a development host only)")


# --- Git -----------------------------------------------------------------

_GIT_ENV_DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
                 "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
                 "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES", "GIT_EXEC_PATH", "GIT_SSH", "GIT_SSH_COMMAND",
                 "GIT_PROXY_COMMAND", "GIT_ASKPASS")


def _env(extra=None):
    env = {k: v for k, v in os.environ.items()
           if k not in _GIT_ENV_DROP and not k.startswith(("GITLEAKS_", "GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    env.update(extra or {})
    return env


def git_run(*args, cwd=None, env=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=_env(env))


def git(*args, cwd=None, check=True, env=None):
    r = git_run(*args, cwd=cwd, env=env)
    if check and r.returncode != 0:
        raise ForgeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def wt_env(d):
    """Git environment for a Work Order worktree. The worktree's own `.git` pointer
    file is never trusted: the PL-recorded Git directory is named explicitly."""
    return {"GIT_DIR": d["git_dir"], "GIT_WORK_TREE": d["worktree"]}


def wgit(d, *args, check=True):
    return git("-c", "core.fsmonitor=false", *args, cwd=d["worktree"], check=check, env=wt_env(d))


def is_ancestor(d, a, b):
    return git_run("-c", "core.fsmonitor=false", "merge-base", "--is-ancestor", a, b,
                   cwd=d["worktree"], env=wt_env(d)).returncode == 0


# --- repository identity -------------------------------------------------

_URL_FORMS = (
    re.compile(r"^https://(?:[^@/:]+@)?github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$"),
    re.compile(r"^ssh://git@github\.com(?::22)?/([^/]+)/([^/]+?)(?:\.git)?/?$"),
    re.compile(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$"),
)


def parse_github_remote(url):
    """Return 'owner/name' (lower-case) for an exact github.com remote, else None.

    Only the three canonical GitHub URL forms are accepted. Look-alike hosts,
    extra path segments, local paths and URLs embedding a password or token are
    rejected rather than pattern-matched on the string 'github.com'.
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
    r = git_run("rev-parse", "--show-toplevel", cwd=path)
    if r.returncode != 0:
        raise ForgeError(f"not a usable git repository: {path}: {r.stderr.strip()}")
    if os.path.realpath(r.stdout.strip()) != path:
        raise ForgeError(f"{path} is not the repository top level ({r.stdout.strip()})")
    if git("config", "--get-regexp", r"^url\.", cwd=path, check=False):
        raise ForgeError("URL rewriting (url.*.insteadOf / pushInsteadOf) is configured; "
                         "remote identity cannot be verified")
    urls = {}
    for kind, flag in (("fetch", []), ("push", ["--push"])):
        got = git("remote", "get-url", "--all", *flag, "origin", cwd=path, check=False).splitlines()
        if len(got) != 1:
            raise ForgeError(f"origin must have exactly one {kind} URL, found {len(got)}")
        slug = parse_github_remote(got[0])
        if slug != expect.lower():
            raise ForgeError(f"repository identity mismatch: origin {kind} URL resolves to "
                             f"{slug or 'an unrecognised remote'}, expected {expect}")
        urls[kind] = got[0].strip()
    if known_commit:
        if git("cat-file", "-t", known_commit, cwd=path, check=False) != "commit":
            raise ForgeError(f"known commit {known_commit} is not in this repository's history")
    common = os.path.realpath(os.path.join(path, git("rev-parse", "--git-common-dir", cwd=path)))
    return {"root": path, "repo": expect.lower(), "push_url": urls["push"], "common_dir": common}


# --- state locations -----------------------------------------------------

def _private_dir(d):
    os.makedirs(d, mode=0o700, exist_ok=True)
    st = os.stat(d)
    if st.st_uid != os.geteuid() or st.st_mode & 0o077:
        raise ForgeError(f"state directory {d} must be owned by this account with mode 0700")
    return d


def state_dir():
    d = os.environ.get("FORGE_STATE_DIR") or os.path.join(os.path.expanduser("~"), ".local", "state", "forgev2")
    _private_dir(d)
    _private_dir(os.path.join(d, "sessions"))
    _private_dir(os.path.join(d, "ledgers"))
    return d


def ledger_path(root, wo):
    key = hashlib.sha256(os.path.realpath(root).encode()).hexdigest()[:16]
    return os.path.join(state_dir(), "ledgers", key, wo, "ledger.json")


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


def bind_session(session_id, path):
    p = session_pointer(session_id)
    _atomic_write(p, path + "\n")


def records_root(root, wo):
    key = hashlib.sha256(os.path.realpath(root).encode()).hexdigest()[:16]
    return os.path.join(state_dir(), "records", key, wo)


def dispatch_dir(ledger):
    """Raw specialist outputs, written only by forge-dispatch, beside the ledger."""
    return os.path.join(os.path.dirname(ledger), "dispatch")


RECORD_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


def record_paths_ok(d, paths):
    """Only the delivery record files may follow the reviewed candidate."""
    ok = re.compile(rf"^\.forge/{re.escape(d['wo'])}/(ledger\.json|REPORT\.md|prompts/[A-Za-z0-9._-]+\.md"
                    r"|dispatch/[0-9]+-[a-z]+\.json)$")
    return all(ok.match(p) for p in paths)


def _pl_dir_at(parent_fd, name):
    """Open (creating if absent) a PL-owned directory without following symlinks."""
    try:
        os.mkdir(name, 0o755, dir_fd=parent_fd)
    except FileExistsError:
        pass
    replaced = ForgeError(f"{name} in the worktree record path is not a plain PL-owned directory; "
                          "it was replaced in the worktree - the Work Order must be BLOCKED")
    try:
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError:
        raise replaced
    st = os.fstat(fd)
    if st.st_uid != os.geteuid() or st.st_mode & 0o022:
        os.close(fd)
        raise replaced
    return fd


def publish_records(d, ledger):
    """Copy the ledger, REPORT.md, prompts and raw dispatch outputs into <worktree>/.forge/<WO>/.

    The Engineer writes the worktree, so every path component is opened without
    following symlinks and must be a plain directory, and every file is created
    fresh. Returns the published paths relative to the worktree."""
    rec = d["records"]
    if not os.path.isfile(os.path.join(rec, "REPORT.md")):
        raise ForgeError(f"write the delivery report to {rec}/REPORT.md first")
    files = {"ledger.json": _dump(d).encode()}
    for sub, pattern in (("", r"^REPORT\.md$"), ("prompts", r"\.md$")):
        src = os.path.join(rec, sub)
        for name in sorted(os.listdir(src)) if os.path.isdir(src) else []:
            p = os.path.join(src, name)
            if os.path.isdir(p) and not sub and name == "prompts":
                continue
            if not RECORD_NAME.match(name) or not re.search(pattern, name) or not os.path.isfile(p) \
                    or os.path.islink(p):
                raise ForgeError(f"unexpected file in the records directory: {p} "
                                 "(only REPORT.md and prompts/*.md are published)")
            with open(p, "rb") as f:
                files[os.path.join(sub, name)] = f.read()
    disp = dispatch_dir(ledger)
    for name in sorted(os.listdir(disp)) if os.path.isdir(disp) else []:
        with open(os.path.join(disp, name), "rb") as f:
            files[os.path.join("dispatch", name)] = f.read()
    fds = [os.open(d["worktree"], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    try:
        for name in (".forge", d["wo"]):
            fds.append(_pl_dir_at(fds[-1], name))
        subdirs = {}
        for rel, data in files.items():
            sub, name = os.path.split(rel)
            if sub and sub not in subdirs:
                subdirs[sub] = _pl_dir_at(fds[-1], sub)
            fd = subdirs[sub] if sub else fds[-1]
            try:
                os.unlink(name, dir_fd=fd)
            except FileNotFoundError:
                pass
            out = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=fd)
            with os.fdopen(out, "wb") as f:
                f.write(data)
        fds.extend(subdirs.values())
    finally:
        for fd in fds:
            os.close(fd)
    return [f".forge/{d['wo']}/{rel}" for rel in files]


# --- worktree preparation -------------------------------------------------

def prepare_worktree(wt):
    """Create <worktree>/.forge as a plain directory, so the sandbox can protect it from the start."""
    fd = os.open(wt, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.close(_pl_dir_at(fd, ".forge"))
    finally:
        os.close(fd)


def private_paths():
    """What specialists may never read: the account's home (Claude login, Git credentials,
    ledger, records), the Claude config directory and the ForgeV2 state directory."""
    home = pwd.getpwuid(os.geteuid()).pw_dir
    paths = [home, claude_config_dir(), state_dir()]
    return sorted({os.path.realpath(p) for p in paths})


def claude_config_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(pwd.getpwuid(os.geteuid()).pw_dir, ".claude")


def require_outside_private(*paths):
    for p in paths:
        for q in private_paths():
            if os.path.commonpath([os.path.realpath(p), q]) == q:
                raise ForgeError(f"{p} is inside {q}, which specialists cannot read; keep projects and "
                                 "worktrees outside the PL's home and state directories")


# --- ledger ---------------------------------------------------------------

def new_ledger(wo, facts, worktree, git_dir, branch, base, base_sha, known_commit, scratch, records):
    return {"wo": wo, "repo": facts["repo"], "root": facts["root"], "worktree": worktree, "git_dir": git_dir,
            "common_dir": facts["common_dir"], "branch": branch, "base": base, "base_sha": base_sha,
            "known_commit": known_commit, "scratch": scratch, "records": records, "limit": LIMIT, "created": now(),
            "counts": {r: 0 for r in ROLES}, "candidate": None, "round": 0, "events": [], "outcome": None}


def _atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    dfd = os.open(d, os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def _dump(data):
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


@contextmanager
def locked_ledger(path, write=True):
    lock = os.open(path + ".lock", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            with open(path) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ForgeError(f"ledger not found: {path}")
        except ValueError as e:
            raise ForgeError(f"ledger {path} is corrupt ({e}); the Work Order cannot continue - "
                             "close it as BLOCKED with a new Work Order id")
        yield data
        if write:
            _atomic_write(path, _dump(data))
    finally:
        os.close(lock)


def write_new_ledger(path, data):
    _private_dir(os.path.dirname(os.path.dirname(path)))
    _private_dir(os.path.dirname(path))
    if os.path.exists(path):
        raise ForgeError(f"ledger already exists: {path}")
    _atomic_write(path, _dump(data))


def pending(d, role=None):
    """Dispatches that have not yet had a result recorded."""
    done = {e["spawn"] for e in d["events"] if e["type"] == "result"}
    return [e for e in d["events"] if e["type"] == "spawn" and e["id"] not in done
            and (role is None or e["role"] == role)]


def worktree_matches_candidate(d):
    head = wgit(d, "rev-parse", "HEAD")
    dirty = wgit(d, "status", "--porcelain", "--", ".", ":!.forge")
    return head == d["candidate"] and not dirty


def spawn(data, role):
    """Count one execution of role. Raises ForgeError if not permitted."""
    if role not in ROLES:
        raise ForgeError(f"unknown role {role}")
    if data["outcome"]:
        raise ForgeError(f"Work Order {data['wo']} is closed ({data['outcome']}); no further dispatch")
    if data["counts"][role] >= LIMIT:
        raise ForgeError(
            f"{role} has used {data['counts'][role]}/{LIMIT} executions for {data['wo']}. "
            "A further execution is prohibited: close the Work Order as ESCALATED with the open findings.")
    if pending(data, role):
        raise ForgeError(f"{role} was already dispatched and has no recorded result; record it first "
                         "(use 'void' if the dispatch produced no result)")
    decision, reason = decide(data)
    if role == "engineer" and decision not in ("BUILD", "CORRECT", "COMMIT"):
        raise ForgeError(f"Engineer dispatch not permitted: next step is {decision} ({reason})")
    if role in REVIEWERS:
        if decision != "REVIEW" or role not in needs_review(data):
            raise ForgeError(f"{role} dispatch not permitted: next step is {decision} ({reason})")
        if not worktree_matches_candidate(data):
            raise ForgeError("worktree does not match the recorded candidate (uncommitted or newer changes); "
                             "commit with forge-commit before review")
    if role == "engineer":
        data["round"] += 1
    data["counts"][role] += 1
    data["events"].append({"t": now(), "type": "spawn", "id": len(data["events"]), "role": role,
                           "n": data["counts"][role], "round": data["round"], "candidate": data["candidate"]})


def record(data, role, outcome, findings=(), note=""):
    if data["outcome"]:
        raise ForgeError(f"Work Order {data['wo']} is closed ({data['outcome']}); results cannot be recorded")
    valid = {"engineer": ("completed", "blocked", "failed", "void")}.get(
        role, ("pass", "findings", "inconclusive", "void"))
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
    slots = pending(data, role)
    if not slots:
        raise ForgeError(f"{role} has no dispatch awaiting a result; each result needs its own dispatch")
    slot = slots[-1]
    if role in REVIEWERS and slot["candidate"] != data["candidate"]:
        raise ForgeError("the candidate changed after this reviewer was dispatched; its result is void")
    ran = [e for e in data["events"] if e["type"] == "dispatched" and e["spawn"] == slot["id"]]
    if not ran and outcome != "void":
        raise ForgeError(f"the {role} dispatch has not returned; record 'void' if it was lost")
    reported = ran[-1]["reported"] if ran else None
    if (role, outcome) in (("engineer", "completed"),) + tuple((r, "pass") for r in REVIEWERS) \
            and reported != outcome:
        raise ForgeError(f"the {role} reported {reported or 'no recognisable status line'}, so '{outcome}' "
                         "cannot be recorded for it")
    data["events"].append({"t": now(), "type": "result", "spawn": slot["id"], "role": role, "outcome": outcome,
                           "findings": parsed, "note": note, "round": slot["round"],
                           "candidate": slot["candidate"]})


def _results(d):
    return [e for e in d["events"] if e["type"] == "result" and e["outcome"] != "void"]


def _current_reviews(d):
    return {e["role"]: e for e in _results(d) if e["role"] in REVIEWERS and e["candidate"] == d["candidate"]}


def needs_review(d):
    current = _current_reviews(d)
    return [r for r in REVIEWERS if r not in current or current[r]["outcome"] == "inconclusive"]


def decide(data):
    """Return (decision, reason): BUILD, COMMIT, REVIEW, CORRECT, DELIVER, ESCALATE or BLOCKED."""
    if data["outcome"]:
        return data["outcome"], "Work Order closed"
    events = data["events"]
    results = _results(data)
    eng = [e for e in results if e["role"] == "engineer"]
    if not eng:
        return "BUILD", "dispatch the Engineer"
    if eng[-1]["outcome"] != "completed":
        return "BLOCKED", f"Engineer reported {eng[-1]['outcome']}: {eng[-1]['note']}"
    last_eng = max(i for i, e in enumerate(events) if e["type"] == "result" and e["role"] == "engineer"
                   and e["outcome"] == "completed")
    if any(e["type"] == "no_change" for e in events[last_eng:]):
        return "ESCALATE", "no progress: the Engineer's round produced no change to commit"
    cands = [i for i, e in enumerate(events) if e["type"] == "candidate"]
    if not cands or last_eng > cands[-1]:
        return "COMMIT", "commit the Engineer's work with forge-commit"
    cand = data["candidate"]
    current = _current_reviews(data)
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
    twice = [r for r in REVIEWERS
             if [e["outcome"] for e in results if e["role"] == r][-2:] == ["inconclusive", "inconclusive"]]
    if twice:
        return "ESCALATE", f"INCONCLUSIVE twice in a row from {', '.join(twice)}; resolve the environment"
    # The next step needs the Engineer and all three reviewers (correction) or the inconclusive reviewers.
    if any(data["counts"][r] >= LIMIT for r in (list(ROLES) if blocking else inconclusive)):
        return "ESCALATE", f"execution limit reached with open items: {', '.join(blocking + inconclusive)}"
    if blocking:
        return "CORRECT", f"route to Engineer: {', '.join(blocking)}"
    return "REVIEW", f"re-run after resolving the environment for: {', '.join(inconclusive)}"


# --- dispatch ---------------------------------------------------------------

_REPORTED = {"engineer": re.compile(r"^[\s>*`#]*STATUS\s*:\s*\**\s*(completed|blocked|failed)\b", re.I | re.M)}
for _r in REVIEWERS:
    _REPORTED[_r] = re.compile(r"^[\s>*`#]*VERDICT\s*:\s*\**\s*(PASS|FINDINGS|INCONCLUSIVE)\b", re.I | re.M)


def parse_reported(role, text):
    """The status a specialist reported in its own final message, or None if absent or ambiguous."""
    got = {m.lower() for m in _REPORTED[role].findall(text or "")}
    return got.pop() if len(got) == 1 else None


def _sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_role(role, roles_dir=None):
    """Role prompt and tool list from plugin/roles/<role>.md."""
    path = os.path.join(roles_dir or os.path.join(PLUGIN_ROOT, "roles"), f"{role}.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    tools = re.search(r"^tools:\s*(.+)$", m.group(1), re.M) if m else None
    if not tools:
        raise ForgeError(f"{path} has no front matter with a tools: line")
    names = [t.strip() for t in tools.group(1).split(",")]
    if not names or not set(names) <= SPECIALIST_TOOLS:
        raise ForgeError(f"{path} lists tools outside {sorted(SPECIALIST_TOOLS)}")
    return names, m.group(2).strip()


def check_runtime():
    """The sandbox needs bubblewrap and socat; Claude must be the root-owned system binary."""
    for dep in SANDBOX_DEPS:
        if not os.access(dep, os.X_OK):
            raise ForgeError(f"{dep} is missing: specialists run only inside the sandbox (INSTALL.md)")
    exe = os.environ.get("FORGE_CLAUDE")
    if exe:
        return exe
    for q in (CLAUDE, os.path.dirname(CLAUDE)):
        st = os.lstat(q)
        if stat.S_ISLNK(st.st_mode) or st.st_uid != 0 or st.st_mode & 0o022:
            raise ForgeError(f"{q} must be root-owned and not group/world-writable")
    return CLAUDE


def sandbox_settings(role, tools, worktree, scratch, home, private, git_dirs):
    """Claude settings for one specialist run. The Engineer may write the worktree (never .git or
    .forge) and scratch; reviewers only scratch. Commands run in bubblewrap with no network, a
    private /proc and no fallback to running unsandboxed; file tools follow the same paths.
    Git directories are denied explicitly: Claude's sandbox otherwise allows writing the Git
    directory of a repository it starts in (specialists start in scratch, not in the worktree)."""
    writable = ([worktree] if role == "engineer" else []) + [scratch]
    allow = [t for t in tools if t in ("Bash", "Read", "Grep", "Glob")]
    if {"Edit", "Write"} & set(tools):
        allow += [f"Edit(/{p}/**)" for p in writable]
    protected = [os.path.join(worktree, ".git"), os.path.join(worktree, ".forge")] + list(git_dirs)
    deny = [f"Read(/{p}/**)" for p in private] + [f"Edit(/{p})" for p in protected] + \
        [f"Edit(/{p}/**)" for p in protected]
    return {
        "disableAllHooks": True,
        "permissions": {"allow": allow, "deny": deny},
        "sandbox": {
            "enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
            "autoAllowBashIfSandboxed": True, "excludedCommands": [], "enableWeakerNestedSandbox": False,
            "allowNestedUserNamespaces": False,
            "filesystem": {"allowWrite": writable + [home], "denyWrite": protected, "denyRead": list(private)},
            "network": {"allowedDomains": [], "strictAllowlist": True},
        },
    }


def specialist_command(d, role, home, exe=CLAUDE):
    """The fixed command line, environment and working directory (scratch) for one specialist
    run in a fresh HOME. Returns (argv, env, cwd)."""
    tools, body = load_role(role)
    wt, scratch = d["worktree"], d["scratch"]
    private = private_paths()
    require_outside_private(wt, scratch, home)
    system = (f"{body}\n\nForgeV2 assignment: role {role}; worktree {wt}; scratch directory {scratch} "
              "(your starting directory; use `git -C <worktree>` and absolute paths for the worktree). "
              "You run in a sandbox: Git metadata, the delivery record, the PL's files and the network "
              "are not available to you" + ("" if role == "engineer" else ", and the worktree is read-only") + ".")
    settings = sandbox_settings(role, tools, wt, scratch, home, private, (d["git_dir"], d["common_dir"]))
    argv = [exe, "-p", "--output-format", "json", "--no-session-persistence", "--safe-mode",
            "--setting-sources", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--disable-slash-commands", "--tools", ",".join(tools), "--permission-mode", "dontAsk",
            "--settings", json.dumps(settings), "--append-system-prompt", system]
    user = pwd.getpwuid(os.geteuid()).pw_name
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": home, "TMPDIR": os.path.join(home, "tmp"),
           "USER": user, "LOGNAME": user, "SHELL": "/bin/bash", "LANG": "C.UTF-8",
           "CLAUDE_CONFIG_DIR": claude_config_dir(), "DISABLE_AUTOUPDATER": "1",
           "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "FORGE_ROLE": role}
    return argv, env, scratch


# --- gitleaks ---------------------------------------------------------------

def gitleaks_bin():
    allowed = dict(GITLEAKS_SHA256)
    for h in filter(None, os.environ.get("FORGE_GITLEAKS_SHA256", "").split(",")):
        allowed[h.strip().lower()] = "operator-approved"
    for p in GITLEAKS_PATHS:
        if not os.path.isfile(p):
            continue
        for q in (p, os.path.dirname(p)):
            st = os.stat(q)
            if st.st_uid != 0 or st.st_mode & 0o022:
                raise ForgeError(f"{q} must be root-owned and not group/world-writable")
        with open(p, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest not in allowed:
            raise ForgeError(f"{p} sha256 {digest} is not an approved gitleaks build")
        return p
    raise ForgeError("gitleaks is not installed at an approved path; refusing to commit or push unscanned changes")


def gitleaks_scan(d, *mode):
    """Scan with ForgeV2's own configuration. Repository allowlists, .gitleaksignore files and
    inline gitleaks:allow comments are not honoured: the scanned source is an empty directory and
    Git is pointed at the Work Order explicitly."""
    exe = gitleaks_bin()
    with tempfile.TemporaryDirectory(prefix="forgev2-scan-") as empty:
        r = subprocess.run([exe, "git", "--no-banner", "--redact", "--ignore-gitleaks-allow",
                            "--config", os.path.join(LIB, "gitleaks.toml"), "--gitleaks-ignore-path", empty,
                            *mode, empty], capture_output=True, text=True, env=_env(wt_env(d)), cwd=empty)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        return False
    return True


def emit(obj):
    json.dump(obj, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
