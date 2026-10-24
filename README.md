# ForgeV2 — governed initiation candidate

ForgeV2 is Matt Scott's internal, portable AI software-delivery engine, evolving the proven ForgeV1 Project Lead and independent engineering audit into FOUNDRY-governed Work Order delivery with Tester and DevSecOps assurance, bounded retries and protected separation between the engine and each application project.

This documentation candidate is written for a currently public repository. It deliberately does **not** publish operator-specific host identities, access configuration or security findings. Those are maintained under restricted operational review; deployment security is not yet approved. A public-safe draft is not permission to release secrets or private infrastructure reports.

**Current verified state:** This repository's `main` inherits the ForgeV1 baseline at `665b32c991caaace95710abd22af6d4c97eefc3b`. **ForgeV2 roles, plugin packaging, enforcement and runtime are not implemented or accepted.** Initiation documents are review candidates until Matt and CGPT approve their exact committed versions. Operational ForgeV1 is a different repository and must not be changed by this initiation.

**Governing framework:** [FOUNDRY](https://github.com/maff0000/foundry) at `aee86185aac6aa0d2ab7a243138c423292af191a` (Stage 1 v0.4 and Amendments 001–005). FOUNDRY supplies role authority, product-record standards, secure engineering and Work Order gates; ForgeV2 supplies delivery capability once implemented.

## Authoritative project records

- [Project Initiation Mandate](PROJECT-INITIATION-MANDATE.md) — existing-project reconciliation, verified/pending environment, and **bounded initiation authority only**.
- [Product Vision](PRODUCT-VISION.md) — intended value, goal, constraints, risks and exact-version approval state.
- [Initial Product Backlog](PRODUCT-BACKLOG.md) — candidate capabilities and priorities, **not authorised Work Orders**.
- [ForgeV2 decisions](DECISIONS.md) — project-specific direction and clearly distinguished unimplemented mechanisms.
- [External software register](security/EXTERNAL_CODE_REGISTER.yaml) — incomplete baseline coverage, no invented approval.
- [Engine-loading experiment](docs/evidence/ENGINE-LOADING-SPIKE-001.md) — reported disposable experiment and its limits.

[Initiation GitHub Issue #1](https://github.com/maff0000/forgev2/issues/1) was verified OPEN against this assignment, scope and starting baseline before this candidate was prepared. This Stage 1 review branch carries the exact Issue reference; it does not authorize specialist dispatch or ForgeV2 implementation. **Do not run inherited ForgeV1 bootstrap scripts, install/upgrade the engine or merge without separate authority.**

## Engine/application separation

ForgeV2 is a tool used by other projects. Its eventual installed release and application workspaces must remain distinct. On the nominated VPS, `/srv/forgev2/` is the proposed protected engine installation; `/srv/pacman/main/` and `/srv/pacman/worktrees/` are the separately governed proposed PACMAN application paths. None existed at the latest read-only inventory. ForgeV2's **own code development** also requires a separately chosen, verified workspace, not implementation edits to its protected installed release. These are deployment examples, not global FOUNDRY defaults.

## Inherited ForgeV1 baseline (preserved)

The inherited source still contains:

- [`PID.md`](PID.md) — historical ForgeV1 self-governance and original PID gate. It is **not** the FOUNDRY PIM or an approved ForgeV2 WO.
- [`docs/FORGE-NORTH-STAR.md`](docs/FORGE-NORTH-STAR.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/OPERATING-MODEL.md`](docs/OPERATING-MODEL.md), [`docs/EVIDENCE-DOCTRINE.md`](docs/EVIDENCE-DOCTRINE.md) — proven V1 principles and recorded limits.
- [ForgeV1 PL skill](.claude/skills/forge/SKILL.md), [Engineer](.claude/agents/forge-engineer.md), [Auditor](.claude/agents/forge-auditor.md) — historical starting points for independently authorised V2 role packaging.
- [`ops/bootstrap`](ops/bootstrap), [`ops/pl-startup-gate`](ops/pl-startup-gate), [`self-test/`](self-test/) and committed Git hooks — inherited operational controls; no unreviewed execution or modification in Stage 1.

ForgeV1's original README documented its PID → PL → Engineer → Auditor loop and North Star. It treats Git as durable truth; Redis/fabric may carry live session messages but hold nothing durable. Its clone setup describes `./ops/bootstrap` verifying `gitleaks` and activating `scripts/hooks/pre-commit` through `core.hooksPath`; this initiation does not run that script. The README also rejects a local-model benchmark or delegation harness without a demonstrated need, because Claude-native Engineer/Auditor subagents already provide independent review ([anti-bloat doctrine](docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine)).

ForgeV1's design used a driving PL session and independent Engineer/Auditor subagents. ForgeV2 must retain its effective protections, including non-vacuous real-browser scrutiny, while explicitly repairing the wrong-repository worktree risk discovered in V1. The added Orchestrator, Tester and DevSecOps roles are **not yet implemented**.
