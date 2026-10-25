# ForgeV2 plugin

A Claude Code plugin that turns one approved task into an independently reviewed
Git branch. The session that runs `/forgev2:deliver` is the **Project Lead (PL)**;
it dispatches four specialist subagents and owns all Git operations.

| Component | Purpose |
| --- | --- |
| `skills/deliver` | PL procedure: intake, identity gate, delivery loop, report |
| `agents/engineer` | Implements and tests the change in the WO worktree; no Git writes |
| `agents/auditor`, `tester`, `devsecops` | Fresh, read-only, independent reviews of a committed candidate |
| `bin/forge-start` | Repository identity gate + `forge/<WO>` worktree + ledger |
| `bin/forge-ledger` | Records results, computes the next step, closes the WO |
| `bin/forge-commit` | gitleaks-gated PL commit that sets the review candidate |
| `bin/forge-push` | Re-verifies identity and pushes the WO branch (never forced) |
| `hooks/guard.py` | Counts dispatches, enforces the loop limit and specialist restrictions |

## Install

```sh
claude plugin marketplace add maff0000/forgev2 && claude plugin install forgev2@forgev2
```

Install it in the account that runs the PL (plugins install per user).
See the repository `INSTALL.md` for the full checklist.

## The loop

```
Engineer -> PL tests + forge-commit -> Auditor | Tester | DevSecOps (parallel, fresh)
   all PASS ............................. DELIVER
   blocking findings .................... consolidated correction -> Engineer -> all three re-review
   same finding survives a correction ... ESCALATE (no progress)
   INCONCLUSIVE twice ................... ESCALATE
   any role at 4 executions ............. ESCALATE (5th dispatch is refused by the guard)
```

Counts and results live in a ledger in the PL's private state directory
(`~/.local/state/forgev2`, mode 0700), never in the worktree. A copy is committed
with the delivery record. Re-running `forge-start` resumes; counts never reset.
Every result must match its own dispatch on the exact commit reviewed, and the
ledger refuses any dispatch or commit the current decision does not allow.

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

**Enforced by the PL tools** (`forge-*`, which run as the PL and keep their
state outside the worktree):

- **Identity gate:** exact `OWNER/NAME` on the single fetch URL and single push
  URL of `origin` (canonical github.com forms only; no URL rewriting, no
  credentials in URLs), top-level checkout, known commit and worktree history.
  Re-checked before every commit and push. Pushes go to the verified URL.
- **Ledger:** results bound to dispatches and candidates; the 4-execution limit
  and escalations are binding; a closed Work Order cannot change.
- **What gets pushed:** only `forge/<WO>`, never forced, and only the reviewed
  candidate followed by delivery-record files. Commits made outside
  `forge-commit` are refused.
- **Secrets:** gitleaks (approved build, checked by path, owner and SHA-256)
  scans each commit and the whole branch before push, using ForgeV2's own rules.
  Repository allowlists, `.gitleaksignore` and `gitleaks:allow` are not honoured.
- **Worktree contents are untrusted:** the PL never runs code or Git hooks from
  the worktree, and never trusts the worktree's `.git` pointer.
- **Not as root:** the tools refuse to run as root unless `FORGE_ALLOW_ROOT=1`
  (development hosts only; recorded in the ledger).

**Guard hook (policy, best-effort):** specialists may use only file tools and
the shell; file tools are confined by an allow-list (reads: worktree, scratch,
project checkout; Engineer writes: worktree minus `.git`/`.forge`; reviewer
writes: scratch). Shell commands get pattern checks (Git writes, PL tools,
credential paths, environment dumps) that a specialist trying to evade them
**can** bypass, for example through an interpreter.

**Not enforced in this release:** specialists run as subagents in the PL's own
process and Unix account. A determined specialist can therefore read whatever
the PL account can read (including any Git credential it holds), write anywhere
that account can write, and edit the ledger through the shell. Requirements 1
and 3 ("Engineer changes only authorised files", "PL credentials inaccessible to
the Engineer") are **not met** until specialists run as `forgev2-agent` in
separate processes. Until then: run the PL as a non-root account holding no
credentials beyond the target repository, and do not give external engineers
access.

| Property | Status |
| --- | --- |
| PL-tool gates (identity, ledger, commit, push, secrets) | Tested: `tests/test_forgev2.py` |
| Filesystem boundary between `forgev2-pl` and `forgev2-agent` | Tested separately: `tests/host/os-boundary.sh` |
| Process isolation between PL and specialists | **Not implemented** (planned: separate processes as `forgev2-agent`) |
| Access by external engineers | **Not ready** |

## Tests

```sh
python3 -m unittest discover -s tests -v   # identity, loop limits, guard, commit/push gates
claude plugin validate plugin              # manifest and components
sudo tests/host/os-boundary.sh plugin      # execution host: forgev2-pl / forgev2-agent separation
```
