# ENGINE-SANDBOX-TEST-001 — Canonical Sandbox Boundary Test Recovery

| Field | Value |
|---|---|
| Work Order | ENGINE-SANDBOX-TEST-001. ForgeV2 engine development (FND-044); not an application WO. |
| Artifact | `work-orders/ENGINE-SANDBOX-TEST-001.md` in `maff0000/forgev2`. This file is version v1.0 for review. The immutable version is the commit that adds it, recorded on the Issue. No SHA in this file refers to its own commit. |
| Status | **Submitted for CGPT exact-version approval.** This file grants no implementation authority until approval is recorded on the Issue. |
| GitHub Issue | https://github.com/maff0000/forgev2/issues/5. Filled in before the artifact commit; see request W1. |
| Parent PBIs | FV2-002, FV2-004 (backlog approved at `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`); supports FV2-D021 |
| Governing FOUNDRY | `5f5e4a51f8909d134c46ef8b43a9bd20d086fcc0` |
| Original base | `63b6b8ab6c6d3c12d1ef3f0aeabe2ca22fbefb82` (`main`, merge of PR #4) |
| Engineering start commit | The CGPT-approved artifact commit, which must be a direct child of the original base that adds only this file |
| Prepared by | Rogue (Orchestrator), 2026-11-06. The preparer cannot approve this WO or dispatch it. |
| Architect rulings incorporated | CGPT review, 2026-11-06, relayed by Matt: `/tmp` fixtures allowed; supervised engine development on the execution host; separate checkout `/srv/src/forgev2/main`; DevSecOps included; at most three recorded acceptance runs; restricted evidence path; plugin stays 0.3.0; stronger probe corroboration |

## 1. Governing authority and revision compatibility

**FOUNDRY sources applied** (at `5f5e4a5`):
- `standards/work-order-contract.md` (content and entry gates 1 to 11)
- `standards/secure-engineering.md`
- `standards/project-scaffolding.md` (Execution rule)
- `GOVERNANCE.md`
- `delivery/rogue-handoff.md`
- `DECISIONS.md` FND-020, FND-035, FND-036, FND-041 to FND-045

**ForgeV2 records at the original base:**
- `DECISIONS.md` FV2-D004, D006, D008, D010, D013, D014, D018 to D023
- `security/ACCESS_CONTROL.md`
- `plugin/README.md`
- `docs/evidence/FORGEV2-PLUGIN-BUILD-001.md`

**Compatibility with `aee86185aac6aa0d2ab7a243138c423292af191a`** (the revision the ForgeV2 README cites). The only intervening commit is `f5c635a` (4 files, +15/−5). It adds FND-045 and makes these changes:
- requires an explicit, verified `host:/path`, canonical checkout and worktree parent;
- makes engine and FOUNDRY installs immutable during application WOs;
- forbids inferring locations from the working directory, a previous assignment, the controller host or a temporary directory;
- requires a demonstrated remote route.

These are all tightenings; nothing is removed. Records approved under `aee8618` remain valid. This WO satisfies the new wording in section 3. The Architect has ruled that explicitly declared, isolated `/tmp` test fixtures are acceptable.

## 2. Intended outcome

Restore `tests/host/sandbox-boundary.sh` as the canonical, executable host acceptance test for the pinned engine. It must cover the **Engineer, Auditor, Tester and DevSecOps** specialists. Every check must end as **PASS, FAIL or NOT RUN**. A probe result counts only when its execution is corroborated by evidence that does not come from model output. **No runtime engine behaviour changes.** The plugin version stays **0.3.0** unless a runtime change proves necessary; such a change is out of scope here and would be BLOCKED.

## 3. Repository, workspace and execution boundary

| Item | Value | Entry verification |
|---|---|---|
| Repository | `maff0000/forgev2` | Fetch/push URLs exactly `github.com/maff0000/forgev2` |
| WO branch | `work/engine-sandbox-test-001`. Its first commit is the artifact commit, a child of the original base. | Remote `main` still equals the original base, or the Architect re-approves. The branch contains no commits other than the approved artifact commit. `feat/remote-execution` has not merged. |
| Engine-development checkout | `<execution-host>:/srv/src/forgev2/main` (canonical) and `/srv/src/forgev2/worktrees/engine-sandbox-test-001` (WO worktree), using the FV2-D014 layout | Provisioned before dispatch (prerequisite P2). Clean; `origin` identity verified; worktree HEAD equals the approved artifact commit. |
| Pinned engine installation | `/srv/forgev2`, root-owned, HEAD at the original base | **Never written, fetched into, patched or used as a worktree.** The baseline listing of `.git` entries is recorded before dispatch. It includes the `FETCH_HEAD` deviation (section 15). |
| Execution host | The approved Debian 13 execution host. Its identity is held in restricted evidence and not published (FV2-D013). | Verified hostname; `forgev2-pl` account; bubblewrap; socat; root-owned `/usr/local/bin/claude` (version recorded); approved gitleaks build (SHA-256 recorded) |
| Test fixture | Each script run declares its own `mktemp -d` roots under `/tmp`, isolated from all project, engine and PL paths. They are removed on exit, except kept failure outputs. | Pre-flight assertion (S2) |
| Restricted evidence | `/root/forgev2-evidence/ENGINE-SANDBOX-TEST-001/` on the execution host, root `0700` | Exists, with the provisional evidence preserved (P4) |
| Untouched | Every application repository and checkout, including the CRM; FOUNDRY; ForgeV1; host services and configuration | n/a |

## 4. Defects in scope

All six are verified at the original base. Provisional evidence comes from Helm's run on 2026-11-06 and is preserved under P4.

| # | Defect | Evidence |
|---|---|---|
| D1 | **Missing `forge-start` arguments:** `--host` and `--worktrees`, both mandatory since `89f9f11` | The script's `forge-start` line; `plugin/bin/forge-start` (`required=True`) |
| D2 | **Fixture installation/project overlap.** The plugin copy is at `$FX/plugin` and the project at `$FX/proj`. Because `PROTECTED_INSTALLS ∋ dirname(dirname(LIB))`, which equals `$FX`, the guard correctly rejects the fixture. | `plugin/lib/forgelib.py` l.28, l.36, `validate_project_target()` |
| D3 | **Auditor probe non-execution.** The Auditor ran neither the probe nor the file-tool actions and returned INCONCLUSIVE. Its reasons: running them would be "working around a denial", and no candidate SHA was supplied, although unchanged `roles/auditor.md` step 1 requires one. The same refusal happened before (87/115 in `FORGEV2-PLUGIN-BUILD-001.md`). | Preserved Auditor transcript |
| D4 | **Wrong classification of probes that never ran.** 28 rows were scored FAIL, but the correct result is NOT RUN. The 5 Auditor PASS results are vacuous, because nothing was attempted. | Preserved transcript ("no commands run"); the script's scoring code |
| D5 | **Ineffective bubblewrap-unavailable test.** As the PL, `mkdir $FX/nobwrap` fails inside the root-owned 0755 `$FX`, so `ln -sf` fails and `PATH` points at nothing. "No command ran unsandboxed" therefore could not fail. | Preserved `nobwrap.out` (`Permission denied`) |
| D6 | **Unremoved temporary HOME.** The `tempfile.mkdtemp()` HOME from the bubblewrap-unavailable block is never deleted, and the cleanup pattern `forgev2-*` does not match it. | Leftover PL-owned `/tmp/tmp*` directory (preserved listing) |

**Provisional (non-canonical) result:** host 9/9, Engineer 32/32, Tester 33/33, Auditor 5 PASS and 28 FAIL. The correct Auditor reading is **33 NOT RUN**. These results are preserved unchanged, and canonical sandbox acceptance remains **BLOCKED**.

## 5. Changed-file allowlist

Any other path makes the WO BLOCKED.

1. `tests/host/sandbox-boundary.sh`
2. `tests/host/sbtest_lib.py`: new, stdlib only, for classification, corroboration parsing and the run ledger
3. Exactly one of: `tests/test_forgev2.py` (adding one regression class) or a new `tests/test_sandbox_boundary.py`
4. `plugin/README.md`: only the "Tests" section and the "Specialist sandbox" row of the "Property | Status" table. The text changes from "for the Engineer, Auditor and Tester" to all four specialists.
5. `INSTALL.md`: change `tests/host/os-boundary.sh` to `sandbox-boundary.sh`, with the invocation written "as root", not assuming `sudo`
6. `docs/evidence/ENGINE-SANDBOX-TEST-001.md` (new, sanitised)
7. `work-orders/ENGINE-SANDBOX-TEST-001.md`: this file, unchanged after approval
8. `DECISIONS.md`: one new FV2-D row recording the outcome, after acceptance

## 6. In-scope work

- **S1 (D1):** pass `--host "$(hostname)"` and `--worktrees "$PROJ/worktrees"` as canonical absolute paths.
- **S2 (D2):** use disjoint `mktemp -d` roots for the engine copy and the project, so that `dirname(dirname(<copy>/lib))` cannot contain the project. Add a pre-flight assertion that computes every protected path for the copied plugin and proves there is no overlap. **The guard is not modified, special-cased or bypassed.**
- **S3 (D3), probe execution prompt:** the test-only user prompt must:
  - cite this WO and the operator authorisation;
  - supply the fixture candidate SHA and base SHA, so that unchanged role step 1 can be satisfied;
  - state that attempting each listed action **once** and reporting the denial is the expected outcome, not a workaround.

  **No production role file changes.**
- **S4 (D3, D4), corroborated three-state classification:**
  - **Primary corroboration: harness-captured Claude Code tool events.** For the test run only, the harness re-runs the exact `specialist_command()` argv with only the output flags changed (`--output-format stream-json --verbose`). This records Claude Code's own `tool_use` and `tool_result` events: what was invoked, and what the tool layer returned or denied.
    - An Auditor check confirms that the argv differs from production only in those output flags.
    - S6 confirms the change does not alter the effective sandbox.
    - If either confirmation fails, primary corroboration is unavailable, and the affected rows are NOT RUN, never PASS.
  - **Secondary corroboration: a root-side observer.** While each specialist runs, a stdlib `/proc` watcher running as root (outside the sandbox) records that the probe process `sh probe.sh <role> <nonce>` existed with a bubblewrap ancestor. It also records the process's PID-namespace inode. The probe writes its own view of that inode into its result file, and the harness compares the two.
  - **The probe result file** (scratch, harness nonce) is used only together with corroboration. **An LLM-reachable result file alone is never independent evidence.**
  - **Command rows** score PASS or FAIL only if all three agree: (a) a `tool_result` for a Bash `tool_use` running the probe with the correct nonce contains the probe output; (b) the root observer recorded the probe under bubblewrap with a matching namespace; (c) the result file matches (a). Anything less is **NOT RUN**.
  - **File-tool rows** score from the `tool_use` and `tool_result` pair for each listed path, plus the on-disk effect. If the attempt is missing, the row is NOT RUN.
  - **Absence checks** (no write, canary absent, worktree read-only) are NOT RUN unless the corresponding attempt is corroborated.
  - **Output and exit codes:** separate PASS/FAIL/NOT RUN counts per role and overall. Exit `0` means all PASS; `1` means any FAIL; `3` means no FAIL but some NOT RUN; `2` means a setup or usage error.
- **S5, DevSecOps coverage:** add `devsecops` to the specialist loop, with the same expectations as the Auditor (non-Engineer profile). No change to `roles/devsecops.md`.
- **S6, deterministic verification (investigation only):**
  - **Question 1:** do the output-flag-only argv change in S4 and the presence of the root observer leave the effective sandbox unchanged? Compare the captured bubblewrap argv, settings and seccomp state between the production and test argv.
  - **Question 2:** can the command rows run without a model under the exact effective sandbox? Candidates:
    - (a) replay a captured bubblewrap invocation, accounting for the seccomp and proxy fds;
    - (b) a standalone sandbox runtime. This would be new external code requiring a register entry and CGPT approval; assess it, do not adopt it;
    - (c) a supported model-free tool-execution mechanism.
  - **Outcome:** if a technique is feasible with no new dependency, no production change and no relaxed setting, add it as an **additional** layer. File-tool rows stay model-driven.
  - **Evidence:** the evidence doc records the verdict and the observations behind it. No change to `sandbox_settings()`, `specialist_command()` or production sandbox architecture.
- **S7 (D5):** the restricted `PATH` lives in a PL-writable fixture directory that actually provides `sh`, `git` and `env`. Non-vacuity is shown in a disposable variant with bubblewrap reachable, where the marker appears. This demonstration is recorded and is not committed as a bypass.
- **S8 (D6):** every HOME the script creates uses a recognisable prefix, is removed on exit, and is covered by the cleanup assertion.
- **S9, recorded-run ledger:** each host run appends a record to the restricted evidence directory: UTC time, candidate or engine SHA, Claude version, per-role and overall counts, exit code, and kept-output SHA-256 manifest. The ledger is append-only, and the script never deletes or overwrites earlier records or kept outputs. Kept outputs move from a fixed `/tmp` name to a per-run directory under the evidence path.
- **S10, regression tests** (unit level, no model, no root):
  - required `forge-start` arguments are present;
  - the fixture layout passes `validate_project_target`, and an overlapping layout is rejected;
  - classification matrix: a missing or wrong-nonce result file; missing `tool_result`; missing observer record; a namespace mismatch; a contradicting value; an uncorroborated absence check gives NOT RUN; exit-code mapping;
  - the argv comparison allows only the output flags to differ;
  - `bash -n` passes on the script.

  Every new test is shown to fail when its fix is reverted.
- **S11, documentation and evidence:** the README and INSTALL rows above, and `docs/evidence/ENGINE-SANDBOX-TEST-001.md`. The evidence doc carries D1 to D6, the S6 verdicts, every host run with its counts (including FAIL and NOT RUN), the preserved provisional results, and the earlier 87/115 run unchanged. It also states residual limits. No hostname, IP or access details appear in it.

## 7. Explicit exclusions

- Any file under `plugin/` except the `plugin/README.md` rows above. This covers `bin`, `lib`, `hooks`, `roles`, `skills`, `.claude-plugin` and `ORCHESTRATOR.md`.
- Weakening, special-casing or adding a bypass flag to the protected-install guard.
- Changes to production role definitions, or to sandbox filesystem, network, nested-userns or unsandboxed-command settings.
- Suppressing, skipping or downgrading checks. Reclassifying NOT RUN as PASS or FAIL, or FAIL as NOT RUN. Deleting or overwriting earlier run records.
- The root-context unit-test dependency (F1) and Python bytecode pollution (F2).
- `/srv/forgev2`; the CRM and all customer applications; FOUNDRY; ForgeV1; host configuration; `feat/remote-execution`.

## 8. Roles and independent evidence

Each specialist is a fresh, separate, supervised Claude Code session, and none receives another's reasoning. Each writes only its own log (section 12) and names the candidate SHA it assessed. The FOUNDRY sequence is Engineer → Auditor → Tester → DevSecOps. Each specialist has at most 4 executions (FND-036, FV2-D008), persisted by the PL in `PL.log`; exhaustion is FAIL. Any Engineer change invalidates earlier PASS results. Final acceptance needs PASS from all three reviewers on the same unchanged candidate.

| Role | Assignment | Independent evidence |
|---|---|---|
| Product Owner | Matt | Stage approvals, merge decision, sandbox acceptance |
| Architect | CGPT | Exact-version approval; architectural acceptance |
| Orchestrator | Rogue | Assigns the approved WO, aggregates Issue status, returns evidence. No implementation, Git writes or acceptance. |
| PL | A supervised engine-development session on the execution host, assigned by Matt; its execution identity is decision M1 | Entry-gate record, counters, commits, allowlist diff check, PR |
| Engineer | A fresh supervised session, distinct from the PL | `ENGINEER.log`: changes, unit results, revert-and-rerun per new test, S6 notes |
| Auditor | A fresh session | Allowlist; guard untouched; no path maps missing or uncorroborated evidence to PASS or FAIL; argv differs only in output flags; tests can fail; roles unchanged |
| Tester | A fresh session, which is also the host-test operator (root, under Matt's stage approval) | Unit suite, `bash -n`, host runs on the candidate. Disposable demonstrations: a forged result file with no tool event or observer record gives NOT RUN; a refusal gives NOT RUN; bubblewrap reachable shows the marker. Counts recorded as printed. Browser gate not applicable (no web UI), with that stated. |
| DevSecOps | A fresh session | Root-run safety: temp-path and TOCTOU handling, `rm` scope, permissions of the observer and the evidence directory; canary and credential exposure in the stream-json transcripts and kept outputs; observer privilege; no new dependency; gitleaks clean |

## 9. Acceptance criteria

1. **AC1:** the fixture's `forge-start` succeeds with `--host` and `--worktrees`, and the regression test fails if either is removed.
2. **AC2:** the pre-flight shows no overlap with any protected path. `git diff <original-base>..<candidate> -- plugin/` touches only `plugin/README.md`.
3. **AC3:** probe rows score PASS or FAIL only with all three corroborations present. A forged result file without a tool event or observer record yields NOT RUN, shown both in a unit test and in a disposable host demonstration.
4. **AC4:** PASS, FAIL and NOT RUN counts are reported separately and exit codes follow S4. A specialist that attempts nothing yields NOT RUN for all of its rows, absence checks included.
5. **AC5:** DevSecOps rows are present and scored like the Auditor's.
6. **AC6:** the S6 verdicts are recorded with evidence. The test-mode argv leaves the effective sandbox unchanged, or the rows depending on it are NOT RUN.
7. **AC7:** the bubblewrap-unavailable check provides `sh`, `git` and `env` on its `PATH`, and the non-vacuity demonstration is recorded.
8. **AC8:** no leftover HOME after a run, and the cleanup check detects a planted one.
9. **AC9:** the run ledger is append-only, and earlier records and kept outputs survive later runs.
10. **AC10:** `python3 -m unittest discover -s tests` passes, and each new test fails when its fix is reverted.
11. **AC11, host acceptance (post-merge, section 11):** at most **three** recorded complete runs from the root-owned pinned `/srv/forgev2` at the merge SHA. Acceptance requires one run with **0 FAIL and 0 NOT RUN** across host, all four specialists, on-disk effects and the bubblewrap-unavailable section. The retry rules:
    - **Any FAIL** stops the sequence: no further runs, return to CGPT.
    - **A re-run is allowed only** when the previous run's sole defect is NOT RUN from model refusal or a void specialist result, and the cause is recorded first.
    - **Every run stays in the ledger and the evidence doc.**
12. **AC12:** the pinned `/srv/forgev2` matches its recorded baseline (HEAD, ignored-status, `.git` entry listing) throughout implementation. Its only change is the approved pin update.
13. **AC13:** the approved gitleaks build reports the branch clean, and public files contain no hostname, IP or credential.

## 10. Preservation of earlier failures

**P4, required before dispatch:** the provisional outputs (`auditor.txt`, `engineer.txt`, `tester.txt`, `*.err`, `nobwrap.out`) and the listing of the leftover HOME are copied byte-for-byte, with a SHA-256 manifest, to `/root/forgev2-evidence/ENGINE-SANDBOX-TEST-001/provisional-2026-11-06/`. They currently sit only in tmpfs `/tmp`. Nothing is deleted. Whether the leftover HOME is removed after it has been recorded is Matt's decision.

The provisional 5 PASS / 28 FAIL Auditor result, its corrected reading of 33 NOT RUN, and the earlier 87/115 run are all carried into the evidence doc verbatim.

## 11. PR, merge and pinning gates

1. A PR from `work/engine-sandbox-test-001` to `main`, opened by the PL. No force-push, no `--no-verify`, and no direct commit to `main`.
2. **Before merge:**
   - Auditor, Tester and DevSecOps PASS on the PR head SHA. The Tester's candidate host runs are diagnostic only; acceptance is AC11.
   - CGPT architectural acceptance on the Issue.
   - Matt's merge decision. Rogue never merges.
3. **Pin update after merge** (approved by Matt, carried out by Helm):
   - Confirm `git diff 63b6b8a..<merge-sha> -- plugin/` touches only `plugin/README.md`. Runtime is then byte-identical and the plugin stays 0.3.0.
   - Fast-forward `/srv/forgev2` to `<merge-sha>`.
   - Verify HEAD, a clean ignored-status and root ownership.
4. **AC11 runs** against `/srv/forgev2/plugin`, as root, each run under Matt's stage approval.
5. **Matt records the sandbox acceptance decision** on the Issue. Only then are the ROGUE.md pin and gates updated, with Matt's agreement. **No CRM implementation WO runs before that record exists.**

## 12. Communications, logs and evidence

- **Status channel:** the WO Issue. Updates are concise and event-driven: start, state transitions, PASS/FAIL with evidence links, blockers, completion.
- **Restricted logs** in `/root/forgev2-evidence/ENGINE-SANDBOX-TEST-001/` (root `0700`):

  | File or directory | Written by |
  |---|---|
  | `PL.log` | PL (including counters) |
  | `ENGINEER.log` | Engineer |
  | `AUDITOR.log` | Auditor |
  | `TESTER.log` | Tester |
  | `DEVSECOPS.log` | DevSecOps |
  | `runs/` (ledger and kept outputs) | Script, under the Tester |
  | `provisional-2026-11-06/` | Preservation step P4 |

  Each file is written only by its named role. Readers: Matt, Rogue, and CGPT on request through sanitised extracts.
- **Public evidence:** `docs/evidence/ENGINE-SANDBOX-TEST-001.md`.
- **Completion report:**
  - outcome;
  - changed paths;
  - original base, start and final SHAs;
  - results for AC1 to AC13;
  - reviewer verdicts;
  - every run with its counts;
  - S6 verdicts;
  - deviations (section 15);
  - limits and residual risks.

## 13. Entry prerequisites

- **P1:** this artifact has been committed, and CGPT's exact-version approval is recorded on the Issue.
- **P2:** `/srv/src/forgev2/main` is cloned and verified, and `/srv/src/forgev2/worktrees/` is created, with ownership set per decision M1. Provisioning is Helm's lane, under Matt's approval.
- **P3:** remote `main` still equals the original base, and `feat/remote-execution` has not merged.
- **P4:** the provisional evidence has been preserved (section 10).
- **P5:** decision M1 is recorded.

## 14. Decision required from Matt

**M1: execution identity for the supervised engine-development sessions and the push credential.**
- FV2-D019 reserves `root` for Matt's administration and requires non-root engineering execution.
- `forgev2-pl` holds a deploy key for the CRM repository only.
- The `maff0000/forgev2` credential on the execution host belongs to root's `gh` login.

Options:
- (a) A narrowly scoped, FV2-D022-style exception for this WO only: a root-local supervised session, with Matt approving each stage.
- (b) A separate non-root engine-development account with its own scoped push credential.

The Architect's ruling ("supervised engine-development implementation on the execution host") does not settle which. Option (b) needs a host change (Helm) and a credential decision.

## 15. Recorded deviation: Git metadata write in the pinned installation

- **What:** at 15:28:26 UTC on 2026-11-06, Rogue ran `git fetch -q origin feat/remote-execution` inside `/srv/forgev2` while preparing draft v0.1. It was unauthorised, and it breaks Rogue's own rule against modifying the pinned checkout.
- **Observed effects:**
  - `.git/FETCH_HEAD` was **created**. It was absent before; the `.git` directory's mtime moved to 15:28. Its content is `994185e80950de29ea4c98c0caa7c5b7d7799755  branch 'feat/remote-execution' of https://github.com/maff0000/forgev2`.
  - The `.git/objects` directory's mtime changed.
  - No new object files were written (`count: 0`; one pack, `in-pack: 525`).
  - `refs/remotes/origin/feat/remote-execution` is unchanged at `994185e`, as already recorded in `packed-refs` (mtime 2026-11-04).
  - `.git/index`, `HEAD` and `config` are unchanged (mtime 2026-11-04).
  - HEAD is still `63b6b8a…`, `status --porcelain --ignored` is empty, and runtime files are untouched.
- **Not altered or cleaned:** `FETCH_HEAD` stays in place as evidence, and removing it is Matt's decision. It is part of the AC12 baseline.
- **Prevention rule:**
  - In protected installs and in checkouts Rogue does not own, Rogue runs only non-writing Git commands: `rev-parse`, `log`, `show`, `diff`, `cat-file`, `for-each-ref`, `remote -v`, `ls-remote`, and `GIT_OPTIONAL_LOCKS=0 git status`.
  - To compare remotes, Rogue uses `ls-remote` or a disposable clone in its own scratch area.
  - Rogue never runs `fetch`, `pull`, `gc`, `checkout`, `config` or `worktree` in protected paths.
  - This rule is also proposed as a FOUNDRY rule in FOUNDRY-ORCH-SETUP-001.

## 16. Separate future findings (not in this WO)

- **F1:** the unit tests depend on root context.
- **F2:** Python bytecode (`__pycache__`) pollution.
- **F3:** specialist stderr reports `Claude configuration file not found at <PL home>/.claude/.claude.json`, while a backup exists. The shared `CLAUDE_CONFIG_DIR` is the likely link. This is for the host and PL-account lane, before live WOs.
- **F4:** `plugin/ORCHESTRATOR.md` uses `sudo` and `/srv/forgev2/src/plugin`. The host has no `sudo`, and the verified path is `/srv/forgev2/plugin`.
- **F5:** the ForgeV2 README cites FOUNDRY `aee8618`; it should cite the governing revision.
- **F6:** root's Claude Code is 2.1.319, while the root-owned `/usr/local/bin/claude` used by the PL is 2.1.317. The version pin and its recording are FV2-D006 and FV2-009 matters.
