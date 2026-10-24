# ForgeV2 — Project Initiation Mandate

**Record:** FORGEV2-INIT-001 · **Route:** EXISTING · **Revision:** v0.2 (accepted), 2026-10-24 · **Author:** CGPT Project Architect · **Stage 1 status:** CLOSED GREEN by CGPT at exact baseline `28d69381355eb6979b302d36cc71320f55e8b56f`; [acceptance is recorded in Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6387428447).

**Governing FOUNDRY revision used for this initiation:** [`aee86185aac6aa0d2ab7a243138c423292af191a`](https://github.com/maff0000/foundry/commit/aee86185aac6aa0d2ab7a243138c423292af191a), including FND-044 engine/application isolation. This identifies the verified framework baseline used at initiation, not a claim about a later `main` head. Matt authorised preparation of initiation records; that authority did not itself approve those records or authorise ForgeV2 implementation.

**Current status:** FOUNDRY Stage 1 is **CLOSED GREEN** at the exact baseline above. CGPT's acceptance comment records that all Stage 1 exit criteria are satisfied and identifies mandatory downstream delivery gates. Product direction remains approved: Matt approved the Product Vision and Product Backlog at exact commit [`071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`](https://github.com/maff0000/forgev2/commit/071426b4cf2b39c39e6e6dd5be619e8afd06d8cb), as recorded in [Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6386137638). Those immutable artifacts retain their status text from when they were written; the later approval applies to those exact versions. No ForgeV2 engineering implementation has started, and no engineering Work Order has been approved. Stage 1 closure does **not** authorise implementation.

## Purpose and current truth

ForgeV2 is the next, portable version of Matt's internal AI engineering delivery system. It evolves the independently proven ForgeV1 Project Lead and Engineer/Auditor practices into FOUNDRY-governed, bounded Work Order delivery with an Orchestrator, independent Tester and DevSecOps, and project-specific evidence. It must let a team member deploy their own engine without access to Matt's private systems. This is an internal engineering capability, not a commercial product.

**Existing code:** The initial [`maff0000/forgev2`](https://github.com/maff0000/forgev2) import baseline was `665b32c991caaace95710abd22af6d4c97eefc3b`, an inherited 26-commit ForgeV1 baseline, **not a functioning ForgeV2 release**. At closure-candidate preparation, GitHub `main` and the canonical source checkout were independently verified at `6da78603478093ff799a2aa70c83a6fdc0d328c3` after a controlled fast-forward. Operational ForgeV1 at `maff0000/forge` is separately protected. The inherited `PID.md`, original `.claude/` roles, PL doctrine, tests and evidence remain historical/compatibility input, not silently rewritten into new authority.

**Project record state:** The Product Vision and initial Product Backlog are approved at the exact version above. The README, this PIM and initiation evidence are preserved in the repository. CGPT accepted Stage 1 CLOSED GREEN at exact baseline `28d69381355eb6979b302d36cc71320f55e8b56f` in [Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6387428447). The external-code register exists and truthfully reports incomplete coverage. No engineering Work Order has been approved. Project-specific records belong in this repository, not in FOUNDRY.

## Product direction

**Product Goal:** A lean, reproducible AI-first delivery engine that takes an Architect-approved, project-specific Work Order through implementation, independent engineering audit, functional/user testing, security assessment and PL-controlled Git delivery, with a bounded corrective loop and verifiable evidence, without allowing application delivery to change its own engine.

**Beneficiaries:** Matt as Product Owner; CGPT as Architect; internal engineers and independent AI agents collaborating on separate, team-owned projects. The engine must not depend on Matt's personal Rogue installation or network.

**Intended outcomes:** Preserve ForgeV1's effective PL; reduce Matt's implementation supervision; keep specialists' context small; produce usable, attractive applications using reuse-first functions/components/CSS and approved local dependencies; prevent unbounded retries, cross-project contamination, unsupported green verdicts and ungoverned Git activity. The planned first external validation is a browser-playable PACMAN web application, governed in its own future repository and project root.

**Scope:** A reusable Claude Code plugin/agent delivery capability; portable Orchestrator and PL roles; specialist Engineer, Auditor, Tester and DevSecOps; exact-PIM/WO intake gates; independent reviewer evidence on a common candidate; four-execution-per-specialist-per-WO limit; project-root Work Order logs/counters; explicit project-owned worktrees; GitHub Issue/branch/PR communication; least-privilege, locally governed dependency use; portable setup instructions and an end-to-end pilot.

**Exclusions:** Modifying operational ForgeV1; shipping a public/commercial SaaS; rebuilding Agile or inventing workflow services without demonstrated need; creating PACMAN application files inside ForgeV2; allowing specialists to modify Git/GitHub; automatic merges; blanket same-project PL concurrency; runtime external code/CDN dependencies without approved exception; treating a successful packaging experiment as a production release.

## Evidence, environment and isolation

- **VERIFIED baseline at the time of reconciliation:** GitHub ForgeV2 `main` was `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`; GitHub FOUNDRY `main` was `aee86185aac6aa0d2ab7a243138c423292af191a`; Issue #1 was open. These SHAs record the baseline checked then, not a claim about a later `main` head. Matt's approval applies to the Product Vision and Product Backlog at the exact ForgeV2 commit `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`; the current environment reconciliation remains a review candidate.
- **APPROVED environment architecture:** ForgeV2 source development is rooted at `/srv/src/forgev2/`, with canonical source checkout `/srv/src/forgev2/main/` and engine-development worktrees under `/srv/src/forgev2/worktrees/`. The protected engine installation is `/srv/forgev2/`. PACMAN owns the independent application root `/srv/pacman/`. These are deployment-specific decisions, not FOUNDRY-wide path defaults. Network perimeter security is managed by the infrastructure provider; no host firewall installation is required.
- **VERIFIED by Codex:** The authorized canonical workspace was independently checked at the expected starting SHA, its repository and branch identity were confirmed, it was clean, and only the canonical checkout was registered as a Git worktree. Codex then completed the controlled fast-forward to the verified GitHub `main` SHA `6da78603478093ff799a2aa70c83a6fdc0d328c3`. See [STAGE1-ENVIRONMENT-RECONCILIATION-001](docs/evidence/STAGE1-ENVIRONMENT-RECONCILIATION-001.md); host-specific identity and access details are omitted.
- **REPORTED by Claude, not independently verified:** No delivery account or GitHub write credentials were available in the workspace at the time of Claude's report. Their current readiness remains **PENDING**, as does host-security acceptance. The approved provider-managed network perimeter and absence of a host-firewall installation requirement do not establish readiness for credentials or real delivery workloads.
- **REPORTED by Claude's spike, not independently replayed by CGPT:** `ENGINE-LOADING-SPIKE-001` ran nine PASS-labelled checks in a temporary directory, demonstrating plugin loading, main agent and specialist dispatch, explicit application worktree operation, tool-level engine write denials and unchanged dummy-engine contents. Automatic Claude worktrees were observed under `main/.claude/worktrees/`, conflicting with the intended sibling worktree topology. This was a disposable experiment, not ForgeV2 production assurance; details are in `docs/evidence/ENGINE-LOADING-SPIKE-001.md`.

Project host, address, paths, branch and access are **deployment facts**, not reusable FOUNDRY defaults. A WO must verify its actual application root, Git lineage, engine release identity and non-overlap independently. Engine source-development and release promotion are separate authorised activities; an application WO cannot modify `/srv/forgev2/`.

## Security and engineering context

Trust boundaries are Matt/CGPT approval → Orchestrator → PL's authorised project Git operations → bounded specialists; engine installation → application workspace; local/externally sourced executable code → approved incorporation; repository/Issue evidence → human acceptance. A read-only engine plugin plus Claude tool denials is useful but **not an OS security boundary when agents execute as root**. Actual delivery protection requires a restricted runtime identity or equivalent enforced isolation, plus verified path/lineage checks and before/after engine identity evidence.

Each governed application owns its source, functions, GUI components, design tokens/CSS, external-code register and runtime. ForgeV2 must not add project-specific files to its installation. External dependencies require exact provenance, licence and vulnerability/security review, controlled local execution and a truthful project-level register. ForgeV2's own existing external-code inventory is not yet fully inspected; see `security/EXTERNAL_CODE_REGISTER.yaml`.

**Material risks:** ForgeV1 hub/worktree wrong-repository hazard; loss of V1 PL/browser assurance during packaging; privileged session ability to bypass tool policies; automatic worktree path conflict; as-yet-untested Orchestrator→PL launch; unsupported claims of same-project parallel PL safety; token/cost escalation; Claude version drift; deployment-security readiness and credential scoping. Each must be addressed or explicitly deferred with accountable evidence before relevant acceptance. Detailed operational findings remain restricted rather than published in a project repository.

## Bounded initiation authority

This mandate authorises **documentation and reconciliation only**, through a separately authorised Codex/PL assignment:

1. Verify exact repository/current baseline and preserve inherited V1 files and history.
2. Verify that [initiation GitHub Issue #1](https://github.com/maff0000/forgev2/issues/1) is OPEN, matches FORGEV2-INIT-001 authority and scope, and identifies the expected starting baseline **before substantive scaffolding**. Stop if it no longer does.
3. Place this Architect-authored PIM and the corresponding candidate Product Vision, Product Backlog, truthful external-code register and spike evidence into the ForgeV2 repository, with minimal README navigation reconciliation.
4. Distinguish design-target decisions from implemented facts. Prepare, but do not dispatch, later Work Orders.
5. Verify links, Markdown, YAML syntax, diff scope, baseline ancestry, unchanged V1 behaviour and absence of secrets.
6. Recheck the proposed diff for host-specific security disclosures before writing to the currently public repository. Commit/push a review branch, return exact candidate SHA and Issue/compare links. **No merge, agent implementation, host provisioning, engine installation or product release.**

The Mac Codex staging operator may be separately authorised for Git writes during initiation. ForgeV2 specialist agents will not receive Git/GitHub authority. PL and Orchestrator runtime roles are not yet implemented. Failed access, missing Issue, unexpected repository baseline or unsafe disclosures are STOP/BLOCKED conditions.

## Review and exit

### Stage 1 exit-gate assessment at the accepted baseline

The table records the closure assessment at baseline `28d69381355eb6979b302d36cc71320f55e8b56f` under [FOUNDRY Stage 1](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/stages/01-product-discovery.md#exit-gate) and the [product record standard](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/product-records.md). Its “closure review pending” labels describe the pre-acceptance assessment. CGPT subsequently accepted all FOUNDRY Stage 1 exit criteria as satisfied in the [Issue #1 closure comment](https://github.com/maff0000/forgev2/issues/1#issuecomment-6387428447).

| FOUNDRY exit criterion | Status at pre-acceptance assessment | Evidence |
| --- | --- | --- |
| 1. Problem or opportunity understood | MET | Product Vision, “Opportunity and beneficiaries,” approved at exact commit `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`. |
| 2. Intended product value clear | MET | Product Vision, “Value and outcomes,” same approved commit. |
| 3. Product Goal exists | MET | Product Vision, “Product Goal,” same approved commit. |
| 4. Scope boundaries and material constraints recorded | MET | Product Vision, “Scope and constraints,” and PIM; same approved direction. |
| 5. Significant assumptions and risks visible | MET | Product Vision and PIM risks/uncertainties; detailed operational evidence remains private. |
| 6. Initial Product Backlog exists | MET | `PRODUCT-BACKLOG.md` at the approved commit contains candidate PBIs and definition states. |
| 7. Architect critical review completed | MET for product direction; CLOSURE REVIEW PENDING | Issue #1 approval comment records CGPT's PASS recommendation for the exact Product Vision/Backlog versions. CGPT must review this full closure assessment and remaining security evidence. |
| 8. No unresolved issue prevents responsible approval of product direction | MET for the approved direction; CLOSURE REVIEW PENDING | Matt approved the direction following CGPT's review. This does not resolve the distinct security and delivery-readiness gates below. |
| 9. Matt explicitly approved Product Vision and initial Product Backlog | MET | Explicit Product Owner approval in [Issue #1 comment](https://github.com/maff0000/forgev2/issues/1#issuecomment-6386137638). |
| 10. Approval identifies exact reviewed artifact versions | MET | Approval names `PRODUCT-VISION.md` and `PRODUCT-BACKLOG.md` at commit `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`. |
| 11. Approved records preserved in GitHub | MET | Exact approved commit is an ancestor of current `main`; both files remain byte-for-byte unchanged there. |

### Cross-cutting Stage 1 evidence and outstanding gates

- **Product security context:** Recorded in the approved Product Vision and this PIM, including trust boundaries, deployment assumptions, risks and external-code expectations. CGPT's later acceptance confirms the Stage 1 exit criteria were satisfied with the remaining delivery gates explicitly deferred.
- **External software register:** `security/EXTERNAL_CODE_REGISTER.yaml` exists and reports `coverage.status: incomplete`, with known gaps. Its inventory snapshot is based on ForgeV1 source import commit `665b32c991caaace95710abd22af6d4c97eefc3b`; the documentation-only sync did not perform a new dependency inventory. No complete coverage, SBOM, dependency approval, or supply-chain assessment is claimed. The closure comment defers assessment of unassessed components until before their execution; the incomplete inventory is not represented as complete.
- **Infrastructure and source availability:** Codex independently verified the authorized workspace and completed the controlled fast-forward. The sanitized evidence and exact resulting source baseline are in [STAGE1-ENVIRONMENT-RECONCILIATION-001](docs/evidence/STAGE1-ENVIRONMENT-RECONCILIATION-001.md). No host-specific access details are reproduced here.
- **Security readiness for real delivery:** PENDING. Real engineering workloads require a non-root delivery identity or equivalent enforceable engine protection, appropriately scoped credentials, and reviewed host-security evidence. The approved IONOS-managed network perimeter remains in force; no host-firewall installation is required. The read-only source verification does not establish runtime isolation or operational security acceptance.
- **Delivery authority:** No engineering Work Order is approved. Product direction approval and any eventual Stage 1 closure do not authorize implementation. A separate approved Work Order and applicable FOUNDRY process are required before engineering work.

**Formal closure record:** CGPT accepted FOUNDRY Stage 1 **CLOSED GREEN** at exact baseline `28d69381355eb6979b302d36cc71320f55e8b56f` in [Issue #1](https://github.com/maff0000/forgev2/issues/1#issuecomment-6387428447). This status update records that later acceptance without changing the approved Product Vision, Product Backlog or historical assessment evidence. No ForgeV2 engineering implementation has started; no engineering Work Order has been approved. Engineering implementation remains **NOT AUTHORISED** until a separate Work Order is approved and mandatory delivery gates are met.

Following accepted initiation, ForgeV2 engineering requires a separately versioned, approved WO under the FOUNDRY Work Order contract and Orchestrator→PL delegation. Candidate first engineering increment: plugin packaging preserving ForgeV1 PL/Engineer/Auditor behaviour; it is **not authorised by this PIM**. Unresolved Orchestrator launch, runtime isolation, version pinning, worktree routing and release-promotion mechanics remain explicit design work.
