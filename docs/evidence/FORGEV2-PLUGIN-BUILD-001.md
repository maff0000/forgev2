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

## Not demonstrated live

- A multi-round correction: no reviewer raised a blocking finding in either delivery. The correction path (findings → correction → all three re-review → deliver), no-progress escalation, INCONCLUSIVE escalation and the refused 5th dispatch are exercised through the real guard and ledger in `tests/test_forgev2.py`.
- Orchestrator → PL handoff from Matt's Orchestrator; the PL running as `forgev2-pl`; push and PR creation; real-browser verification (no browser tooling on the host).
