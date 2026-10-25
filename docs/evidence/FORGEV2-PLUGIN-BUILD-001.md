# FORGEV2-PLUGIN-BUILD-001 — plugin build and test evidence

**Date:** 2026-10-25 (UTC) · **Runtime:** Claude Code 2.1.310 · **Base:** `66d3b88` + INSTALL.md candidate `7ef1e06`
**Status:** v0.2 candidate (correction A). Not accepted; not deployed. Process isolation (B) not yet implemented.

## Correction A (v0.2): review findings and resolution

PR #4 (v0.1) was reviewed by an external audit (4 findings) and by three fresh Claude
sessions with no build context (security, correctness, claims; all FAIL). Every
finding below was reproduced against v0.1 before it was fixed. Root cause: the ledger
lived in the Engineer-writable worktree and the shell guard was relied on for
enforcement it cannot provide.

| Finding (source) | Resolution in v0.2 | Test |
| --- | --- | --- |
| PASS recorded without a fresh review (audit 1; correctness C1) | Each result consumes exactly one dispatch made on the current candidate | `test_pass_cannot_be_recorded_without_fresh_review`, `test_result_needs_its_own_dispatch`, `test_blocking_result_cannot_be_overwritten` |
| Result stamped with the wrong candidate (C2) | Candidate stamped at dispatch; no commit while a dispatch is pending | `test_candidate_cannot_change_while_review_pending` |
| Unreviewed code pushed (audit 2; C5; security S5) | `close DELIVERED` requires HEAD = candidate; `forge-push` requires candidate + record files only, pushes only `forge/<WO>` to the verified URL | `test_push_refuses_unreviewed_commit_after_delivery`, `test_close_delivered_refuses_head_beyond_candidate`, `test_push_refuses_non_forge_branch` |
| Ledger editable by specialists; limit raisable; planted ledger trusted (S1, S2, C3, C4) | Ledger in the PL's private state directory (0700), limit from code, base containing `.forge/<WO>` refused | `test_ledger_and_scratch_outside_worktree_and_home`, `test_limit_in_ledger_is_ignored`, `test_rejects_base_with_records_for_same_wo` |
| Escalation advisory only; closed WO mutable; inconclusive rule wrong; no COMMIT step (C8–C11; claims C6) | Dispatch/commit only when the decision allows; closed WO immutable; INCONCLUSIVE twice per reviewer; `COMMIT` decision; a no-change Engineer round escalates | `test_repeated_finding_escalates_and_stops_dispatch`, `test_closed_work_order_is_immutable`, `test_no_result_accepted_after_close`, `test_inconclusive_*`, `test_correction_without_change_escalates` |
| Crash-unsafe ledger writes (C7) | Lock file + temp file + fsync + atomic replace; corrupt ledger gives a clean error | `test_corrupt_ledger_fails_cleanly` |
| Extra push URL / URL rewriting passed the identity gate (S3) | Exactly one fetch and one push URL; any `url.*` rewriting refused; credentials in URLs rejected | `test_rejects_additional_push_url`, `test_rejects_url_rewriting`, `RemoteParsing` |
| gitleaks bypasses: allow comment, repo config, `.gitleaksignore`, staged-only scan, fake binary on PATH (S6, C6) | Approved binary by path/owner/SHA-256; ForgeV2's own config; empty scan source with Git directory passed explicitly; whole-branch scan before push; out-of-band commits refused | `test_repository_cannot_suppress_the_secret_scan`, `test_out_of_band_commit_blocks_commit`, `test_push_scans_whole_branch_history`, `test_missing_or_unapproved_gitleaks_refused` |
| Worktree hooks / `.git` pointer could run code as the PL (found during A) | PL Git calls name the recorded Git directory and the common-dir hooks path; PL never runs worktree code | `test_worktree_hooks_not_run_by_pl`, `test_tampered_worktree_git_pointer_is_ignored` |
| Runs as root silently (S9, claims C7) | `forge-*` refuse euid 0 unless `FORGE_ALLOW_ROOT=1` (recorded in the ledger) | `test_refuses_root_without_override` |
| Grep/Glob reach credentials; other tools unguarded; interpreter path (S8, H1, H2) | File tools confined by allow-list; specialists limited to a fixed tool set; hook matcher `*`; `/usr/bin/python3` | `test_file_tools_confined_to_allowed_directories`, `test_specialists_limited_to_known_tools` |
| Shell bypasses: Git via interpreters, writes anywhere, credential reads (audit 3; S4, S7, S8) | **Not fixable by pattern checks.** Some patterns tightened (`remote -v`, `-c`, `--output`); README now states the shell is unconfined and requirements 1 and 3 are unmet until B | `test_engineer_git_writes_denied` (patterns only) |
| Scratch under the PL home blocked reviewers as `forgev2-pl` (claims C4) | Scratch moved to `<worktrees>/.forge-scratch/<WO>` | `test_ledger_and_scratch_outside_worktree_and_home` |
| Docs overclaimed; install command; "no warnings" (S11, claims C1–C3, C8–C10, S3) | README security model rewritten (enforced / best-effort / not enforced); CLI install form; see validation note below | — |
| 25/34 without gitleaks (audit 4) | Environment, not a defect: the suite now states the prerequisite explicitly | `Prerequisites` |

## v0.2 checks

| Check | Result |
| --- | --- |
| `python3 -m unittest discover -s tests` | 65 tests OK (with gitleaks 8.30.1 installed) |
| Non-vacuity: 13 fixes individually disabled | Every sabotage made at least one test fail (first pass found one insensitive test, which was strengthened) |
| `tests/host/os-boundary.sh` | 19/19 PASS |
| `claude plugin validate plugin` | Passed, with one listing warning (`ICON_MISSING`; cosmetic) |

### Live headless runs, v0.2 (fixture `forgev2-fixture/calc`, `PUSH: no`, PL as root with `FORGE_ALLOW_ROOT=1`)

| Work Order | Result | Notes |
| --- | --- | --- |
| WO-CALC-003 `percent()` | DELIVERED, 1 round, 1/1/1/1 | Ledger: each result bound to its dispatch; PL used only `forge-*` for Git and ran no project code; records commit contains only `.forge/WO-CALC-003/` files |
| WO-CALC-004 `parse_duration()` (edge-case heavy) | DELIVERED, 1 round, 1/1/1/1 | As above |
| WO-CALC-005 cron `next_fire()` (error-prone) | DELIVERED, 1 round, 1/1/1/1 | Tester cross-checked 1,500 random expressions against a brute-force reference |
| WO-CALC-006, **fault injection**: Engineer told to omit criterion 2 in round 1 only | DELIVERED, **2 rounds, 2/2/2/2** | All three reviewers independently caught the omission (blocking); correction became a new candidate; all three re-reviewed; delivered |
| WO-CALC-007, **fault injection**: omission in every round | ESCALATED by the PL | Exposed a gap: a correction producing no change left the ledger at COMMIT. Fixed: a no-change round is now a binding no-progress escalation (unit-tested) |
| WO-CALC-008, same injection (after the fix) | No final status | PL declined to continue the sabotage and paused to ask; its reply broke the output contract (an Orchestrator would treat it as BLOCKED). Skill now says conflicting instructions are BLOCKED, never a question |
| WO-CALC-009, explicit authorised injection | BLOCKED (binding) | Round-2 Engineer reported `failed`; ledger stopped further dispatch |

Fault-injection runs used an extra `--append-system-prompt` on the test command only; nothing in the plugin produces them. They test the loop's mechanics and reviewer detection of a planted omission, not reviewer sensitivity to subtle real defects. Modelled cost: $0.86–$1.60 per delivery.

## v0.1 record (superseded)

### Automated checks (v0.1)

| Check | Result |
| --- | --- |
| `claude plugin validate plugin` and `claude plugin validate .` (marketplace) | Passed (the plugin-directory `ICON_MISSING` listing warning was not reported at the time) |
| `claude --plugin-dir plugin plugin details forgev2` | 1 skill (`deliver`), 4 agents, 1 PreToolUse hook; ~390 always-on tokens |
| `python3 -m unittest discover -s tests` | 34 tests OK |
| Non-vacuity: loop limit raised to 5 | 2 limit tests failed (detected) |
| Non-vacuity: guard Git check disabled | 2 guard tests failed (detected) |
| `tests/host/os-boundary.sh` as root with `forgev2-pl`/`forgev2-agent` | 19/19 PASS |

### Live headless deliveries (disposable fixture `forgev2-fixture/calc`, `PUSH: no`)

Invocation: `claude -p --plugin-dir plugin --add-dir <worktrees> --allowedTools "Bash Read Write Edit Glob Grep Agent" "/forgev2:deliver <WO>"`, run as root on the development host.

| Work Order | Result | Notes |
| --- | --- | --- |
| WO-CALC-001 `divide()` | DELIVERED, 1 round, executions 1/1/1/1 | Guard counted every dispatch; reviewers ran in parallel on the committed candidate; 9 tests OK; canonical checkout untouched. DevSecOps reported (advisory) that the guard blocked `gitleaks git <path>` — a guard false positive, fixed and covered by tests before the next run. |
| WO-WRONG-REPO (expects `forgev2-fixture/calc-prod`) | BLOCKED at identity gate | No branch, worktree or ledger created; no workaround attempted. |
| WO-CALC-002 v1 (`evaluate()`, criterion 4 self-contradictory) | BLOCKED at intake | PL identified the contradiction and proposed two rewrites; nothing created. |
| WO-CALC-002 v2 (criterion corrected) | DELIVERED, 1 round, executions 1/1/1/1 | 18 tests OK; DevSecOps ran gitleaks (no leaks) and DoS probes; two advisory findings recorded and verified by the PL. |
| WO-WRONG-REPO re-run after the output-contract fix (`--output-format json`) | BLOCKED at identity gate | `result` now starts with `# WO-WRONG-REPO - BLOCKED`. Before the fix, this case started with prose. |

### Output contract check

With `--output-format json`, stdout is one JSON object, so the status is not the first line of stdout. The contract is in `plugin/ORCHESTRATOR.md` (section 3): parse the JSON, require `type=result`, `subtype=success`, `is_error=false`, and a first `result` line of exactly `# <WO> - <STATUS>`, and cross-check the ledger `outcome` where a ledger exists. Checked against the recorded runs:

- **WO-CALC-001 and WO-CALC-002:** conform, and the ledger `outcome` is `DELIVERED`.
- **First WO-WRONG-REPO run:** did **not** conform, because the result began with prose. A validating Orchestrator would have treated it as BLOCKED (malformed), which is safe, but it was a defect. The skill now requires the heading for every outcome. The re-run conforms.

### Security scope (precise)

| Property | Status |
| --- | --- |
| Plugin behaviour: identity gate, loop limits, guard, commit/push gates | Tested (unit tests and the live runs above) |
| Filesystem boundary between `forgev2-pl` and `forgev2-agent` | Tested separately (`tests/host/os-boundary.sh`, 19/19) |
| Process isolation between PL and Engineer | **Not demonstrated.** Subagents run in the PL's own process and Unix account, so the guard is a policy layer and does not provide OS isolation |
| Access by external engineers | **Not ready** |

`total_cost_usd`, about $0.90 per delivery and $0.13 for an identity-gate block, is Claude Code's modelled API-equivalent figure. It is a baseline for scaling, not necessarily a separate charge on Matt's subscription.

### Not demonstrated live

- A multi-round correction: no reviewer raised a blocking finding in either delivery. The correction path (findings → correction → all three re-review → deliver), no-progress escalation, INCONCLUSIVE escalation and the refused 5th dispatch are exercised through the real guard and ledger in `tests/test_forgev2.py`.
- Orchestrator → PL handoff from Matt's Orchestrator; the PL running as `forgev2-pl`; push and PR creation; real-browser verification (no browser tooling on the host).

## Not demonstrated (v0.2)

- **Process isolation (B):** specialists still run inside the PL's process and Unix account. Requirements 1 and 3 are not met against a specialist that tries to evade the shell checks.
- Orchestrator → PL handoff from Matt's Orchestrator; the PL running as `forgev2-pl`; push and PR creation through `forge-push`; real-browser verification.
- A live no-change correction reaching the ledger's no-progress rule (unit-tested; live runs ended via the PL and via a binding BLOCKED instead).
