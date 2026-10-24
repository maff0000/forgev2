# ForgeV2 — Initial Product Backlog

**Draft:** v0.1 · 2026-10-24 · **Status:** CANDIDATE; relative order proposed by CGPT, pending Matt's exact-version approval. A PBI is not a WO and provides no implementation authority.

The backlog is outcome-oriented and deliberately short. A separate approved, versioned WO will define the detailed deliverable, role context, checks, paths, evidence and limits for each engineering increment. FOUNDRY governs that refinement.

| PBI | Priority | Definition | Capability and intended value | Key dependencies and uncertainties |
| --- | --- | --- | --- | --- |
| FV2-001 | P0 | DEFINED | Package the proven ForgeV1 PL, Engineer, Auditor and skills into a locally loadable versioned ForgeV2 plugin without weakening existing contracts or real-browser assurance. | Preserve historical baseline; convert relative/script paths; repeat dummy plugin checks. No installed engine modification by application WOs. |
| FV2-002 | P0 | DEFINED | Establish project-correct, explicit PL-owned Git worktrees, protected engine identity, and a verified starting repository/workspace gate. | Need isolated engine release, runtime user/security decision, path and lineage tests; default automatic worktrees conflict with sibling layout. |
| FV2-003 | P0 | DEFINED | Require an exact Architect-approved WO and current project PIM/records before dispatch; reject missing/changed authority. | Implement FOUNDRY WO contract and approval evidence without breaking historical V1 PID expectations. |
| FV2-004 | P0 | DEFINED | Provide independent Tester and DevSecOps agent roles, retaining Auditor independence and real-browser non-vacuity. | Relevant skills; enforce role access; verify same-candidate PASSES and FAIL correction routing. |
| FV2-005 | P0 | DEFINED | Enforce bounded correction loops: each specialist up to four executions per WO, persisted by PL across restarts, with FAIL/reason on exhaustion. | Requires durable project-owned counters and non-bypassable WO identity; no invisible reset. |
| FV2-006 | P1 | PROVISIONAL | Provide portable Orchestrator→PL dispatch with fresh WO contexts and evidence return, supporting concurrent PLs on different projects. | Orchestrator→PL session launch not tested; same-project concurrency excluded pending independent coordination design. |
| FV2-007 | P1 | DEFINED | Record concise WO-specific role logs, GitHub Issue state, candidate/PR evidence and escalation without sending entire histories through agent contexts. | GitHub Issue/API write mechanism distinct from SSH deploy key; must be verified and scoped. |
| FV2-008 | P1 | DEFINED | Make secure/reuse-first engineering operational: functions, modules, UI components/design tokens, local vetted dependencies, provenance register, security and test skills. | Applicable FOUNDRY standards; role instructions need-to-know; external source code approval and disclosure. |
| FV2-009 | P1 | PROVISIONAL | Deliver portable team setup, pinned engine/Claude release identity and a safe, separately authorised upgrade path. | Choose source-development root; verify non-root runtime and credential isolation; determine release promotion mechanics. |
| FV2-010 | P1 | PROVISIONAL | Demonstrate complete ForgeV2 delivery using a separately governed playable PACMAN web application, with functional and visual user acceptance. | ForgeV2 release gate and separate PACMAN project/PIM/WOs; no code or worktrees under engine install. |
| FV2-011 | P2 | PLACEHOLDER | Improve multi-project coordination efficiency based on measured delivery experience without adding unnecessary services. | Data and repeated incidents required; never infer safe same-project PL concurrency or build queues by default. |

**Near-term architectural sequence:** Verify Stage 1 records and approved direction → prepare `ENGINE-PACKAGING-001` WO for FV2-001 → test packaging without deploying to `/srv` → progress through project/worktree, intake, assurance and loop controls → portable Orchestrator → PACMAN pilot. This is a proposed dependency order, not implementation authority.

**Priority authority:** Matt. **Architecture/refinement:** CGPT. Product Vision/backlog exact-version acceptance and Stage 1 closure are not yet recorded.
