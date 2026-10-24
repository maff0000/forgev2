# ForgeV2 — governed initiation candidate

ForgeV2 is Matt Scott's internal, portable AI software-delivery engine, evolving the proven ForgeV1 Project Lead and independent engineering audit into FOUNDRY-governed Work Order delivery with Tester and DevSecOps assurance, bounded retries and protected separation between the engine and each application project.

This documentation candidate is written for a currently public repository. It deliberately does **not** publish operator-specific host identities, access configuration or security findings. Those are maintained under restricted operational review; deployment security is not yet approved. A public-safe draft is not permission to release secrets or private infrastructure reports.

**Current status:** The ForgeV1 source import baseline verified when ForgeV2 initiation began was `665b32c991caaace95710abd22af6d4c97eefc3b`; this is historical baseline provenance, not a claim about the current `main` head. **ForgeV2 roles, plugin packaging, enforcement and runtime are not implemented or accepted.** Matt approved `PRODUCT-VISION.md` and `PRODUCT-BACKLOG.md` at exact commit [`071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`](https://github.com/maff0000/forgev2/commit/071426b4cf2b39c39e6e6dd5be619e8afd06d8cb), recorded in [Issue #1 approval comment](https://github.com/maff0000/forgev2/issues/1#issuecomment-6386137638). The environment reconciliation is a **review candidate**; Stage 1 closure is **PENDING**; engineering implementation is **NOT AUTHORISED**. Operational ForgeV1 is a different repository and must not be changed by this initiation.

**Governing framework:** [FOUNDRY](https://github.com/maff0000/foundry) at `aee86185aac6aa0d2ab7a243138c423292af191a` (Stage 1 v0.4 and Amendments 001–005). FOUNDRY supplies role authority, product-record standards, secure engineering and Work Order gates; ForgeV2 supplies delivery capability once implemented.

## Authoritative project records

- [Project Initiation Mandate](PROJECT-INITIATION-MANDATE.md) — existing-project reconciliation, verified/pending environment, and **bounded initiation authority only**.
- [Product Vision](PRODUCT-VISION.md) — approved at exact commit `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`.
- [Initial Product Backlog](PRODUCT-BACKLOG.md) — approved at exact commit `071426b4cf2b39c39e6e6dd5be619e8afd06d8cb`; its items are **not authorised Work Orders**.
- [ForgeV2 decisions](DECISIONS.md) — project-specific direction and clearly distinguished unimplemented mechanisms.
- [External software register](security/EXTERNAL_CODE_REGISTER.yaml) — incomplete baseline coverage, no invented approval.
- [Engine-loading experiment](docs/evidence/ENGINE-LOADING-SPIKE-001.md) — reported disposable experiment and its limits.
- [Stage 1 environment reconciliation](docs/evidence/STAGE1-ENVIRONMENT-RECONCILIATION-001.md) — approved workspace boundaries and attributed verification status.

[Initiation GitHub Issue #1](https://github.com/maff0000/forgev2/issues/1) was verified OPEN against this assignment, scope and starting baseline before this candidate was prepared. This Stage 1 review branch carries the exact Issue reference; it does not authorize specialist dispatch or ForgeV2 implementation. **Do not run inherited ForgeV1 bootstrap scripts, install/upgrade the engine or merge without separate authority.**

## Engine/application separation

ForgeV2 is a tool used by other projects. Its installed release and application workspaces remain distinct. The approved deployment layout places ForgeV2 source under `/srv/src/forgev2/`, with `/srv/src/forgev2/main/` as its canonical source checkout and `/srv/src/forgev2/worktrees/` reserved for engine-development worktrees. The protected engine installation is `/srv/forgev2/`; PACMAN owns the independent application root `/srv/pacman/`. These are deployment-specific decisions, not global FOUNDRY defaults. Claude reports that the source checkout and worktrees directory are present and that the protected engine and PACMAN locations were left untouched; this report has not been independently verified. Network perimeter security is managed by the infrastructure provider, and no host firewall installation is required. Environment and security readiness remain pending; see the [reconciliation evidence](docs/evidence/STAGE1-ENVIRONMENT-RECONCILIATION-001.md).

## Inherited ForgeV1 baseline (preserved)

The inherited source still contains:

- [`PID.md`](PID.md) — historical ForgeV1 self-governance and original PID gate. It is **not** the FOUNDRY PIM or an approved ForgeV2 WO.
- [`docs/FORGE-NORTH-STAR.md`](docs/FORGE-NORTH-STAR.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/OPERATING-MODEL.md`](docs/OPERATING-MODEL.md), [`docs/EVIDENCE-DOCTRINE.md`](docs/EVIDENCE-DOCTRINE.md) — proven V1 principles and recorded limits.
- [ForgeV1 PL skill](.claude/skills/forge/SKILL.md), [Engineer](.claude/agents/forge-engineer.md), [Auditor](.claude/agents/forge-auditor.md) — historical starting points for independently authorised V2 role packaging.
- [`ops/bootstrap`](ops/bootstrap), [`ops/pl-startup-gate`](ops/pl-startup-gate), [`self-test/`](self-test/) and committed Git hooks — inherited operational controls; no unreviewed execution or modification in Stage 1.

ForgeV1's original README documented its PID → PL → Engineer → Auditor loop and North Star. It treats Git as durable truth; Redis/fabric may carry live session messages but hold nothing durable. Its clone setup describes `./ops/bootstrap` verifying `gitleaks` and activating `scripts/hooks/pre-commit` through `core.hooksPath`; this initiation does not run that script. The README also rejects a local-model benchmark or delegation harness without a demonstrated need, because Claude-native Engineer/Auditor subagents already provide independent review ([anti-bloat doctrine](docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine)).

ForgeV1's design used a driving PL session and independent Engineer/Auditor subagents. ForgeV2 must retain its effective protections, including non-vacuous real-browser scrutiny, while explicitly repairing the wrong-repository worktree risk discovered in V1. The added Orchestrator, Tester and DevSecOps roles are **not yet implemented**.
