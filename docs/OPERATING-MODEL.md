# Operating model

`Human + CGPT PID → PL (driving Claude Code session) → Engineer/Auditor subagents → GitHub → CGPT scrutiny`

The Human Product Owner participates in PID creation/start, genuinely
unavoidable product decisions, and final acceptance. Routine technical
questions remain with the PL. The Human must not act as a message courier
between the PL and CGPT; a GitHub issue on the governed project (or on this
repository, for Forge's own framework changes) is the durable communication
surface once that need is observed — not built pre-emptively.

Forge itself is reviewed by CGPT independently, specifically for fidelity to
ANVIL's doctrine, per `trinity:anvil:claude_port_plan:v1` — a deliberate
structural safeguard: the entity with the most direct knowledge of where
ANVIL's doctrine is load-bearing versus incidental is ANVIL's own builder.

Future delivery loops must preserve mechanical tests, bounded attempts,
evidence, and independent scrutiny — including, for anything user-facing,
scrutiny in a real rendered browser. See `.claude/agents/forge-auditor.md`.
