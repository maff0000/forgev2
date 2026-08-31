# FORGE-BOOTSTRAP-0001 — repo scaffold and doctrine port

Status: COMPLETE (this commit)

## What this covers

Initial scaffold of `/srv/forge`: security baseline (`.gitignore`, gitleaks
pre-commit gate), doctrine ported from ANVIL, the PL delivery loop skill,
and the two subagent definitions. No governed project has moved through the
loop yet — see `docs/FORGE-NORTH-STAR.md#proven-state`.

## Authority

Matt, 2026-08-31, direct WO (`trinity:comms:helm:wo_forge_build_0001`),
plan review (`trinity:comms:helm:reply:wo_forge_build_0001_plan_review`),
and the path-containment correction
(`trinity:comms:helm:correction:forge_agents_path_containment`).

## Discrepancy resolved: email-builder `PROJECT_ROOT`

ANVIL's `email-builder/PID.md` declares `PROJECT_ROOT: /srv/codex/email-builder`
in both copies found on this host. The actively-developed copy is
`/srv/codex/anvil/email-builder`, evidenced by: identical git origin
(`maff0000/email-builder.git`) in both, a newer commit at the `anvil/` copy
(2026-08-31 09:44Z vs. 2026-08-27 11:09Z), and `AXIOM.md` at the `anvil/`
copy being a strict superset of the other (it carries later doctrine —
Git-durability rule, worker-watch feedback protocol, ACK's thinness
principle — the older copy never received). `PROJECT_ROOT` is stale
documentation drift from before the project moved under `anvil/`, not a
live discrepancy. Not corrected in place here — that's a trivial first
Forge-Engineer task against `email-builder`'s own PID, once Forge points at
it, with its own evidence trail rather than a silent out-of-band edit.

## Porting decisions — what was kept, changed, or dropped

| ANVIL element | Forge disposition | Why |
|---|---|---|
| North Star doctrine (purpose, authority model, durable truth, anti-bloat, workspace doctrine, half-built-project workflow) | Ported near-verbatim, Codex/Axiom → Claude/PL substitutions | WO: "port it faithfully, not redesign" |
| `frontend-product-ui/SKILL.md` (presentation targets, PRODUCT RED, auditor checklist) | Ported into `skills/forge/SKILL.md`, generalised from "frontend" to the whole PL loop | Same doctrine, now the load-bearing gate rather than optional guidance |
| Axiom (PL) | The driving Claude Code session itself, no separate process | No orchestration runtime needed — capability already exists |
| Native Engineer/Auditor subagents (`WORKER-002`–`WORKER-004`) | `Agent` tool calls — `isolation:"worktree"` for Engineer, fresh `Agent` (not fork) for Auditor | Direct Claude-native equivalent; ANVIL had to build subagent viability, Claude Code ships it |
| Local-GPU/Qwen bounded coding (`anvil/anvil/*.py`, the whole benchmark harness) | **Not ported** | Existed to give Codex a second, cheaper set of eyes. Claude subagents already are that. Reintroduce only on an observed capability gap. |
| `ops/github-control` (async issue-comment resume daemon) | **Deferred, not built** | PL is a live session, not an unattended daemon, until an observed need says otherwise |
| Redis/fabric in the delivery loop | **Not used at all** | `Agent`-call return values are the message bus. Stronger than WO Rule 2 requires — the retirement of PBGv2 is the reason this got the stricter reading. |
| `.ack/` (isolated-worker-clone framework found inside `email-builder`) | **Not ported.** One idea borrowed: a bounded worker never writes canonical Git refs/objects (its `ADR-001`) | Not in the WO's reading list; appears to be a separate, more elaborate framework Codex evolved alongside ANVIL for this one project. Forge gets the same safety property for free from "Engineer doesn't commit," without the isolated-clone machinery. |
| `docs/CAPABILITY-MATRIX.md`, `docs/BETA.md` | **Not ported as documents.** Their function (empirical proof before claiming capability) is preserved as `docs/FORGE-NORTH-STAR.md#proven-state`, currently empty | ANVIL's matrix records local-model benchmark results specific to Codex's own capability question; Forge's equivalent claim ("Claude subagents are viable Engineer/Auditor") is asserted by construction and awaits its own first real proof, not a ported table of someone else's numbers |

## Path containment

`/srv/forge/.claude/agents/forge-engineer.md` and
`/srv/forge/.claude/agents/forge-auditor.md` — full path, always. A bare
`.claude/agents/forge-auditor.md` reference is ambiguous between Claude
Code's project scope and user/global scope; left unfixed, that is exactly
how core doctrine ends up living outside this repository's git history.
Caught by Trinity before any file existed on disk — see
`trinity:comms:helm:correction:forge_agents_path_containment`.

## Verification

- `gitleaks protect --staged` ran clean on every commit in this bootstrap
  (enforced by the committed pre-commit hook, not run manually after the
  fact).
- No internal IPs, hostnames, or infra fingerprints of this host appear in
  any committed file — checked by inspection during authoring, not by tool.
- No PID has moved through the loop yet. This bootstrap is infrastructure,
  not a proof of the delivery loop itself.
