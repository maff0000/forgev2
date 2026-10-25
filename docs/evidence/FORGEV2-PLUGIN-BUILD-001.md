# FORGEV2-PLUGIN-BUILD-001 — plugin build and test evidence

**Date:** 2026-10-25 (UTC) · **Runtime:** Claude Code 2.1.310 · **Base:** `66d3b88` + INSTALL.md candidate `7ef1e06`
**Status:** candidate for independent audit and testing. Not accepted; not deployed.

## Automated checks

| Check | Result |
| --- | --- |
| `claude plugin validate plugin` and `claude plugin validate .` (marketplace) | Passed, no warnings |
| `claude --plugin-dir plugin plugin details forgev2` | 1 skill (`deliver`), 4 agents, 1 PreToolUse hook; ~390 always-on tokens |
| `python3 -m unittest discover -s tests` | 34 tests OK |
| Non-vacuity: loop limit raised to 5 | 2 limit tests failed (detected) |
| Non-vacuity: guard Git check disabled | 2 guard tests failed (detected) |
| `tests/host/os-boundary.sh` as root with `forgev2-pl`/`forgev2-agent` | 19/19 PASS |

## Live headless deliveries (disposable fixture `forgev2-fixture/calc`, `PUSH: no`)

Invocation: `claude -p --plugin-dir plugin --add-dir <worktrees> --allowedTools "Bash Read Write Edit Glob Grep Agent" "/forgev2:deliver <WO>"`, run as root on the development host.

| Work Order | Result | Notes |
| --- | --- | --- |
| WO-CALC-001 `divide()` | DELIVERED, 1 round, executions 1/1/1/1 | Guard counted every dispatch; reviewers ran in parallel on the committed candidate; 9 tests OK; canonical checkout untouched. DevSecOps reported (advisory) that the guard blocked `gitleaks git <path>` — a guard false positive, fixed and covered by tests before the next run. |
| WO-WRONG-REPO (expects `forgev2-fixture/calc-prod`) | BLOCKED at identity gate | No branch, worktree or ledger created; no workaround attempted. |
| WO-CALC-002 v1 (`evaluate()`, criterion 4 self-contradictory) | BLOCKED at intake | PL identified the contradiction and proposed two rewrites; nothing created. |
| WO-CALC-002 v2 (criterion corrected) | DELIVERED, 1 round, executions 1/1/1/1 | 18 tests OK; DevSecOps ran gitleaks (no leaks) and DoS probes; two advisory findings recorded and verified by the PL. |
| WO-WRONG-REPO re-run after the output-contract fix (`--output-format json`) | BLOCKED at identity gate | `result` now starts with `# WO-WRONG-REPO - BLOCKED`. Before the fix, this case started with prose. |

## Output contract check

With `--output-format json`, stdout is one JSON object, so the status is not the first line of stdout. The contract is in `plugin/README.md` ("Output contract"): parse the JSON, require `type=result`, `subtype=success`, `is_error=false`, and a first `result` line of exactly `# <WO> - <STATUS>`, and cross-check the ledger `outcome` where a ledger exists. Checked against the recorded runs:

- **WO-CALC-001 and WO-CALC-002:** conform, and the ledger `outcome` is `DELIVERED`.
- **First WO-WRONG-REPO run:** did **not** conform, because the result began with prose. A validating Orchestrator would have treated it as BLOCKED (malformed), which is safe, but it was a defect. The skill now requires the heading for every outcome. The re-run conforms.

## Security scope (precise)

| Property | Status |
| --- | --- |
| Plugin behaviour: identity gate, loop limits, guard, commit/push gates | Tested (unit tests and the live runs above) |
| Filesystem boundary between `forgev2-pl` and `forgev2-agent` | Tested separately (`tests/host/os-boundary.sh`, 19/19) |
| Process isolation between PL and Engineer | **Not demonstrated.** Subagents run in the PL's own process and Unix account, so the guard is a policy layer and does not provide OS isolation |
| Access by external engineers | **Not ready** |

`total_cost_usd`, about $0.90 per delivery and $0.13 for an identity-gate block, is Claude Code's modelled API-equivalent figure. It is a baseline for scaling, not necessarily a separate charge on Matt's subscription.

## Not demonstrated live

- A multi-round correction: no reviewer raised a blocking finding in either delivery. The correction path (findings → correction → all three re-review → deliver), no-progress escalation, INCONCLUSIVE escalation and the refused 5th dispatch are exercised through the real guard and ledger in `tests/test_forgev2.py`.
- Orchestrator → PL handoff from Matt's Orchestrator; the PL running as `forgev2-pl`; push and PR creation; real-browser verification (no browser tooling on the host).
