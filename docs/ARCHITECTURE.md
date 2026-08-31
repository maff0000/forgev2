# Architecture

Forge has three layers: doctrine (this `docs/` tree and `skills/forge/SKILL.md`),
subagent definitions (`.claude/agents/forge-engineer.md`,
`.claude/agents/forge-auditor.md`), and the PL itself — which is not a
separate process, it is whichever Claude Code session is driving a given PID
under this doctrine.

There is no orchestration runtime, no queue, no daemon, and no database.
Dispatch is a direct Claude Code `Agent` tool call; the message bus is the
tool call's return value.

## The PL startup gate

Before any of the mechanics below run, the PL verifies a PID, a git
repository, and a GitHub remote all exist for the project — a hard
refuse-to-proceed check, not an assumption baked into step 1. Full doctrine
in `skills/forge/SKILL.md#0-pl-startup-gate--verify-before-touching-anything`;
the runnable check is `ops/pl-startup-gate`, which depends on nothing but
`git` so it works identically whether the PL is this household's Claude
Code, Trinity acting as PL-sponsor, or a human engineer running Forge cold
on their own machine against a project Forge has never seen. A missing
piece is a product-authority gap the PL hands back, never one it papers
over.

## How "the PL owns Git" is enforced

Not by a custom isolated-clone tool. `Agent` calls made with
`isolation: "worktree"` already give an Engineer dispatch its own clean git
worktree. The contract layered on top, stated in
`.claude/agents/forge-engineer.md`, is simple: **the Engineer never runs
`git commit`.** It produces a diff in its own worktree and reports back. The
PL inspects that diff and commits it itself, from its own working tree, onto
the branch it controls.

This achieves the same safety property a more elaborate isolated-clone-per-
worker design would — a bounded worker never writes canonical Git refs or
objects — without building any of that machinery. It falls out of the
primitive Claude Code already provides, once the "Engineer doesn't commit"
contract is stated and the PL actually reviews before committing.

## Auditor isolation

Auditor dispatches are fresh `Agent` calls, not forks — a fork would inherit
the Engineer's reasoning and context, defeating the point of an independent
challenge. The Auditor sees only the PID, the repository state at the commit
under review, and its own instructions.

## What is proven, what is not

Proven boundaries: Git/GitHub delivery surfaces, evidence preservation, and
native subagent dispatch as a viable Engineer/Auditor mechanism. Forge's own
self-test — `docs/evidence/FORGE-SELFTEST-0001.md` — established this for
Claude-native dispatch: a genuinely correct implementation returns GREEN,
and a genuinely blind, independently-verified defect of the exact class the
browser-verification gate exists to catch — never shown to the Auditor in
advance — returns PRODUCT_RED. The gate generalises rather than recognising
only one illustrative example.

Not implemented: queues, leases, a workflow engine, a generic SDK copied into
governed projects, or an async resume daemon. See
`docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine`.
