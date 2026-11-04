# ForgeV2 plugin

A Claude Code plugin that turns one approved task into an independently reviewed
Git branch. The session that runs `/forgev2:deliver` is the **Project Lead (PL)**.
It runs as the non-root `forgev2-pl` account, the one Claude login ForgeV2 uses,
and owns all Git operations. Each of the four specialists runs as a fresh, separate
`claude -p` process under that same account, inside Claude Code's sandbox.

| Component | Purpose |
| --- | --- |
| `skills/deliver` | PL procedure: intake, identity gate, delivery loop, report |
| `roles/engineer.md` | Implements and tests the change in the WO worktree; no Git writes |
| `roles/auditor.md`, `tester.md`, `devsecops.md` | Fresh, independent reviews of a committed candidate |
| `bin/forge-start` | Repository identity gate, `forge/<WO>` worktree and scratch directory, ledger |
| `bin/forge-dispatch` | Counts a dispatch, runs the specialist in a sandboxed Claude process, keeps its output |
| `bin/forge-ledger` | Records results, computes the next step, closes the WO |
| `bin/forge-commit` | gitleaks-gated PL commit that sets the review candidate; publishes the record |
| `bin/forge-push` | Re-verifies identity and pushes the WO branch (never forced) |
| `hooks/guard.py` | Keeps the PL session on the procedure (no subagents, Git only via forge tools) |

## Install

The execution host needs one-time setup (bubblewrap and socat, system `claude`,
and one Claude login for `forgev2-pl`); see `INSTALL.md`. Launch each PL with
`--plugin-dir` pointing to the **root-owned, non-writable** ForgeV2 installation;
do not install a second, PL-writable user-scope copy. For the planned Trinity
deployment, the protected installation is `trinity:/srv/forgev2`; installation
there is a separate, post-sign-off operation. Foundry, if locally installed at
`trinity:/srv/foundry`, is likewise read-only during application deliveries.

## The loop

```
Engineer -> PL reads the diff + forge-commit -> Auditor | Tester | DevSecOps (parallel, fresh)
   all PASS ............................. DELIVER
   blocking findings .................... consolidated correction -> Engineer -> all three re-review
   same finding survives a correction ... ESCALATE (no progress)
   INCONCLUSIVE twice ................... ESCALATE
   any role at 4 executions ............. ESCALATE (5th dispatch is refused)
```

Counts and results live in a ledger in the PL's private state directory
(`~/.local/state/forgev2`, mode 0700), never in the worktree. Re-running
`forge-start` resumes; counts never reset. Every result must match its own
dispatch on the exact commit reviewed, a `pass` or `completed` must be what the
specialist itself reported, and the ledger refuses any dispatch or commit the
current decision does not allow. The delivery record committed to the branch
(`.forge/<WO>/`) holds the ledger, the report, every prompt and every
specialist's final message as captured by `forge-dispatch`.

## Work Order format

```
WO: WO-123
REPO: owner/name            # exact GitHub identity; look-alikes are rejected
HOST: dev-hostname          # the verified development/execution machine, not assumed Trinity
ROOT: /abs/path/to/checkout # canonical checkout; the PL never edits it directly
WORKTREES: /abs/path/to/worktrees # explicit sibling of ROOT; no default
BASE: main                  # optional
KNOWN_COMMIT: <sha>         # optional, recommended: proves the right history
PUSH: no                    # optional
BROWSER: yes                # optional: browser behaviour is material

## Change
...
## Acceptance criteria
...
```

## Running it (Orchestrator handoff)

How an Orchestrator starts the PL, passes a Work Order, validates the JSON
result and handles `DELIVERED` / `ESCALATED` / `BLOCKED` is described in
[`ORCHESTRATOR.md`](ORCHESTRATOR.md).

**Host/path gate:** `forge-start` checks the current machine against `HOST`
before changing Git; ROOT and WORKTREES must be explicit canonical absolute
siblings in the project's declared directory. No delivery worktree can overlap
`/srv/forgev2`, `/srv/foundry`, or the running plugin source. These tools are
local-filesystem tools: an Orchestrator on Trinity cannot use them to develop
on a remote host merely by naming its IP. The approved execution/transport path
to a remote host must exist and be tested first; otherwise return BLOCKED.

## Security model

**One account, one login, specialists sandboxed.** The PL and every specialist run
as `forgev2-pl`, using its single Claude login; no login is copied and no
credential is passed to a specialist. Each specialist is a fresh `claude -p`
process with a fresh, empty HOME, started by `forge-dispatch` with fixed settings:

- Safe mode: no settings files, hooks, MCP servers, skills or CLAUDE.md are loaded.
- Commands run in Claude Code's sandbox (bubblewrap, seccomp and a network proxy).
  If the sandbox cannot start, the run stops; nothing runs unsandboxed.
- File tools (Read/Grep/Glob/Edit/Write) are limited by permission rules on the
  same paths, enforced by Claude Code. The specialist starts in the scratch
  directory, not in the repository.

| Specialist access (commands and file tools) | Engineer | Auditor, Tester, DevSecOps |
| --- | --- | --- |
| Worktree | read, write (not `.git` or `.forge`) | read only |
| Scratch directory | read, write | read, write |
| Worktree and common Git directories (refs, objects, hooks, config) | read only | read only |
| PL home: Claude login, Git credentials, ledger, records, Claude config | no access | no access |
| Other processes (including the PL's environment and memory) | not visible (own `/proc`) | not visible |
| Network from commands; Unix sockets; new user namespaces | blocked | blocked |
| `/tmp`, `/var/tmp`, canonical checkout, rest of the system | read only | read only |

`tests/host/sandbox-boundary.sh` checks each row with real specialist runs, for the
Engineer, Auditor and Tester: commands through a probe script that records only
reachable/blocked, file tools through attempted reads and writes whose effects
are checked on disk. It also checks that a run stops when bubblewrap is unavailable.

**Weaker than separate Unix accounts.** Everything above is enforced by Claude
Code (its sandbox runtime and its permission checks) and by bubblewrap and the
kernel's namespaces, all inside the account that holds the PL's Claude login and
Git credentials. The specialist's own Claude process runs unsandboxed in that
account and holds the login token in memory; only the tools the model uses are
confined. A defect in Claude Code's sandbox or permission checks, in bubblewrap,
or a kernel namespace escape would expose the PL's credentials to a specialist.
Separate Unix accounts would not depend on Claude Code for that boundary, but
need a second login. Sandboxed commands also see two values the sandbox itself
sets: its proxy password (the proxy allows no hosts) and its session-inbox token
(unusable: Unix sockets are blocked). Both are tested.

**Enforced by the PL tools** (`forge-*`, running as the PL):

- **Identity gate:** exact `OWNER/NAME` on the single fetch URL and single push
  URL of `origin` (canonical github.com forms only; no URL rewriting, no
  credentials in URLs), top-level checkout, known commit and worktree history.
  Re-checked before every dispatch, commit and push. Pushes go to the verified URL.
- **Ledger:** results bound to dispatches and candidates; a `pass`/`completed`
  only if the specialist reported it; the 4-execution limit and escalations are
  binding; a closed Work Order cannot change.
- **What gets pushed:** only `forge/<WO>`, never forced, and only the reviewed
  candidate followed by delivery-record files. Commits made outside
  `forge-commit` are refused.
- **Secrets:** gitleaks (approved build, checked by path, owner and SHA-256)
  scans each commit and the whole branch before push, using ForgeV2's own rules.
  Repository allowlists, `.gitleaksignore` and `gitleaks:allow` are not honoured.
- **Worktree contents are untrusted:** the PL never runs code or Git hooks from
  the worktree, never trusts its `.git` pointer, and writes the delivery record
  into it without following links planted there.
- **Projects outside the PL home:** a project or worktree inside the PL's home
  or state directory is refused (specialists could not read it anyway).
- **Not as root:** the tools refuse to run as root unless `FORGE_ALLOW_ROOT=1`
  (development hosts only; recorded in the ledger).

**Guard hook (policy on the PL's own tool calls):** while a Work Order is open
the PL cannot start in-process subagents or run `claude`/`bwrap` directly, makes
Git writes only through `forge-commit`/`forge-push`, cannot edit the ledger, and
does not write into the shared worktree or follow links planted in it. Its shell
checks are pattern-based; it is not a security boundary.

**Not enforced:**

- The specialist's Claude process itself reaches Anthropic's API; only its
  commands are offline. It can read the worktree, the project checkout and
  anything world-readable on the host, and it reports text back to the PL.
- All specialists share the scratch directory.
- The PL is a Claude session reading text written by specialists (diffs,
  reports). Its tools bound what it can do, but prompt injection into the PL is
  not prevented.
- No browser on this host: web changes come back `ESCALATED` (Tester
  `INCONCLUSIVE`), never claimed as browser-verified.

| Property | Status |
| --- | --- |
| PL-tool gates (identity, ledger, dispatch, commit, push, secrets) | Tested: `tests/test_forgev2.py` |
| Specialist sandbox (commands, file tools, fail-closed start) | Tested on the host: `tests/host/sandbox-boundary.sh` |
| Delivery with sandboxed specialists under `forgev2-pl` | Live runs: `docs/evidence/FORGEV2-PLUGIN-BUILD-001.md` |
| Access by external engineers | **Not assessed** |

## Tests

```sh
python3 -m unittest discover -s tests -v   # identity, loop limits, dispatch, sandbox settings, guard, commit/push
claude plugin validate plugin              # manifest and components
sudo tests/host/sandbox-boundary.sh plugin # execution host: real sandboxed specialists (needs the PL login)
```
