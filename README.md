# Forge

A Claude-native port of [ANVIL](https://github.com/maff0000/anvil)'s
PID → PL → Engineer → Auditor delivery framework.

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
  FORGE-NORTH-STAR.md    doctrine ported from ANVIL, Claude-native substitutions
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

## Relationship to ANVIL

ANVIL (`/srv/codex/anvil`, Codex-native) remains untouched and canonical for
its own lineage. Forge ports its doctrine, not its Python local-GPU benchmark
harness — Claude Code's native subagent tooling replaces what ANVIL built
Qwen delegation for. See `docs/evidence/` for the specific porting decisions
and what was deliberately left out.
