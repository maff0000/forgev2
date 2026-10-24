# ENGINE-LOADING-SPIKE-001 — initiation evidence

**Date:** 2026-10-24 · **Source:** Claude Code report supplied by Matt to CGPT · **Status:** REPORTED nine-test result, not independently replayed by CGPT · **Purpose:** Test external engine/application isolation before designing ForgeV2 packaging.

**Environment reported:** Debian 12 VPS, Claude Code 2.1.310, Git 2.39.5, root-run disposable experiment. Temporary evidence root `/tmp/forge-spike-57AzN7/`, vulnerable to host restart; raw evidence has not yet been promoted into GitHub and may be unavailable later. Three headless sessions cost approximately USD 0.25, according to Claude; no retries or permission-bypass mode.

| Test | Claude's verdict | Reported evidence and limits |
| --- | --- | --- |
| T1: Plugin structure | PASS | `claude plugin validate` exited 0 with non-blocking metadata warnings; disposable `.claude-plugin/plugin.json` and `agents/*.md`. |
| T2: External discovery | PASS | `--plugin-dir` discovered namespaced dummy plugin and agents. |
| T3: Main-session role | PASS | `--agent spikeengine:spike-lead` produced marker defined by agent file. |
| T4: Specialist dispatch | PASS | Agent tool accepted `subagent_type: spikeengine:spike-specialist` at depth 1. |
| T5: Correct repository | PASS | Launch from dummy application repo; specialist's `git rev-parse --show-toplevel` resolved the application, not the plugin. |
| T6: Explicit worktree | PASS | `git worktree add` created a sibling application worktree on a WO-style branch with correct lineage. |
| T7: Automatic worktree location | PASS for observed behaviour, **design conflict** | Claude's `isolation: worktree` created under `app/main/.claude/worktrees/` rather than `app/worktrees/`; automatic path violates FOUNDRY's intended sibling layout. No modified-worktree cleanup test. |
| T8: Tool-level deny | PASS for tested calls | Settings denied Edit, Write and a recognisable Bash redirect to dummy engine; controls outside engine succeeded. Did not attempt bypass via alternate interpreters or other commands. Root can bypass tool policy. |
| T9: Dummy engine unchanged | PASS | SHA-256 manifest and full content comparison reported all six dummy-engine files identical before/after; no additions or deletions. |

**Architect interpretation:** The plugin architecture is supported for a first ForgeV2 packaging candidate. The dummy experiment does **not** prove installed release integrity, enforceable OS isolation, non-root runtime operation, PL adaptation, Orchestrator→PL launch, full four-role assurance, hidden tool effects, cross-project concurrency or PACMAN delivery. It does identify a real automatic-worktree layout conflict and supports explicit PL-created worktrees.

**Next acceptance conditions:** Maintain a protected engine installation distinct from source-development and application roots; test non-root delivery or equivalent OS enforcement; verify plugin role/script path resolution from the application worktree; preserve ForgeV1 PL and browser assurance; pin runtime/release versions; replay the relevant checks against the actual package; keep GitHub Issue/WO evidence in project-owned records. Actual ForgeV2 implementation requires later approved Work Orders.
