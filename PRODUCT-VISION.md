# ForgeV2 — Product Vision

**Draft:** v0.2 · 2026-10-24 · **Route:** EXISTING initiation reconciliation · **Status:** CANDIDATE — Matt's exact-version approval not yet recorded

**Product Owner:** Matt Scott. **Architect:** CGPT. **Governing framework:** [FOUNDRY](https://github.com/maff0000/foundry) at `aee86185aac6aa0d2ab7a243138c423292af191a`.

## Opportunity and beneficiaries

Matt has many software ideas but cannot sustainably act as the human development manager for every coding agent. ForgeV1 demonstrated that a disciplined Claude Code Project Lead, bounded Engineers, independent Auditor, real-browser scrutiny and Git evidence can deliver reliably. ForgeV2 builds on that proven capability to make delivery portable across independent projects and internal team machines, with FOUNDRY retaining project initiation and architectural governance.

The beneficiaries are Matt (product decisions and ownership), CGPT (architecture and acceptance), internal engineers (reproducible setup) and PL/specialist agents (small, reliable contracts). This system is for Matt's team, not a commercial product or external multi-tenant service.

## Product Goal

**Enable an approved project Work Order to be implemented, independently audited, functionally tested and security-reviewed, then returned as a reproducible GitHub delivery candidate—without a specialist gaining Git authority, an uncontrolled retry loop or any application WO modifying the ForgeV2 engine.**

## Value and outcomes

- Matt concentrates on vision, priorities, risk and acceptance rather than repetitive coding-agent management.
- The Project Lead retains ForgeV1's effective repository truth, engineering decomposition, independent evidence and Git control.
- The Orchestrator can coordinate independent PL sessions across projects without consuming a single giant context window.
- Every specialist receives minimum sufficient WO context, suitable skills and the relevant reuse-first/secure engineering rules.
- Engineer → Auditor → Tester → DevSecOps checks are independent, explicit PASS/FAIL with reasons and candidate identity; corrections restart assurance, and a fifth execution per specialist per WO is prohibited.
- Each application owns its repository, main checkout, sibling worktrees, functions, GUI components/CSS, dependencies, logs, test evidence and runtime. The installed engine is protected and versioned independently.
- Local, provenance-verified third-party code is governed and documented; no uncontrolled runtime CDN execution.
- An engineer can install ForgeV2 on a separate machine and use it against their own project without access to Matt's systems.

## Observable success indicators

1. A clean internal installation can discover and load a versioned ForgeV2 agent package, while the engine's tracked files and content hashes remain unchanged across application delivery.
2. A PL refuses a wrong repository, missing WO approval, invalid project/engine boundary, exhausted attempt count or unavailable evidence with an attributable BLOCKED/FAIL result.
3. An independently approved WO produces traceable evidence from all applicable assurance roles against the same unchanged candidate, plus PL-controlled Git/PR history.
4. Real-browser user behaviour is genuinely exercised for applicable usable/polished interfaces; a deliberately faulty case is detected rather than vacuously reported GREEN.
5. The PACMAN pilot is a playable, visually coherent browser application delivered through the accepted workflow in its own project, with reuse of components/design tokens and no application files written under the ForgeV2 installation.
6. The complete process can be reconstructed after agent context loss from project records, Issue/WO evidence and repository state.

No numerical delivery-time, success-rate or cost improvement baseline has yet been established. The `ENGINE-LOADING-SPIKE-001` experimental cost was approximately USD 0.25 for three headless sessions as reported by Claude; this is not a production cost forecast.

## Scope and constraints

**In scope:** Packaging reusable ForgeV2 roles/skills; FOUNDRY PIM and approved WO intake; PL project/worktree verification; Orchestrator→PL handoff; Engineer, Auditor, Tester and DevSecOps role contracts; bounded correction and persisted counts; candidate/evidence communication; secure dependency governance; independent real-browser verification; controlled engine release and team setup instructions; controlled PACMAN pilot.

**Out of scope:** Changes to operational ForgeV1; automatic authority expansion or merges; specialists writing Git/GitHub; copying engine source into application repositories; unrestricted multiple PLs inside one project; a commercial product; a new queue/daemon/dashboard without a demonstrated need; arbitrary external executable/CDN code; unbounded loops.

**Material constraints:** Use established Agile semantics through FOUNDRY. Preserve ForgeV1's PL and browser-verification strengths. Prefer existing Claude capabilities before custom machinery. Four executions maximum per specialist/WO, including the initial one. PL owns all authorised Git operations. Infrastructure is discovered per deployment, not globally fixed. ForgeV2 delivery should eventually use a non-root identity or equivalent enforceable engine isolation; root remains an administrative bootstrap context. Pin reviewed engine/Claude releases and review upgrades separately. The project security register must reflect actual coverage and approvals.

## Evidence and uncertainties

- **VERIFIED:** [`forgev2`](https://github.com/maff0000/forgev2) is inherited ForgeV1 baseline at `665b32c991caaace95710abd22af6d4c97eefc3b`; ForgeV1 has PL/Engineer/Auditor Markdown definitions and prior self-test evidence. This does not prove ForgeV2 features.
- **REPORTED experimental evidence:** `ENGINE-LOADING-SPIKE-001` established nine PASS-labelled checks for a dummy Claude plugin and dummy application, including namespaced agents, project-correct explicit worktrees, tool-level denies and unchanged dummy engine. Full evidence is ephemeral on the VPS; independent replay and durable evidence promotion remain pending.
- **KNOWN conflict:** Claude's automatic worktrees are located under `main/.claude/worktrees`, whereas FOUNDRY uses separate project `worktrees/`. Preferred initial strategy is explicit PL worktree creation, pending V2 acceptance tests.
- **UNPROVEN:** Full role sequence; Orchestrator launching PL; technical exclusion of Git/GitHub operations by specialists; protection from a root process; same-project parallel PL safety; a portable installation and controlled version upgrade.
- **DEPLOYMENT:** An experimental environment was reported, but its full security readiness is not approved. Specific host identities, access details and findings are retained as restricted operational evidence outside this project candidate. Before credentials or real delivery workloads, a separately accountable security gate must be evidenced. Engine installation and actual source-development workspace are not yet created/verified.

## Approval and evolution

Matt approved the **direction to document and initiate** ForgeV2 on 2026-10-24 in conversation. This document is a review candidate, not an approved exact GitHub version. Matt must approve the committed Product Vision and initial Product Backlog by immutable references; CGPT's critical review is separate. Future product-direction changes require traceable authority, and inclusion in the Backlog does not authorise engineering.
