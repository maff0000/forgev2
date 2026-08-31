# Forge Self-Test Case 1 (Positive) — Project Initiation Document

Part of `WO-FORGE-SELFTEST-0001`. A deliberately trivial synthetic target,
inside Forge's own repo, used only to prove the PID → Engineer → PL-commit →
Auditor loop runs mechanically end to end. Not a real product.

## 1. Identity

```text
PROJECT_ROOT:

/srv/forge/self-test/case-1-positive-toggle

GitHub repository:

maff0000/forge (this project lives inside the Forge repo itself — a
self-test target, not a governed external project)

Remote:

https://github.com/maff0000/forge.git
```

## 2. Purpose

Prove the mechanics of the Forge delivery loop work at all, on the smallest
real feature that still has a genuine user-observable interaction.

## 3. Target Outcome

A single-page Flask app with one button that toggles a details panel open
and closed, correctly, in a real browser.

## 4. Users

None — self-test only.

## 5. Presentation Target

`PRODUCT_USABLE`. This deliberately triggers the Auditor's mandatory
real-browser verification gate — the whole point of this case is proving
that gate fires and passes on a genuinely correct implementation.

## 6. Scope

- One route (`/`) rendering a page with a "Show details" button and a
  details panel, initially hidden.
- Clicking the button reveals the panel; clicking again hides it.
- No persistence, no other pages, no styling requirements beyond basic
  legibility.

## 7. Non-Goals

Anything beyond the single toggle. No forms, no save/load, no export — this
case is deliberately minimal.

## 8. Architecture

Flask, server-rendered HTML, one small JS handler for the toggle. Own
`requirements.txt` and `.venv`, isolated to this directory — do not touch
anything outside `PROJECT_ROOT`.

## 9. Public Repository Security

Applies — this lives inside the public `forge` repo. No secrets, no infra
details. Nothing here should need any.

## 10. Persistence and Durable Truth

None. Stateless page.

## 11. Git and GitHub

The PL (not the Engineer) commits. Standard Forge doctrine, restated here
per `docs/PID-TEMPLATE.md` §11.

## 12. Quality and Testing

Server-side test asserting the route renders the button and the panel
markup. Acceptance criteria for the Auditor's browser gate:

- **AC1**: on initial page load, the details panel is not visible.
- **AC2**: clicking "Show details" makes the details panel visible, with
  its expected text content.
- **AC3**: clicking "Show details" again hides the details panel.

## 13. Acceptance Definition

GREEN requires: server tests pass, AND the Auditor's real-browser
verification drives AC1–AC3 and confirms actual computed visibility at
each step (not just that a click handler fired) — per
`.claude/agents/forge-auditor.md`.

## 14. Development Inputs

`.claude/agents/forge-engineer.md`, `.claude/agents/forge-auditor.md`,
`.claude/skills/forge/SKILL.md`.
