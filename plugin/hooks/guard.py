#!/usr/bin/env python3
"""ForgeV2 PreToolUse guard for the Project Lead session.

Specialists do not run inside the PL's Claude process: forge-dispatch starts each
one as a separate, sandboxed Claude process. While a Work Order is bound to the
session, this guard keeps the PL itself on the procedure:

1. No in-process subagents (Agent/Task/SendMessage) while the Work Order is
   open, and no direct `claude` runs: engineering and review run only through
   forge-dispatch, where every execution is counted and sandboxed.
2. Git writes only through forge-commit / forge-push; never --no-verify or a
   forced push.
3. The ledger and the raw dispatch outputs change only through forge-* tools.
4. The worktree and scratch directory are the specialists': the PL does not
   write there, and does not follow a link planted there to a path outside.

This is a policy layer on the PL's own tool calls, not an OS boundary. It fails
closed: any internal error blocks the tool call.
"""
import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "lib"))
import forgelib as F  # noqa: E402

STATE = re.compile(r"forgev2/(ledgers|sessions)")
FILE_TOOLS = {"Read", "Grep", "Glob", "Edit", "Write", "MultiEdit", "NotebookEdit"}
WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
DISPATCH_TOOLS = {"Agent", "Task", "SendMessage"}
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
        return f"git {sub} can change repository state; Git writes go through forge-commit"
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


def lexically_under(path, root):
    path, root = os.path.normpath(path), os.path.normpath(root)
    return os.path.commonpath([path, root]) == root


def main():
    ev = json.load(sys.stdin)
    tool, ti = ev.get("tool_name", ""), ev.get("tool_input") or {}
    ledger = F.ledger_for_session(ev.get("session_id", ""))
    if not ledger:
        return
    with F.locked_ledger(ledger, write=False) as d:
        pass
    if tool in DISPATCH_TOOLS:
        if not d["outcome"]:
            deny("while a Work Order is open, specialists run only through forge-dispatch (separate, "
                 "counted and isolated processes); in-process subagents are not permitted")
        return
    cwd = ev.get("cwd") or os.getcwd()
    private = [os.path.join(F.state_dir(), x) for x in ("ledgers", "sessions")]
    if tool in FILE_TOOLS:
        _file_rules(tool, ti, d, cwd, private)
    if tool == "Bash":
        _bash_rules(ti.get("command", ""), private)


def _file_rules(tool, ti, d, cwd, private):
    paths = [ti.get(k) for k in ("file_path", "notebook_path", "path") if ti.get(k)]
    for p in (os.path.join(cwd, x) for x in paths):
        if tool in WRITE_TOOLS and any(under(p, q) for q in F.PROTECTED_INSTALLS):
            deny("Foundry and ForgeV2 installations are immutable during application Work Orders")
        if tool in WRITE_TOOLS and (STATE.search(os.path.realpath(p)) or any(under(p, x) for x in private)):
            deny("the ledger and dispatch outputs are changed only through forge-* tools")
        for area in (d["worktree"], d["scratch"]):
            if lexically_under(p, area) or under(p, area):
                if tool in WRITE_TOOLS:
                    deny(f"{area} belongs to the specialists: the Engineer changes the worktree "
                         "(dispatch it with forge-dispatch); PL records go in the records directory")
                if not under(p, area):
                    deny(f"{p} is a link planted in the shared area pointing outside it; not followed")


def _bash_rules(cmd, private):
    if STATE.search(cmd) or any(x in cmd for x in private):
        deny("the ledger is changed only through forge-ledger")
    if re.search(r"(^|[\s;&|(/])(claude|sudo|bwrap)(\s|$)", cmd):
        deny("specialists are started only by forge-dispatch, inside the sandbox")
    if "--no-verify" in cmd or re.search(r"\bpush\b.*(--force|\s-f\b|\+refs|\s\+)", cmd):
        deny("hooks are never bypassed and pushes are never forced")
    r = git_violation(cmd)
    if r:
        deny(f"{r}: while a Work Order is bound, commit with forge-commit and push with forge-push")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail closed
        print(f"ForgeV2 guard internal error, blocking: {e}", file=sys.stderr)
        sys.exit(2)
