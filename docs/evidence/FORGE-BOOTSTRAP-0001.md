# FORGE-BOOTSTRAP-0001 — repo scaffold and doctrine

Status: COMPLETE (this commit)

## What this covers

Initial scaffold of `/srv/forge`: security baseline (`.gitignore`, gitleaks
pre-commit gate), core doctrine (purpose, authority model, durable truth,
anti-bloat constraints), the PL delivery loop skill, and the two subagent
definitions. No governed project had moved through the loop yet at this
point — see `docs/FORGE-NORTH-STAR.md#proven-state` for what has been
proven since.

## Authority

Matt, 2026-08-31, direct build instruction.

## Design decisions

- **The PL alone owns Git.** Engineer dispatches run in an isolated
  worktree and report a diff back rather than commit it — the PL reviews
  and commits. This keeps a bounded worker from ever writing canonical Git
  refs or objects, without needing any isolated-clone tooling beyond what
  the dispatch mechanism already provides.
- **Auditor dispatches are fresh, never forks.** A fork would inherit the
  Engineer's reasoning and context; the whole point of independent audit
  is that it doesn't.
- **No local-model delegation harness.** Native subagent dispatch already
  provides an independent second set of eyes on any change; a separate
  delegation layer for a cheaper or local model would duplicate that
  without a proven need.
- **No async resume daemon, no Redis in the delivery loop.** The PL is a
  live session, not an unattended process, until an observed need proves
  otherwise; dispatch return values are the message bus.
- **Mandatory real-browser verification for `PRODUCT_USABLE`+ targets.**
  The single most important rule in this scaffold: a technically-passing
  implementation (clean markup, passing server-side tests) is not
  sufficient evidence that a user-facing feature actually works — only a
  real rendered/interactive check catches a defect invisible to both of
  those. See `.claude/agents/forge-auditor.md` for the full gate and
  `docs/FORGE-NORTH-STAR.md` for why this is doctrine rather than optional
  polish.

## Path containment

`/srv/forge/.claude/agents/forge-engineer.md` and
`/srv/forge/.claude/agents/forge-auditor.md` — full path, always. A bare
`.claude/agents/forge-auditor.md` reference is ambiguous between Claude
Code's project scope and user/global scope; left unfixed, that is exactly
how core doctrine ends up living outside this repository's git history.
Caught before any file existed on disk.

## Verification

- `gitleaks protect --staged` ran clean on every commit in this bootstrap
  (enforced by the committed pre-commit hook, not run manually after the
  fact).
- No internal IPs, hostnames, or infra fingerprints of any host appear in
  any committed file — checked by inspection during authoring.
- No PID had moved through the loop yet at this point. This bootstrap is
  infrastructure, not a proof of the delivery loop itself.
