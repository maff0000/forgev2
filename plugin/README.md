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

```
/plugin install forgev2 --marketplace maff0000/forgev2
```

or from a shell: `claude plugin marketplace add maff0000/forgev2 && claude plugin install forgev2@forgev2`.
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

Counts live in `<worktree>/.forge/<WO>/ledger.json` and are committed with the
delivery record. They persist across restarts: re-running `forge-start` resumes.

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

- **Identity gate:** exact `OWNER/NAME` match on both fetch and push URLs (only
  canonical github.com forms), top-level checkout, optional known commit, and a
  worktree-history check. Re-checked before every commit and push.
- **Specialist restrictions (guard):** Git read-only; no `.git`/`.forge` access;
  no credential paths or environment dumps; Engineer edits only inside its
  worktree (symlinks resolved); reviewers write only to a scratch directory; no
  PL tools; the guard fails closed.
- **Secrets:** every PL commit is scanned by gitleaks; a finding blocks the commit.
- **Limit of this layer:** subagents run in the PL's own process and Unix
  account, so the guard is a policy layer. It does **not** provide
  operating-system isolation between PL and Engineer, and a fault in the guard
  or in Claude Code would not be contained by the OS.

| Property | Status |
| --- | --- |
| Plugin behaviour (identity gate, loop limits, guard, commit/push gates) | Tested: unit tests and live runs |
| Filesystem boundary between the `forgev2-pl` and `forgev2-agent` accounts | Tested separately: `tests/host/os-boundary.sh` |
| Process isolation between PL and Engineer (Engineer under `forgev2-agent`) | **Not demonstrated.** The plugin does not do this yet |
| Access by external engineers | **Not ready** |

## Tests

```sh
python3 -m unittest discover -s tests -v   # identity, loop limits, guard, commit/push gates
claude plugin validate plugin              # manifest and components
sudo tests/host/os-boundary.sh plugin      # execution host: forgev2-pl / forgev2-agent separation
```
