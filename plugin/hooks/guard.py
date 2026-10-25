#!/usr/bin/env python3
"""ForgeV2 PreToolUse guard.

1. Counts every ForgeV2 specialist dispatch in the Work Order ledger and refuses
   any dispatch the ledger does not permit, including the 5th execution of a role.
   While a Work Order is open, uncounted helpers (other subagent types, resuming a
   subagent) are refused.
2. Constrains ForgeV2 specialists. File tools (Read/Grep/Glob/Edit/Write) are
   confined by an allow-list: reads to the worktree, scratch directory and
   canonical checkout; Engineer writes to its worktree (never .git or .forge);
   reviewer writes to scratch. Other tools are refused.
3. Shell commands get best-effort checks only (Git writes, PL tools, credential
   paths, environment dumps). A specialist that tries can evade shell checks;
   they are not a security boundary.
4. Keeps the PL's own Git writes inside forge-commit / forge-push while a Work
   Order is bound to the session.

This is a policy layer inside one Unix identity, not an OS boundary. It fails
closed: any internal error blocks the tool call.
"""
import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
import forgelib as F  # noqa: E402

CRED = re.compile(r"(\.ssh(/|$|\s|['\"])|\.git-credentials|\.netrc|\.config/gh(/|$|\s)|\.claude/\.credentials"
                  r"|\.claude\.json|/var/lib/forgev2/pl|\bid_(rsa|ed25519|ecdsa)|/proc/[^/\s]+/environ"
                  r"|\.aws/|\.docker/config|GH_TOKEN|GITHUB_TOKEN|ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH)")
ENV_DUMP = re.compile(r"(^|[;&|(]\s*|\s)(printenv\b|env\s*($|[;&|)])|set\s*($|[;&|)])|export\s+-p|declare\s+-x)")
PL_TOOLS = re.compile(r"\bforge-(start|ledger|commit|push)\b")
STATE = re.compile(r"forgev2/(ledgers|sessions)|ledger\.json")
SPECIALIST_TOOLS = {"Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "TodoWrite"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
DISPATCH_TOOLS = {"Agent", "Task"}
GIT_READ = {"status", "diff", "log", "show", "rev-parse", "ls-files", "ls-tree", "cat-file", "blame",
            "grep", "describe", "shortlog", "merge-base", "rev-list", "for-each-ref", "name-rev",
            "show-ref", "whatchanged", "help", "version", "check-ignore", "diff-tree", "diff-files",
            "diff-index", "var"}
BRANCH_FLAGS = {"-a", "-r", "-v", "-vv", "--list", "--show-current", "--all", "--remotes"}
GIT_OPT_ARG = {"-C"}
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "then", "do", "else", "!", "{"}
WRAPPERS = {"xargs", "-exec", "-execdir", "env", "command", "exec", "nohup", "timeout", "nice", "sudo",
            "time", "watch", "parallel", "stdbuf", "ionice", "chronic"}


def deny(reason):
    json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                      "permissionDecisionReason": f"ForgeV2 guard: {reason}"}}, sys.stdout)
    sys.exit(0)


def tokens(cmd):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>")
    lex.whitespace_split = True
    return list(lex)


def git_violation(cmd, depth=0):
    """Return a reason if cmd may write Git state, else None. Recurses into quoted strings."""
    if depth > 3:
        return "command nesting too deep to verify"
    try:
        toks = tokens(cmd)
    except ValueError:
        return "command could not be parsed for Git safety"
    for i, t in enumerate(toks):
        if " " in t and re.search(r"\bgit\b", t) and _under_shell(toks, i):
            r = git_violation(t, depth + 1)
            if r:
                return r
        if os.path.basename(t) != "git" or not _executed(toks, i):
            continue
        j = i + 1
        while j < len(toks) and toks[j].startswith("-"):
            opt = toks[j]
            if opt.startswith(("--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env")) \
                    or opt == "-c":
                return f"git {opt} is not permitted"
            j += 2 if opt in GIT_OPT_ARG else 1
        if j >= len(toks):
            continue
        sub, rest = toks[j], []
        for x in toks[j + 1:]:
            if x in (";", "&&", "||", "|", "&", ")", "(") or x.startswith((";", "&", "|")):
                break
            rest.append(x)
        if any(x.startswith(("--output", "--ext-diff", "--textconv")) for x in rest):
            return f"git {sub} with output/external-program options is not permitted"
        if sub in GIT_READ:
            continue
        if _list_only(sub, rest):
            continue
        return f"git {sub} can change repository state; only the PL runs Git writes"
    return None


SHELLS = {"sh", "bash", "dash", "zsh", "ksh", "eval", "su", "runuser", "ssh", "script"}


def _under_shell(toks, i):
    """True if toks[i] is a string handed to a shell/eval within the same simple command."""
    k = i - 1
    while k >= 0 and toks[k] not in SEPARATORS and not toks[k].startswith((";", "&", "|")):
        if os.path.basename(toks[k]) in SHELLS:
            return True
        k -= 1
    return False


def _executed(toks, i):
    """True if toks[i] runs as a command: command position, after VAR=x, or under a wrapper."""
    k = i - 1
    while k >= 0 and toks[k] not in SEPARATORS and not toks[k].startswith((";", "&", "|")):
        if os.path.basename(toks[k]) in WRAPPERS:
            return True
        k -= 1
    first = k + 1
    while first < i and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[first]):
        first += 1
    return first == i


def _list_only(sub, rest):
    """True only for the read-only forms of otherwise state-changing subcommands."""
    first = rest[0] if rest else None
    if sub == "branch":
        return all(x in BRANCH_FLAGS for x in rest)
    if sub == "tag":
        return all(x in ("-l", "--list") for x in rest)
    if sub == "remote":
        return rest in ([], ["-v"]) or (first in ("get-url", "show") and all(
            not x.startswith("-") or x in ("--push", "--all") for x in rest[1:]))
    if sub == "worktree":
        return first == "list"
    if sub == "stash":
        return first in ("list", "show")
    if sub == "config":
        return first in ("--get", "--get-all", "--list", "-l", "--get-regexp")
    return False


def under(path, root):
    path, root = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([path, root]) == root


def _glob_base(pattern, base):
    """Directory a Glob pattern can reach: its literal prefix, resolved against base."""
    parts = []
    for part in pattern.split("/"):
        if any(c in part for c in "*?[{"):
            break
        parts.append(part)
    return os.path.join(base, "/".join(parts) or ".")


def main():
    ev = json.load(sys.stdin)
    tool, ti = ev.get("tool_name", ""), ev.get("tool_input") or {}
    agent = ev.get("agent_type") or ""
    session = ev.get("session_id", "")
    ledger = F.ledger_for_session(session)
    specialist = agent.startswith(F.PLUGIN + ":")

    if tool in DISPATCH_TOOLS:
        st = ti.get("subagent_type") or ""
        if specialist:
            deny("specialists may not dispatch other agents")
        if st.startswith(F.PLUGIN + ":"):
            role = st.split(":", 1)[1]
            if role not in F.ROLES:
                deny(f"unknown ForgeV2 role {role}")
            if not ledger:
                deny("no Work Order is bound to this session; run forge-start first")
            try:
                with F.locked_ledger(ledger) as d:
                    F.spawn(d, role)
            except F.ForgeError as e:
                deny(str(e))
            return
        if ledger and _open(ledger):
            deny(f"subagent type {st or 'general-purpose'} is not a counted ForgeV2 role; "
                 "dispatch forgev2:engineer/auditor/tester/devsecops")
        return
    if tool == "SendMessage" and ledger and _open(ledger):
        deny("specialists are dispatched fresh each time; resuming a subagent bypasses execution counting")

    if not specialist:
        if ledger:
            _pl_rules(tool, ti, ledger)
        return
    role = agent.split(":", 1)[1]
    if role not in F.ROLES:
        deny(f"unknown ForgeV2 role {role}")
    if tool not in SPECIALIST_TOOLS:
        deny(f"{tool} is not available to ForgeV2 specialists")
    if not ledger:
        deny("no bound Work Order; specialist tools are not permitted")
    with F.locked_ledger(ledger, write=False) as d:
        pass
    cwd = ev.get("cwd") or os.getcwd()
    wt, scratch = d["worktree"], d["scratch"]
    paths = [ti.get(k) for k in ("file_path", "notebook_path") if ti.get(k)]
    if tool in ("Grep", "Glob"):
        paths.append(ti.get("path") or cwd)
    if tool == "Glob":
        pat = ti.get("pattern") or ""
        if ".." in pat.split("/"):
            deny("Glob patterns may not climb out of the search directory")
        paths.append(_glob_base(pat, ti.get("path") or cwd))
    paths = [os.path.join(cwd, p) for p in paths]
    for p in paths:
        if CRED.search(p) or CRED.search(os.path.realpath(p)) or STATE.search(os.path.realpath(p)):
            deny("credential and PL-private paths are not accessible to specialists")
    if tool in WRITE_TOOLS:
        if not paths:
            deny("no file path given")
        p = os.path.realpath(paths[0])
        if role == "engineer":
            if not under(p, wt):
                deny(f"Engineer may edit only inside its assigned worktree {wt}")
            rel = os.path.relpath(p, wt).split(os.sep)
            if ".git" in rel or rel[0] == ".forge":
                deny("Engineer may not modify Git metadata or the Work Order record")
        elif not under(p, scratch):
            deny(f"{role} is read-only; scratch files belong under {scratch}")
        return
    if tool in ("Read", "Grep", "Glob"):
        for p in paths:
            if not any(under(p, r) for r in (wt, scratch, d["root"])):
                deny(f"{role} may read only its worktree, scratch directory and the project checkout")
        return
    if tool == "Bash":
        cmd = ti.get("command", "")
        if CRED.search(cmd) or STATE.search(cmd):
            deny("credential and PL-private paths are not accessible to specialists")
        if ENV_DUMP.search(cmd):
            deny("dumping the environment is not permitted for specialists")
        if PL_TOOLS.search(cmd):
            deny("forge-* commands are PL-only")
        if re.search(r"(^|[\s'\"=/])\.forge(/|\s|$|['\"])", cmd):
            deny("the Work Order record is PL-only")
        if re.search(r"(^|[\s'\"=/])\.git(/|\s|$|['\"])", cmd) or "GIT_DIR" in cmd or "--no-verify" in cmd:
            deny("direct Git metadata access is PL-only")
        r = git_violation(cmd)
        if r:
            deny(r)


def _pl_rules(tool, ti, ledger):
    """While a Work Order is bound, the PL changes Git state and the ledger only through forge-* tools."""
    if tool in WRITE_TOOLS:
        p = ti.get("file_path") or ti.get("notebook_path") or ""
        if STATE.search(os.path.realpath(p)):
            deny("the ledger is changed only through forge-ledger")
    if tool == "Bash":
        cmd = ti.get("command", "")
        if re.search(r"forgev2/(ledgers|sessions)", cmd):
            deny("the ledger is changed only through forge-ledger")
        if "--no-verify" in cmd or re.search(r"\bpush\b.*(--force|\s-f\b|\+refs|\s\+)", cmd):
            deny("hooks are never bypassed and pushes are never forced")
        r = git_violation(cmd)
        if r:
            deny(f"{r}: while a Work Order is bound, commit with forge-commit and push with forge-push")


def _open(ledger):
    with F.locked_ledger(ledger, write=False) as d:
        return not d["outcome"]


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail closed
        print(f"ForgeV2 guard internal error, blocking: {e}", file=sys.stderr)
        sys.exit(2)
