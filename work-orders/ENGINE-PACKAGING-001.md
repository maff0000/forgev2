# ENGINE-PACKAGING-001 — ForgeV2 Plugin Packaging

- **Status:** DRAFT — no implementation authority
- **Work Order:** ENGINE-PACKAGING-001
- **GitHub Issue:** [#2](https://github.com/maff0000/forgev2/issues/2)
- **Parent PBI:** FV2-001
- **Governing FOUNDRY:** [`aee86185aac6aa0d2ab7a243138c423292af191a`](https://github.com/maff0000/foundry/tree/aee86185aac6aa0d2ab7a243138c423292af191a)
- **Project initiation:** [PIM v0.2](../PROJECT-INITIATION-MANDATE.md), Stage 1 CLOSED GREEN
- **Approved product direction:** `PRODUCT-VISION.md` and `PRODUCT-BACKLOG.md` at [`071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`](https://github.com/maff0000/forgev2/tree/071426b4cf2b39c39e6e6dd5be619e8afd06d8cb); Matt's exact-version approval is recorded in [Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6386137638).
- **Architect approval:** Not granted. CGPT must approve this exact committed artifact version through a traceable Issue #2 record before dispatch.
- **Delivery assignment:** None. The Orchestrator has not assigned a PL.

This draft is prepared under the [FOUNDRY Work Order contract](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/work-order-contract.md) and [secure engineering standard](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/secure-engineering.md). It describes a proposed bounded engine-development increment; it does not authorize implementation, installation, deployment, or changes to ForgeV1.

## 1. Intended outcome

Package the inherited and proven ForgeV1 Project Lead (PL), Engineer, Auditor, and associated skills as a portable, versioned Claude Code plugin. Preserve successful ForgeV1 startup, PID, delivery, Git-authority, independence, and real-browser assurance behavior while making plugin resources resolve from the plugin itself and allowing the PL to operate on a separately identified application repository.

One WO is one bounded ForgeV2 delivery cycle; FV2-001 may be delivered by multiple separately approved WOs. This is ForgeV2 engine-source development, not an application Work Order or a ForgeV2 release. The inherited source lineage is the ForgeV1 import at `665b32c991caaace95710abd22af6d4c97eefc3b`; verify the relevant objects and paths in the approved ForgeV2 baseline. It is compatibility input, not authority to change the operational `maff0000/forge` repository or installation.

## 2. Authority and approved context

- Matt retains product direction, priority, material product-risk acceptance, and final product acceptance. The approved FV2-001 direction and exact-version provenance above apply.
- CGPT is the Project Architect and must approve this exact Work Order version before any delivery dispatch. New dependencies and architectural exceptions also require CGPT approval; material risk acceptance beyond architectural authority goes to Matt.
- The Orchestrator must assign the approved WO to a named PL. Rogue is Matt's Orchestrator implementation, not the PL. No Orchestrator or ForgeV2 PL runtime is claimed to exist yet.
- The PL controls all Git/GitHub mutation within the authorized WO branch. Engineer, Auditor, Tester, and DevSecOps do not commit, push, create branches, or mutate GitHub.
- The PL owns the persistent per-specialist execution record for this WO. These are documentary operating requirements, not implemented enforcement.

Issue #2 establishes the request and traceability, not approval. Approval requires an explicit CGPT decision identifying this file and the immutable commit that already contains the reviewed content. The approval record must be made after that commit exists; no self-referential commit SHA is to be written into this file. Any subsequent content change requires a new artifact version and renewed approval.

## 3. Repository and workspace boundary

| Item | Authorized identity or boundary | Required entry verification |
| --- | --- | --- |
| Target repository | `maff0000/forgev2` | Verify the GitHub identity, configured remote, and repository access. |
| Starting baseline | Commit `5e6d5d6ce7d369e64b8d4f2078acfeb6feee6822` on the approved `main` lineage | Verify current remote `main` and its ancestry. If it has moved, stop for a revised Architect-approved baseline; do not silently retarget this WO. |
| Canonical engine-source checkout | `/srv/src/forgev2/main/` | Verify on the approved development environment; do not infer that a prior report proves current state. Keep it unchanged during implementation. |
| WO branch | `work/engine-packaging-001` | PL creates and controls this branch from the verified baseline only after all entry gates pass. No writes to `main`. |
| Authorized engine-source worktree | `/srv/src/forgev2/worktrees/engine-packaging-001/` | PL creates it explicitly from the target ForgeV2 repository and verifies branch, HEAD, clean state, and Git lineage before dispatch. Do not use Claude automatic worktree isolation for this cross-repository/hub arrangement. |
| Protected engine installation | `/srv/forgev2/` | Must remain outside all write paths. This WO does not install, update, or execute an installed ForgeV2 engine. |
| PACMAN application root | `/srv/pacman/` | Must remain untouched. No PACMAN files or worktrees are in scope. |
| Disposable test application | A separately identified and approved test-project repository and isolated project root; identity and actual location are not yet established | See blocking prerequisite in §5. Do not create or assume a repository, host, path, PID, Issue, branch, or credentials. |

These are project-specific approved layout decisions, not FOUNDRY-wide defaults. The actual host/workspace identity and present availability must be verified and recorded in the private or otherwise approved delivery evidence before work. This public Work Order intentionally omits hostnames, addresses, SSH aliases, access details, and sensitive operational evidence. No application write, log, build, dependency, test, or asset path may enter the protected engine installation. No unapproved filesystem/repository overlap is permitted.

The authorized Git push target, after Architect approval and Orchestrator assignment, is only the PL-controlled `work/engine-packaging-001` branch in `maff0000/forgev2`. The PL must verify the configured destination and SSH identity using existing authorized access; do not hard-code an SSH alias or change credentials. Specialists have no Git/GitHub write authority.

## 4. Scope

The PL may authorize changes only on the WO branch, within these paths:

- A self-contained Claude Code plugin package under `plugin/`, including its manifest, namespaced PL/Engineer/Auditor definitions, skills, and required plugin-owned resources/scripts.
- `tests/engine-packaging-001/` for bounded package-level validation that does not modify the operational ForgeV1 system or the disposable application's repository.
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
10. Validate the package with the approved, assessed CLI (including `claude plugin validate .` from the plugin root) and provide reproducible evidence from a separately governed disposable test application. The fixture must have its own verified repository identity, PID/startup context, and approved scope. Exercise plugin discovery/loading without installing or deploying the engine, namespaced agent availability, plugin-relative paths from a different project root, startup/PID boundaries, and correct project-owned sibling worktree routing. Exercise a user-visible behavior in a real browser under independent Tester assessment; Auditor browser checks remain mandatory wherever its existing gate applies.
11. Keep engine source, any eventual installation, and application/test-project workspaces isolated. This Work Order produces source and evidence only; it does not promote or release a plugin into `/srv/forgev2/`.
12. Identify each reviewed candidate by its exact Git commit SHA and clean tree. Auditor, Tester, and DevSecOps evidence must each identify the same unchanged candidate. Any Engineer modification invalidates prior reviewer PASS results and restarts the required assurance sequence.

## 5. Blocking prerequisites and unresolved design decisions

The following are not established by the repository baseline and must be resolved and evidenced before CGPT can approve this Work Order for dispatch. A missing prerequisite is **BLOCKED + specific reason + evidence**, never an inferred pass.

1. **Bootstrap authority and role coverage — CGPT decision required.** ForgeV2 has no implemented Orchestrator, installed ForgeV2 PL, Tester, or DevSecOps role. Proposed bounded arrangement: Rogue/manual Orchestrator coordination assigns one existing ForgeV1 PL-capable session to control the ForgeV2 WO branch; that PL uses the unchanged ForgeV1 PL/Engineer/Auditor doctrine as the bootstrap capability. CGPT must explicitly appoint independent Auditor, Tester, and DevSecOps reviewers for this candidate. The existing ForgeV1 Auditor may fill Auditor if its independence and context separation are evidenced; qualified external human/reviewer sessions may fill missing roles if CGPT approves their competence, independence, scope, and evidence contract. Do not represent these temporary reviewers as implemented ForgeV2 agents. If independent required assessments cannot be provided, do not waive or silently skip them; dispatch is BLOCKED.
2. **Disposable test-application identity — Matt/CGPT decision required.** No separately governed test-application repository, approved test PID, Issue, or workspace is identified in the current project records. Approve and provide that fixture's exact repository, baseline, PID/authority, and isolated location before the final WO approval. Creating a test repository or application is not implicitly authorized by this draft. Without it, the required disposable application and real-browser evidence cannot be produced responsibly.
3. **Current development workspace — PL verification required.** Previously recorded workspace evidence is historical and does not establish current host availability, identity, checkout cleanliness, branch state, worktree absence, or exact baseline. Reverify the approved environment, project root, engine boundary, and exact main lineage at dispatch. If unavailable or divergent, stop; do not substitute a local Mac, different host, or guessed path.
4. **Claude Code CLI — CGPT approval required.** Pin the exact CLI version and assess its source/provenance, license, and suitability before validation or plugin execution. The earlier loading spike's reported CLI version is not an approved current pin. Do not install or update a CLI under this WO.
5. **Plugin identity/version — CGPT decision required.** Approve the plugin identifier and initial version before packaging. They must not be silently inferred from this WO title.
6. **Existing inventory coverage — PL/security reviewer assessment required.** The current ForgeV2 external-code register reports incomplete coverage. Inspect and record the scope and gaps relevant to packaging and test execution. Do not execute unassessed inherited or external code; if required provenance cannot be established, stop for CGPT/security decision.

These decisions do not change the approved product direction. They are prerequisites for an executable, assurance-complete WO, not permission to implement any missing ForgeV2 capability as part of this package.

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

1. From the plugin root, `claude plugin validate .` and the approved load command pass with the exact approved CLI version; the commands, version, and output are preserved.
2. PL, Engineer, and Auditor are discoverable under the approved plugin namespace, and their instructions/resources load from plugin-owned paths when invoked from the separately governed test project.
3. Startup/PID and authority behavior remains intact: the existing gate is preserved; missing or invalid project authority blocks dispatch; PIM, PID, and WO remain distinct; and no approved WO means no implementation authority.
4. Only the PL performs Git/GitHub operations. Before any specialist dispatch, the PL demonstrates that the assigned worktree belongs to the test project’s verified repository and expected history, not merely that it is a clean worktree. Branch, baseline, remote identity, and path boundaries are recorded.
5. Plugin operation does not write to or alter the protected engine installation, canonical main checkout, operational ForgeV1, or unrelated project paths. Before/after Git and filesystem evidence identifies the candidate and verifies those boundaries without publishing sensitive host details.
6. The test application’s named user-visible acceptance behavior passes independent Tester verification in a real browser, with replayable steps and evidence. The Auditor independently performs all applicable ForgeV1 checks, including its real-browser gate when its PID conditions apply. If a browser assessment is judged inapplicable, CGPT must approve a specific evidence-based rationale before dispatch; it cannot be silently omitted.
7. Independent assurance follows Engineer → Auditor → Tester → DevSecOps. Each reviewer reports PASS or FAIL, reason, evidence locations, reviewer identity, and exact candidate SHA. FAIL findings route through the PL to Engineer correction or escalation. Every applicable reviewer returns PASS on the same unchanged candidate before completion.
8. The execution record is persisted by the PL per specialist for this WO: maximum four executions each, including the first; fifth prohibited; counts survive restart/context reset; no reset or replacement WO bypass; exhaustion is FAIL with reason and evidence. No technical enforcement is claimed.
9. Reuse-first and Security by Design requirements are evidenced. Every copied/vendor component and executable dependency in scope is assessed and recorded with verified provenance, exact version/hash, location, consumer, purpose, license, security/approval evidence, and truthful inventory coverage. Unapproved material is not trusted or executed; no externally hosted executable is introduced.
10. Changes are limited to the approved scope, existing ForgeV1 behavior is preserved, and `security/EXTERNAL_CODE_REGISTER.yaml` accurately states the inspected coverage and remaining gaps. No placeholder/fabricated inventory data is added.
11. Final evidence identifies the starting baseline, changed paths, candidate commit SHA, clean working tree, test commands/results, external-code assessment, reviewer PASS records, and limitations. Any Engineer change creates a new candidate and restarts required assurance.
12. The PL returns a completion report through the Orchestrator to CGPT. CGPT performs architectural acceptance; Matt retains product acceptance. No merge or engine installation/deployment is included.

## 8. Communications, logs, and execution bounds

Use [Issue #2](https://github.com/maff0000/forgev2/issues/2) for WO status and sanitized evidence links. It is not itself approval. Keep role records in the project repository at `work-orders/logs/ENGINE-PACKAGING-001/`, subject to entry verification and public-safe content:

| Record | Writer | Readers and purpose |
| --- | --- | --- |
| `PL.md` | Assigned PL only | Orchestrator and CGPT; authoritative progress, prerequisite decisions, branch/worktree identity, specialist counters, dispatches, candidate SHA, escalations, and final aggregate report. |
| `ENGINEER.md` | Assigned Engineer only | PL; bounded implementation actions, commands, changed paths, test results, and escalation. |
| `AUDITOR.md` | Independent Auditor only | PL and CGPT; independent findings and PASS/FAIL tied to exact candidate. |
| `TESTER.md` | Independent Tester only | PL and CGPT; functional/browser test procedure, observations, artifacts, and PASS/FAIL tied to exact candidate. |
| `DEVSECOPS.md` | Independent DevSecOps reviewer only | PL and CGPT; provenance, dependency, trust-boundary, security evidence, findings, and PASS/FAIL tied to exact candidate. |

The PL verifies actual writable locations and access before dispatch. Do not put credentials, host-specific access configuration, private security evidence, or sensitive data in these public-repository logs; retain restricted evidence only in an approved location and reference it without disclosure. Each specialist receives only the approved WO and the context needed for that role.

Each specialist has an independent maximum of four executions for this WO, counting its first invocation. A fifth is prohibited. Counts persist across restarts and context resets. The specialist checks its own limit; the PL's durable `PL.md` record is authoritative. No counter reset or replacement WO may bypass exhaustion. Exhaustion is FAIL with reason and evidence. Only Engineer escalates an execution failure to the PL. Material architectural ambiguity goes to CGPT; product direction, priority, or material product risk goes through the Orchestrator to Matt. No role may expand scope by interpretation.

Progress reports are event-driven and concise: dispatch, verified gate result, material finding/blocker, candidate change, each assurance result, and completion. On any failed entry condition, wrong repository/worktree, changed baseline, unassessed dependency, missing approval/reviewer, candidate mismatch, or unsafe boundary, the PL records **BLOCKED + reason + evidence** and stops affected work. No reviewer gate may be silently skipped.

## 9. Evidence and candidate acceptance

Store sanitized, reproducible evidence under `docs/evidence/ENGINE-PACKAGING-001/`, including:

- Exact CLI version and plugin validator output.
- Plugin discovery/loading and namespaced-role checks.
- Test fixture identity and baseline, PID/startup-gate evidence, and disposable-application test result.
- Worktree repository/branch/lineage checks and before/after boundary evidence.
- Reuse and security/dependency review, register coverage statement, and explicit approvals.
- Functional/browser evidence and the separate Auditor, Tester, and DevSecOps reports.
- Starting and candidate SHAs, changed paths, clean-tree evidence, and completion report.

Evidence must be reproducible where practicable and must distinguish verified facts, inference, and unknowns. Redact operational details that are not suitable for this public repository. The candidate identity is the exact Git commit SHA plus a verified clean working tree; reviewers must independently confirm they assessed that same commit. Any source change invalidates earlier PASS reports.

## 10. Proposed bootstrap delivery arrangement

Because the ForgeV2 Orchestrator and installed PL/specialist chain do not yet exist, a one-time manual bootstrap can be considered only with explicit CGPT approval in the exact Work Order approval record: Rogue/manual Orchestrator coordinates one existing ForgeV1 PL-capable session against the verified ForgeV2 engine-source worktree; that PL dispatches the unchanged ForgeV1 Engineer and Auditor capabilities; independently appointed qualified Reviewer sessions or people provide Tester and DevSecOps assessments; and the PL records the four-execution limits durably by hand. No temporary reviewer is represented as a shipped ForgeV2 role, and no missing capability or assurance gate is waived. PL retains Git control and all reviewer independence requirements apply to the exact candidate.

This proposal is not approved authority. If CGPT cannot identify an independent reviewer for every applicable assessment, or the separate test application and its PID/repository are not approved, the WO remains BLOCKED. The arrangement must also avoid loading unassessed source or relying on a root session as an enforceable security boundary.

## 11. Completion and stop

The WO cycle completes only after all entry gates, acceptance criteria, and applicable independent assurance pass on one unchanged candidate, the PL's completion evidence is returned through the Orchestrator, and CGPT accepts the result. A failed or missing gate is not a pass. An unresolved architectural ambiguity returns to CGPT; product-authority decisions return to Matt. Stop after the candidate and evidence are submitted for acceptance.

This draft authorizes no dispatch. Even after exact-version approval, this Work Order does not authorize merging, ForgeV2 installation/release, host changes, PACMAN work, or any excluded capability above.
