# ENGINE-PACKAGING-001 — ForgeV2 Plugin Packaging

- **Status:** DRAFT — no implementation authority
- **Work Order:** ENGINE-PACKAGING-001
- **GitHub Issue:** [#2](https://github.com/maff0000/forgev2/issues/2)
- **Parent PBI:** FV2-001
- **Governing FOUNDRY:** [`aee86185aac6aa0d2ab7a243138c423292af191a`](https://github.com/maff0000/foundry/tree/aee86185aac6aa0d2ab7a243138c423292af191a)
- **Project initiation:** [PIM v0.2](../PROJECT-INITIATION-MANDATE.md), Stage 1 CLOSED GREEN
- **Approved product direction:** `PRODUCT-VISION.md` and `PRODUCT-BACKLOG.md` at [`071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`](https://github.com/maff0000/forgev2/tree/071426b4cf2b39c39e6e6dd5be619e8afd06d8cb); Matt's exact-version approval is recorded in [Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6386137638).
- **Plugin identity:** `forgev2`, development version `0.1.0-dev.1`, source package `plugin/`; not an approved release.
- **CGPT browser-applicability determination:** Real-browser testing of a new application is inapplicable to this packaging-only increment. Independent Tester functional verification remains required. The inherited Auditor's real-browser gate must be preserved without weakening.
- **Architect approval:** Not granted. CGPT must approve this exact committed artifact version through a traceable Issue #2 record before dispatch.
- **Delivery assignment:** None. No PL is assigned; the proposed manual orchestration requires explicit exact-version approval before dispatch.

This draft is prepared under the [FOUNDRY Work Order contract](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/work-order-contract.md) and [secure engineering standard](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/secure-engineering.md). It describes a proposed bounded engine-development increment; it does not authorize implementation, installation, deployment, or changes to ForgeV1.

## 1. Intended outcome

Package the inherited and proven ForgeV1 Project Lead (PL), Engineer, Auditor, and associated skills as a portable, versioned Claude Code plugin. Preserve successful ForgeV1 startup, PID, delivery, Git-authority, independence, and real-browser assurance behavior while making plugin resources resolve from the plugin itself and allowing the PL to operate on a separately identified application repository.

One WO is one bounded ForgeV2 delivery cycle; FV2-001 may be delivered by multiple separately approved WOs. This is ForgeV2 engine-source development, not an application Work Order or a ForgeV2 release. The inherited source lineage is the ForgeV1 import at `665b32c991caaace95710abd22af6d4c97eefc3b`; verify the relevant objects and paths in the approved ForgeV2 baseline. It is compatibility input, not authority to change the operational `maff0000/forge` repository or installation.

## 2. Authority and approved context

- Matt retains product direction, priority, material product-risk acceptance, and final product acceptance. The approved FV2-001 direction and exact-version provenance above apply.
- CGPT is the Project Architect and must approve this exact Work Order version before any delivery dispatch. New dependencies and architectural exceptions also require CGPT approval; material risk acceptance beyond architectural authority goes to Matt.
- Normally the Orchestrator assigns an approved WO to a named PL. For this bootstrap only, Matt and CGPT manually perform that coordination and explicitly assign an existing PL-capable Claude session; Rogue is not required. No ForgeV2 Orchestrator or PL runtime is claimed to exist yet.
- The PL controls all Git/GitHub mutation within the authorized WO branch. Engineer, Auditor, Tester, and DevSecOps do not commit, push, create branches, or mutate GitHub.
- The PL owns the persistent per-specialist execution record for this WO. These are documentary operating requirements, not implemented enforcement.

Issue #2 establishes the request and traceability, not approval. Approval requires an explicit CGPT decision identifying this file and the immutable commit that already contains the reviewed content. After that commit exists, CGPT's approval and the exact approved artifact SHA must be recorded on Issue #2. Do not embed a self-referential commit SHA in this file. Any subsequent content change requires a new artifact version and renewed approval.

## 3. Repository and workspace boundary

| Item | Authorized identity or boundary | Required entry verification |
| --- | --- | --- |
| Target repository | `maff0000/forgev2` | Verify the GitHub identity, configured remote, and repository access. |
| Original engineering-source baseline | Commit `5e6d5d6ce7d369e64b8d4f2078acfeb6feee6822`; historical source baseline for this WO | Verify the approved WO commit descends from this SHA and that the only intervening changed path is this approved Work Order documentation. Verify inherited implementation source is unchanged. This SHA is not the engineering worktree starting commit. |
| Approved WO artifact commit | The exact CGPT-approved commit recorded on Issue #2 after that commit exists | Before worktree creation, verify this commit was fast-forwarded to `main`, remains on the original baseline's ancestry, and contains the exact approved Work Order. No SHA is embedded in this file. |
| Canonical engine-source checkout | `/srv/src/forgev2/main/` | Verify on the approved development environment that the checkout is clean and at the exact approved WO commit on `main`. Keep it unchanged during implementation. |
| WO branch | `work/engine-packaging-001` | PL creates and controls this branch from the exact approved WO commit only after it has been fast-forwarded to `main` and all entry gates pass. No writes to `main`. |
| Authorized engine-source worktree | `/srv/src/forgev2/worktrees/engine-packaging-001/` | PL creates this sibling worktree from the WO branch at the exact approved WO commit. Verify its HEAD and Work Order contents equal the approved artifact, and verify branch, clean state, repository identity, ancestry, and worktree lineage before dispatch. Do not use Claude automatic worktree isolation for this cross-repository/hub arrangement. |
| Protected engine installation | `/srv/forgev2/` | Must remain outside all write paths. This WO does not install, update, or execute an installed ForgeV2 engine. |
| PACMAN application root | `/srv/pacman/` | Must remain untouched. No PACMAN files or worktrees are in scope. |
| Disposable test fixture | Temporary, isolated local Git repositories and worktrees generated only for tests under the approved test workspace | No GitHub application repository, product initiation, or network access is required. Synthetic fixture `PID.md` content tests presence/absence gates only and grants no authority. Verify fixture paths are outside protected engine and operational ForgeV1 locations and remove them after use. |

These are project-specific approved layout decisions, not FOUNDRY-wide defaults. The actual host/workspace identity and present availability must be verified and recorded in the private or otherwise approved delivery evidence before work. This public Work Order intentionally omits hostnames, addresses, SSH aliases, access details, and sensitive operational evidence. No application write, log, build, dependency, test, or asset path may enter the protected engine installation. No unapproved filesystem/repository overlap is permitted.

Before creating the branch or worktree, the PL verifies and records that the exact CGPT-approved WO commit from Issue #2 is the current remote and local `main` HEAD; that it descends from the original engineering-source baseline; and that the complete change set since that baseline contains only this approved WO documentation. Compare inherited implementation paths/content with the original baseline and confirm they are unchanged. Create the branch and sibling worktree from that approved commit, then verify the worktree HEAD and its copy of this Work Order match it exactly. If `main` has moved, the ancestry or changed-path check fails, or any inherited implementation source differs, stop and return to CGPT; do not retarget or repair silently.

The authorized Git push target, after CGPT approves this exact WO version and Matt/CGPT manually assign the named PL, is only the PL-controlled `work/engine-packaging-001` branch in `maff0000/forgev2`. The PL must verify the configured destination and SSH identity using existing authorized access; do not hard-code an SSH alias or change credentials. Specialists have no Git/GitHub write authority. Record both the original engineering-source baseline and the actual engineering-worktree starting commit in `PL.log` and the delivery evidence.

## 4. Scope

The PL may authorize changes only on the WO branch, within these paths:

- The `forgev2` Claude Code plugin source package under `plugin/`, development version `0.1.0-dev.1`, including its manifest, namespaced PL/Engineer/Auditor definitions, skills, and required plugin-owned resources/scripts. This is not an approved release.
- `tests/engine-packaging-001/` for bounded package-level validation using disposable, isolated local Git fixtures; do not create an application or GitHub repository.
- `security/EXTERNAL_CODE_REGISTER.yaml`, only to record verified code/dependency provenance and truthful coverage for incorporated material; do not claim full coverage unless evidenced.
- `docs/evidence/ENGINE-PACKAGING-001/` for sanitized, reproducible results tied to exact candidate identities.
- `work-orders/logs/ENGINE-PACKAGING-001/` for the WO-specific role and PL records described in §8.

All other paths are excluded unless CGPT approves a revised, exact-version Work Order before the affected change. In particular, do not modify inherited `.claude/` roles or skills, `ops/pl-startup-gate`, `PID.md`, product records, ForgeV1, deployment configuration, host configuration, or any installed engine. The PL may read inherited files to assess and package their behavior. Do not execute inherited scripts, hooks, bootstrap helpers, or self-tests until their contents and effects have been assessed and the PL records that assessment.

### Required design and delivery coverage

The candidate must:

1. Provide a valid Claude Code plugin manifest and portable plugin layout, with namespaced PL, Engineer, and Auditor agents. Use the [official plugin overview](https://code.claude.com/docs/en/plugins), [creation guide](https://code.claude.com/docs/en/plugins/create), [component reference](https://code.claude.com/docs/en/plugins/components), and [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference) as current upstream references. Verify behavior against the exact reviewed Claude Code CLI version; documentation alone does not prove compatibility.
2. Resolve plugin-owned instructions, resources, and scripts relative to the plugin root, not the caller's working directory or a globally fixed host path.
3. Preserve the existing PL startup gate and `PID.md` requirement. Preserve PID content and authority: a FOUNDRY PIM is initiation context; neither PIM nor approved WO replaces a ForgeV1 PID or startup gate. The approved WO is distinct delivery authority. No work begins on a project that fails its applicable startup/authority gates.
4. Preserve PL ownership of Git operations and specialist prohibition on commit/push/GitHub mutation.
5. Require explicit sibling worktrees created from the correct target repository, with branch, starting SHA, remote identity, and lineage verified before dispatch. Do not rely on Claude automatic worktree isolation in the hub model.
6. Work with the project's already configured, verified GitHub SSH identity without baking operator-specific aliases, keys, or credentials into plugin content.
7. Preserve the Auditor's independence, evidence standards, and mandatory real-browser gate whenever its existing PID conditions apply. Do not weaken or remove ForgeV1 browser assurance before an equivalent ForgeV2 Tester capability is proven.
8. Apply reuse-first engineering and the FOUNDRY Security by Design competence at [`skills/security-by-design.md`](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/skills/security-by-design.md), alongside the secure engineering standard. A skill provides competence, not authority; do not claim runtime skill loading beyond behavior actually verified.
9. Assess copied/vendor executable code and every introduced dependency before trusting or executing it. Obtain exact provenance and version/hash, license suitability, vulnerability and supply-chain evidence, transitive-dependency awareness, and required CGPT/security approval. Update the external-code register truthfully. No unapproved third-party dependency, remotely hosted executable, CDN code, fake register entry, or unsupported coverage claim is allowed. Scanning alone is not a safety determination.
10. Validate the package with the approved, assessed CLI (including `claude plugin validate .` from the plugin root) and provide reproducible evidence using disposable, isolated local Git fixtures. Exercise plugin discovery/loading without installing or deploying the engine, namespaced agent availability, plugin-relative paths from a different project root, startup/PID/remote-identity boundaries, and correct project-owned sibling worktree routing. A new application's real-browser test is inapplicable to this packaging-only increment; the independent Tester must still verify these functional behaviors. Preserve the inherited Auditor's real-browser gate without weakening it.
11. Keep engine source, any eventual installation, and disposable local test fixtures isolated. This Work Order produces source and evidence only; it does not promote or release a plugin into `/srv/forgev2/`.
12. Freeze and identify the implementation candidate by its exact Git commit SHA and clean tree. Auditor, Tester, and DevSecOps assess that same frozen implementation candidate. Evidence-only commits may follow only when independent comparison shows implementation contents are unchanged. Any Engineer source modification invalidates prior reviewer PASS results and restarts assurance on the new frozen candidate.

## 5. Blocking prerequisites and unresolved design decisions

The following are not established by the repository baseline and must be resolved and evidenced before CGPT can approve this Work Order for dispatch. A missing prerequisite is **BLOCKED + specific reason + evidence**, never an inferred pass.

1. **Bootstrap authority and role coverage — exact-version approval required.** ForgeV2 has no implemented Orchestrator, installed ForgeV2 PL, Tester, or DevSecOps role. Matt and CGPT will manually coordinate the Orchestrator function and explicitly assign one existing PL-capable Claude session to control the ForgeV2 WO branch using unchanged ForgeV1 PL/Engineer/Auditor doctrine. CGPT must appoint independent Auditor, Tester, and DevSecOps reviewers, with named identities and role boundaries recorded before dispatch. Do not represent temporary reviewers as implemented ForgeV2 agents. The arrangement is usable only after CGPT approves this exact Work Order version and the assignment before dispatch. If independent required assessments cannot be provided, do not waive or silently skip them; dispatch is BLOCKED.
2. **Disposable local fixture — PL verification required.** No application or GitHub test repository is required. Generate isolated local Git repositories/worktrees only for testing, using synthetic remote identities clearly marked as fixtures and no network access. The tests must provide meaningful positive and negative cases for the applicable startup, PID, remote-identity, and worktree gates. Verify fixture identity, paths, and cleanup; never present synthetic remote values as real repository evidence.
3. **Current development workspace and approved baseline — PL verification required.** Previously recorded workspace evidence is historical and does not establish current host availability, identity, checkout cleanliness, branch state, worktree absence, or exact baseline. At worktree creation, verify `main` equals the exact approved WO commit recorded on Issue #2; verify ancestry from the original engineering-source baseline; verify the only intervening change is this approved Work Order; compare inherited implementation source as unchanged; and confirm the new worktree contains the exact approved WO. Record the original baseline and actual worktree starting commit. If `main` moved, any check differs, or implementation files changed, stop for CGPT review without retargeting. Do not substitute a local Mac, different host, or guessed path.
4. **Runtime security and credentials — approval required.** Before executing the CLI, plugin, scripts, builds, or fixtures, establish a non-root delivery identity or equivalent enforceable isolation protecting the engine installation; verify appropriately scoped credentials; and obtain CGPT approval of runtime-security evidence. No credential or host changes are authorized here. If these controls cannot be verified, dispatch is BLOCKED.
5. **Claude Code CLI — CGPT approval required.** Pin the exact CLI version and assess its source/provenance, license, and suitability before validation or plugin execution. The earlier loading spike's reported CLI version is not an approved current pin. Do not install or update a CLI under this WO.
6. **Existing inventory coverage — PL/security reviewer assessment required.** The current ForgeV2 external-code register reports incomplete coverage. Inspect and record the scope and gaps relevant to packaging and test execution. Do not execute unassessed inherited or external code; if required provenance cannot be established, stop for CGPT/security decision.

The plugin identity/version and browser-applicability determination are established for this draft; neither makes it an approved release or waives independent Tester/Auditor assurance. Remaining prerequisites do not change the approved product direction and are not permission to implement missing ForgeV2 capabilities.

## 6. Explicit exclusions

This WO does not authorize:

- Building an Orchestrator, Tester, or DevSecOps agent, implementing full WO dispatch automation, or changing ForgeV1 PL/Engineer/Auditor behavior.
- Implementing persistent execution-counter enforcement. The PL must still maintain the required durable manual record for this WO; tooling enforcement remains excluded.
- Changing ForgeV1's existing PID/startup, Git authority, worktree, independence, or browser behavior; modifying the operational ForgeV1 repository or installation; or executing its unassessed scripts.
- Installing, promoting, or deploying ForgeV2; changing `/srv/forgev2/`; or implementing an engine release/upgrade process.
- Creating or implementing PACMAN, writing under `/srv/pacman/`, or adding application code to the ForgeV2 engine repository.
- Changing hosts, users, filesystem permissions, network/firewall rules, SSH, credentials, secrets, or repository security settings.
- Adding unapproved dependencies, remote executable/CDN loading, CI, scanners, SBOM generators, audit automation, schedulers, or other automated enforcement.
- Merging the WO branch or modifying `main`.

## 7. Acceptance criteria

The PL may present the candidate for final acceptance only when all applicable criteria below have evidence:

1. The source package is `plugin/`, and its manifest identifies plugin `forgev2` at development version `0.1.0-dev.1`. `claude plugin validate .` from the plugin root and approved load checks pass with the exact approved CLI version. This is a development candidate, not an approved release.
2. PL, Engineer, and Auditor are discoverable under the `forgev2` plugin namespace, and their instructions/resources load from plugin-owned paths when invoked from a separate fixture working directory.
3. Startup/PID and authority behavior remains intact: the existing gate is preserved; missing or invalid project authority blocks dispatch; PIM, PID, and WO remain distinct; and no approved WO means no implementation authority.
4. Only the PL performs Git/GitHub operations. Disposable local fixtures provide positive and negative tests for each applicable gate: valid versus missing startup prerequisites; present versus absent synthetic `PID.md`; expected versus wrong synthetic GitHub-form remote identity; and a correctly derived sibling worktree versus a wrong-repository or wrong-lineage worktree. These use local Git repositories and synthetic remote URLs only; they make no network requests and do not claim a real GitHub repository. The PL demonstrates expected fixture history resolves in the worktree, not merely that it is clean.
5. Plugin operation does not write to or alter the protected engine installation, canonical main checkout, operational ForgeV1, or unrelated project paths. Before/after Git and filesystem evidence identifies the candidate and verifies those boundaries without publishing sensitive host details.
6. The independent Tester functionally verifies plugin discovery/loading, authority and startup/PID/remote-identity gates, correct-project worktree routing, and negative cases using isolated local fixtures. CGPT has determined real-browser testing of a new application is inapplicable to this packaging-only increment. Preserve and validate the inherited Auditor's real-browser gate without weakening it; where that gate applies in future product work, it remains mandatory until an equivalent ForgeV2 Tester capability is proven.
7. Independent assurance follows Engineer → Auditor → Tester → DevSecOps. Each reviewer reports PASS or FAIL, reason, evidence locations, reviewer identity, and exact candidate SHA. FAIL findings route through the PL to Engineer correction or escalation. Every applicable reviewer returns PASS on the same unchanged candidate before completion.
8. The execution record is persisted by the PL per specialist for this WO: maximum four executions each, including the first; fifth prohibited; counts survive restart/context reset; no reset or replacement WO bypass; exhaustion is FAIL with reason and evidence. No technical enforcement is claimed.
9. Reuse-first and Security by Design requirements are evidenced. Every copied/vendor component and executable dependency in scope is assessed and recorded with verified provenance, exact version/hash, location, consumer, purpose, license, security/approval evidence, and truthful inventory coverage. Unapproved material is not trusted or executed; no externally hosted executable is introduced.
10. Changes are limited to the approved scope, existing ForgeV1 behavior is preserved, and `security/EXTERNAL_CODE_REGISTER.yaml` accurately states the inspected coverage and remaining gaps. No placeholder/fabricated inventory data is added.
11. Final evidence records both the original engineering-source baseline and the actual engineering-worktree starting commit, changed paths, frozen implementation candidate SHA, clean working tree, test commands/results, external-code assessment, reviewer PASS records, and limitations. All reviewers assess that same implementation SHA. Evidence-only commits may follow only when independent comparison proves implementation contents are unchanged; report both the implementation candidate SHA and evidence commit SHA. Any Engineer source change creates a new frozen candidate and restarts all required assurance.
12. The PL returns a completion report through the Orchestrator to CGPT. CGPT performs architectural acceptance; Matt retains product acceptance. No merge or engine installation/deployment is included.
13. At worktree creation, evidence confirms `main` equals the exact approved WO commit recorded on Issue #2; that commit descends from original baseline `5e6d5d6ce7d369e64b8d4f2078acfeb6feee6822`; the only intervening changed path is this approved Work Order; inherited implementation source is unchanged; and the worktree contains the exact approved WO at the exact approved SHA. Any mismatch or unexpected `main` movement stops work for CGPT review.

## 8. Communications, logs, and execution bounds

Use [Issue #2](https://github.com/maff0000/forgev2/issues/2) for WO status and sanitized evidence links. It is not itself approval. Keep role records in the project repository at `work-orders/logs/ENGINE-PACKAGING-001/`, subject to entry verification and public-safe content:

| Record | Writer | Readers and purpose |
| --- | --- | --- |
| `work-orders/logs/ENGINE-PACKAGING-001/PL.log` | Assigned PL only | Matt and CGPT; authoritative progress, prerequisite decisions, branch/worktree identity, specialist counters, dispatches, frozen candidate SHA, escalations, and final aggregate report. |
| `work-orders/logs/ENGINE-PACKAGING-001/ENGINEER.log` | Assigned Engineer only | PL; bounded implementation actions, commands, changed paths, test results, and escalation. |
| `work-orders/logs/ENGINE-PACKAGING-001/AUDITOR.log` | Independent Auditor only | PL and CGPT; independent findings and PASS/FAIL tied to the frozen implementation candidate SHA. |
| `work-orders/logs/ENGINE-PACKAGING-001/TESTER.log` | Independent Tester only | PL and CGPT; functional test procedure, observations, artifacts, and PASS/FAIL tied to the frozen implementation candidate SHA. |
| `work-orders/logs/ENGINE-PACKAGING-001/DEVSECOPS.log` | Independent DevSecOps reviewer only | PL and CGPT; provenance, dependency, trust-boundary, security evidence, findings, and PASS/FAIL tied to the frozen implementation candidate SHA. |

The PL verifies actual writable locations and access before dispatch. Do not put credentials, host-specific access configuration, private security evidence, or sensitive data in these public-repository logs; retain restricted evidence only in an approved location and reference it without disclosure. Each specialist receives only the approved WO and the context needed for that role. The PL persists each specialist's execution counter in `PL.log` across restarts/context resets and records each invocation in that specialist's role log.

Each specialist has an independent maximum of four executions for this WO, counting its first invocation. A fifth is prohibited. Counts persist across restarts and context resets. The specialist checks its own limit; the PL's durable `work-orders/logs/ENGINE-PACKAGING-001/PL.log` record is authoritative. No counter reset or replacement WO may bypass exhaustion. Exhaustion is FAIL with reason and evidence. Only Engineer escalates an execution failure to the PL. Material architectural ambiguity goes to CGPT; product direction, priority, or material product risk goes through the Orchestrator to Matt. No role may expand scope by interpretation.

Progress reports are event-driven and concise: dispatch, verified gate result, material finding/blocker, candidate change, each assurance result, and completion. On any failed entry condition, wrong repository/worktree, changed baseline, unassessed dependency, missing approval/reviewer, candidate mismatch, or unsafe boundary, the PL records **BLOCKED + reason + evidence** and stops affected work. No reviewer gate may be silently skipped.

## 9. Evidence and candidate acceptance

Store sanitized, reproducible evidence under `docs/evidence/ENGINE-PACKAGING-001/`, including:

- Exact CLI version and plugin validator output.
- Plugin discovery/loading and namespaced-role checks.
- Disposable local fixture setup/cleanup, synthetic remote identities, baseline, PID/startup-gate outcomes, and positive/negative worktree-lineage results; no test application or external GitHub repo is created.
- Worktree repository/branch/lineage checks and before/after boundary evidence.
- Reuse and security/dependency review, register coverage statement, and explicit approvals.
- Functional evidence and the separate Auditor, Tester, and DevSecOps reports; no new-application browser test is applicable to this packaging-only increment.
- Original engineering-source baseline SHA and actual engineering-worktree starting SHA; approved WO SHA from Issue #2; candidate SHAs, changed paths, clean-tree evidence, and completion report.

Evidence must be reproducible where practicable and must distinguish verified facts, inference, and unknowns. Redact operational details that are not suitable for this public repository. Freeze the implementation candidate at an exact Git commit SHA with a verified clean implementation tree; all reviewers independently confirm they assessed that same SHA. Evidence-only commits may follow if independent comparison proves implementation paths and content unchanged, with both SHAs recorded. Any Engineer source change invalidates earlier PASS reports and requires a new frozen candidate and restarted assurance.

## 10. Proposed bootstrap delivery arrangement

Because the ForgeV2 Orchestrator and installed PL/specialist chain do not yet exist, a one-time manual bootstrap is proposed: Matt and CGPT manually coordinate the Orchestrator function and explicitly assign one existing PL-capable Claude session to control the ForgeV2 WO branch using unchanged ForgeV1 PL/Engineer/Auditor doctrine. CGPT appoints independent Auditor, Tester, and DevSecOps reviewers; the PL records four-execution limits durably by hand. No temporary reviewer is represented as a shipped ForgeV2 role, and no missing capability or assurance gate is waived. The PL retains Git control. This arrangement requires CGPT's explicit approval of this exact committed WO version and named assignments before dispatch.

This proposal is not dispatch authority. If CGPT cannot identify an independent reviewer for every required assessment, or the disposable local fixture cannot safely exercise the required gates, the WO remains BLOCKED. Use a non-root delivery identity or equivalent enforceable isolation protecting the engine installation, scoped credentials, and CGPT-approved runtime-security evidence; a root session or Claude tool restrictions alone are not an enforceable boundary. Do not load or execute unassessed source.

## 11. Completion and stop

The WO cycle completes only after all entry gates, acceptance criteria, and applicable independent assurance pass on one unchanged candidate, the PL's completion evidence is returned through the Orchestrator, and CGPT accepts the result. A failed or missing gate is not a pass. An unresolved architectural ambiguity returns to CGPT; product-authority decisions return to Matt. Stop after the candidate and evidence are submitted for acceptance.

This draft authorizes no dispatch. Even after exact-version approval, this Work Order does not authorize merging, ForgeV2 installation/release, host changes, PACMAN work, or any excluded capability above.
