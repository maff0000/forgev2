# Operating model

`Human + CGPT PID → PL (driving Claude Code session) → Engineer/Auditor subagents → GitHub → CGPT scrutiny`

The Human Product Owner participates in PID creation/start, genuinely
unavoidable product decisions, and final acceptance. Routine technical
questions remain with the PL. The Human must not act as a message courier
between the PL and CGPT; a GitHub issue on the governed project (or on this
repository, for Forge's own framework changes) is the durable communication
surface once that need is observed — not built pre-emptively.

Forge itself is reviewed by CGPT independently as an outside second opinion
on the framework's own soundness — a deliberate structural safeguard
against the blind spots a single builder can't see in its own work.

Future delivery loops must preserve mechanical tests, bounded attempts,
evidence, and independent scrutiny — including, for anything user-facing,
scrutiny in a real rendered browser. See `.claude/agents/forge-auditor.md`.
