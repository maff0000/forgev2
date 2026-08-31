# Forge

A lightweight PID → PL → Engineer → Auditor delivery-control framework for
Claude Code: point it at a project with product intent defined, and it runs
a bounded implementation-and-independent-audit loop toward a delivery
candidate, while a Human retains product authority and final acceptance.

North star: **PID in → autonomous Claude-native delivery → independently
scrutinised product out.** See [docs/FORGE-NORTH-STAR.md](docs/FORGE-NORTH-STAR.md).

## Durable truth

Everything lives in this repository: code, doctrine, PIDs, evidence,
decisions. Redis/fabric may carry live messaging between a session and its
subagents during a run — it holds nothing durable and nothing this repo
depends on for correctness. If it isn't in git, it didn't happen.

## Setup (once per clone)

```sh
./ops/bootstrap
```

Installs nothing itself but verifies `gitleaks` is on PATH and wires the
committed pre-commit hook (`scripts/hooks/pre-commit`, activated via
`core.hooksPath` — not a local-only `.git/hooks` file, so the control is
itself part of Forge's history, not host-local convenience).

## Layout

```text
docs/
  FORGE-NORTH-STAR.md    core doctrine: purpose, authority model, durable truth
  ARCHITECTURE.md
  OPERATING-MODEL.md
  PID-TEMPLATE.md
  evidence/              per-increment evidence trail
skills/forge/SKILL.md    the PL-facing delivery loop
.claude/agents/
  forge-engineer.md      bounded implementation subagent
  forge-auditor.md       independent review subagent (mandatory real-browser
                          verification for PRODUCT_USABLE+ targets)
scripts/hooks/           committed git hooks (secret scanning)
ops/                     small operator scripts, no framework
```

## Scope

Forge does not include a local-model benchmark or delegation harness.
Claude Code's native subagent dispatch (Engineer/Auditor) already provides
an independent second set of eyes on any change; a separate delegation
layer for a cheaper or local model would duplicate that without a proven
need. See `docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine`.
