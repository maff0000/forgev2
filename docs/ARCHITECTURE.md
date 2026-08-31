# Architecture

Forge has three layers: doctrine (this `docs/` tree and `skills/forge/SKILL.md`),
subagent definitions (`.claude/agents/forge-engineer.md`,
`.claude/agents/forge-auditor.md`), and the PL itself — which is not a
separate process, it is whichever Claude Code session is driving a given PID
under this doctrine.

There is no orchestration runtime, no queue, no daemon, and no database.
Dispatch is a direct Claude Code `Agent` tool call; the message bus is the
tool call's return value.

## How "the PL owns Git" is enforced

Not by a custom isolated-clone tool. `Agent` calls made with
`isolation: "worktree"` already give an Engineer dispatch its own clean git
worktree. The contract layered on top, stated in
`.claude/agents/forge-engineer.md`, is simple: **the Engineer never runs
`git commit`.** It produces a diff in its own worktree and reports back. The
PL inspects that diff and commits it itself, from its own working tree, onto
the branch it controls.

This gets ANVIL's `email-builder/.ack/decisions/ADR-001-isolated-worker-repositories.md`
safety property — a bounded worker never writes canonical Git refs or
objects — without building ADR-001's isolated-clone machinery. It falls out
of the primitive Claude Code already provides, once the "Engineer doesn't
commit" contract is stated and the PL actually reviews before committing.

## Auditor isolation

Auditor dispatches are fresh `Agent` calls, not forks — a fork would inherit
the Engineer's reasoning and context, defeating the point of an independent
challenge. The Auditor sees only the PID, the repository state at the commit
under review, and its own instructions.

## What is proven, what is not

Proven boundaries, inherited directly from ANVIL: Git/GitHub delivery
surfaces, evidence preservation, and native subagent dispatch as a viable
Engineer/Auditor mechanism (ANVIL's `WORKER-002` through `WORKER-004`
established this for Codex subagents; Forge's Claude-native equivalent is
asserted by construction, not yet independently re-proven — the first real
PID through the loop is that proof).

Not implemented: queues, leases, a workflow engine, a generic SDK copied into
governed projects, or an async resume daemon. See
`docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine`.
