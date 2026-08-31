---
name: forge
description: PL-facing delivery loop for Forge-governed projects — PID intake, Engineer/Auditor dispatch, PRODUCT RED adjudication, presentation-target gating.
---

# Forge — PL delivery loop

This is the doctrine the driving session follows while acting as PL for a
Forge-governed project. It is not application runtime code, and governed
applications must not import Forge because of it — same boundary ANVIL draws
around `frontend-product-ui/SKILL.md`.

## 1. Discover

Point at the project's repository. Do not assume old documentation,
`PID.md` fields, or local worktrees are correct — establish current truth
from the repository and runtime evidence. Forge's own bootstrap found a
stale `PROJECT_ROOT` field this way; assume every project can have one.

## 2. Read or write the PID

Use `docs/PID-TEMPLATE.md`'s shape. If a PID already exists, read it in
full before touching anything — scope, presentation target (§5 of the
template), acceptance criteria. If none exists, this is a genuinely
unavoidable product decision — that's the Human's call, not the PL's to
assume.

**Establish the presentation target explicitly.** `FUNCTIONAL_ONLY`,
`PRODUCT_USABLE`, or `PRESENTATION_POLISHED`. Default to at least
`PRODUCT_USABLE` when the PID calls for a usable user-facing business tool.
Technical tests alone do not establish that target — this single field is
what gates the Auditor's browser-verification requirement below.

## 3. Decompose and sequence

Break the PID's scope into bounded, independently reviewable work items.
Small enough that an Engineer dispatch can complete one without needing to
guess at intent, and an Auditor can check it against the PID without asking
what was meant.

## 4. Dispatch the Engineer

`Agent` tool call, `isolation: "worktree"`. Give it: the specific work item,
the `PROJECT_ROOT` boundary, what it may and may not touch, and the relevant
PID sections. Before styling or structural changes on anything user-facing,
the Engineer should inspect the existing templates/CSS/component
conventions first, not introduce a new stack.

**The Engineer does not commit.** It reports back with a diff in its own
worktree. The PL reviews that diff — inspect it the way you'd review any
change before it enters history — and commits it from the PL's own working
tree onto the branch the PL controls. See `docs/ARCHITECTURE.md` for why
this is sufficient without isolated-clone tooling.

If required work would cross `PROJECT_ROOT`, the Engineer should stop and
report rather than expand scope. Route that back through the PID, not
around it.

## 5. Reconcile and test

Run the project's mechanical tests against the PL-integrated commit before
audit. A RED here is not an Auditor question yet — fix or route back to the
Engineer first.

## 6. Dispatch the Auditor

A **fresh** `Agent` call — never a fork, never a continuation of the
Engineer's session. It should have no memory of the Engineer's reasoning,
only the PID, the repository at the commit under review, and its own
instructions in `.claude/agents/forge-auditor.md`.

For any PID at `PRODUCT_USABLE` or `PRESENTATION_POLISHED` whose diff
touches anything that renders to a browser, the Auditor's real-browser
verification gate is **mandatory, not optional** — see
`.claude/agents/forge-auditor.md` for the full spec. Source-only review,
however clean, is never sufficient by itself to issue a GREEN at that
target. This is the direct, carried-forward fix for the gap in
`worker-015-human-repair.md`: markup and server tests all passed while a
core UI control was completely dead in a real browser.

## 7. Adjudicate

- **GREEN** — accept. Proceed to PR.
- **PRODUCT RED** — a technically-passing implementation that misses the
  declared presentation target, with concrete evidence (not "looked
  broken"). Route to a fresh repair Engineer dispatch. The PL adjudicates
  the finding; it does not overrule it without stated reason.
- **STARTUP_FAILURE** — the app wouldn't run from the audited commit.
  Route to repair; the Auditor does not patch it into running itself.
- **INCONCLUSIVE** — an environment blocker unrelated to the diff (only
  after the standard disposable-setup path was actually attempted and
  failed). Not a verdict on the diff either way — resolve the environment
  issue and re-audit, never report it as a pass.

## 8. Deliver

Clean, reconstructable Git history. PR with the evidence trail — Auditor
verdict, replayable interaction steps for anything browser-verified,
before/after state — landed in the repo, not left fabric-only. Fabric may
carry the live "auditing now" / "verdict is X" message during the session;
it must never be the only place the evidence lives.

## Anti-bloat reminder

Do not build a durable "verification history" service, a permanent
regression suite the Engineer inherits by default, or a scheduler for any
of the above. Each PID's loop is a live session doing bounded work, not a
standing system. If a project genuinely needs durable regression coverage
over time, that's a separate, explicit PID decision — this loop doesn't
create one implicitly.
