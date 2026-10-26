# ForgeV2 plugin

A Claude Code plugin that turns one approved task into an independently reviewed
Git branch. The session that runs `/forgev2:deliver` is the **Project Lead (PL)**.
It runs as the `forgev2-pl` account and owns all Git operations. Each of the four
specialists runs as a separate `claude -p` process under the `forgev2-agent`
account, started through a small root-owned launcher.

| Component | Purpose |
| --- | --- |
| `skills/deliver` | PL procedure: intake, identity gate, delivery loop, report |
| `roles/engineer.md` | Implements and tests the change in the WO worktree; no Git writes |
| `roles/auditor.md`, `tester.md`, `devsecops.md` | Fresh, independent reviews of a committed candidate |
| `bin/forge-start` | Repository identity gate, `forge/<WO>` worktree shared with the agent account, ledger |
| `bin/forge-dispatch` | Counts a dispatch, runs the specialist as `forgev2-agent`, keeps its output |
| `bin/forge-ledger` | Records results, computes the next step, closes the WO |
| `bin/forge-commit` | gitleaks-gated PL commit that sets the review candidate; publishes the record |
| `bin/forge-push` | Re-verifies identity and pushes the WO branch (never forced) |
| `libexec/agent-run` | The launcher, installed root-owned by the operator with its one-line sudo rule |
| `hooks/guard.py` | Keeps the PL session on the procedure (no subagents, Git only via forge tools) |

## Install

The execution host needs a one-time set-up by root (the `forgev2-work` group,
the launcher and its sudo rule, and a Claude login for each account); see the
repository `INSTALL.md`. Then, as `forgev2-pl`:

```sh
claude plugin marketplace add maff0000/forgev2 && claude plugin install forgev2@forgev2
```

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
ROOT: /abs/path/to/checkout # canonical checkout; the PL never edits it directly
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

## Security model

**Two accounts, enforced by the operating system.** The PL runs as `forgev2-pl`;
specialists run as `forgev2-agent`. The only link between them is the sudo rule
`forgev2-pl ALL=(forgev2-agent) NOPASSWD: /usr/local/libexec/forgev2/agent-run`:
the PL can run the launcher, only as the agent account, and nothing else. The
launcher accepts a role, a worktree created by `forge-start` and a prompt on
stdin. It builds the `claude` command line and environment itself, and starts
Claude in safe mode with no settings, hooks, MCP servers, skills or CLAUDE.md
files, in a fresh empty HOME for every run.

| The agent account (all specialists) | can | cannot |
| --- | --- | --- |
| WO worktree files, scratch directory | read, write | |
| Worktree Git metadata, refs, objects, hooks, config | read | write (so it cannot commit, branch or push) |
| `.forge/` delivery record in the worktree | read | write |
| Canonical checkout (`ROOT`) | read | write |
| PL home: Claude login, Git credentials, ledger, records | | read or list |
| PL process environments | | read |
| sudo | | run anything |

`tests/host/os-boundary.sh` checks each row on the real accounts, together with
the sudo rule and the launcher's refusals.

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
  into it without following links the agent account could plant there.
- **Not as root:** the tools refuse to run as root unless `FORGE_ALLOW_ROOT=1`
  (development hosts only; recorded in the ledger).

**Guard hook (policy on the PL's own tool calls):** while a Work Order is open
the PL cannot start in-process subagents or call sudo/the launcher directly, makes
Git writes only through `forge-commit`/`forge-push`, cannot edit the ledger, and
does not write into the shared worktree or follow links planted in it. Its shell
checks are pattern-based; it is not a security boundary.

**Not enforced:**

- All four specialists share the one agent account. The operating system does
  not stop a reviewer from editing the worktree, or the Engineer from reading
  scratch files. A change in the worktree is caught instead: review requires a
  clean worktree equal to the candidate, a review that leaves it changed is void,
  and delivery requires the worktree to be exactly the reviewed commit.
- The agent account has network access and its own Claude login. A misbehaving
  specialist could send out what it can read: the worktree, the project
  checkout, and anything world-readable on the host.
- The PL is a Claude session reading text written by the agent account (diffs,
  specialist reports). Its tools bound what it can do, but prompt injection into
  the PL is not prevented.
- No browser on this host: web changes come back `ESCALATED` (Tester
  `INCONCLUSIVE`), never claimed as browser-verified.

| Property | Status |
| --- | --- |
| PL-tool gates (identity, ledger, dispatch, commit, push, secrets) | Tested: `tests/test_forgev2.py` |
| Separation of `forgev2-pl` and `forgev2-agent`, sudo rule, launcher | Tested on the host: `tests/host/os-boundary.sh` |
| Delivery with specialists as `forgev2-agent` | Live runs: `docs/evidence/FORGEV2-PLUGIN-BUILD-001.md` |
| Access by external engineers | **Not assessed** |

## Tests

```sh
python3 -m unittest discover -s tests -v   # identity, loop limits, dispatch, launcher, guard, commit/push
claude plugin validate plugin              # manifest and components
sudo tests/host/os-boundary.sh plugin      # execution host: accounts, sudo rule, launcher
```
