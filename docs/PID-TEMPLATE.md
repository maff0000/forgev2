# [Project Name] — Project Initiation Document

This is the standard shape every Forge-governed project's PID follows. Add
project-specific sections; do not drop these.

## 1. Identity

```text
PROJECT_ROOT:

<absolute path — verify it against actual git remote/commit history before
writing it here, not against an assumption or a prior document. A stale
PROJECT_ROOT field looks harmless until an Engineer or Auditor trusts it
over the actual repository state.>

GitHub repository:

<owner/repo>

Remote:

<clone URL>
```

## 2. Purpose

What this project is for, in plain language, one paragraph.

## 3. Target Outcome

What "done" looks like for the Human who owns this PID.

## 4. Users

Who actually uses the delivered product, and how.

## 5. Presentation Target

**Required for any project with a user-facing surface.** Declare one:

- `FUNCTIONAL_ONLY` — behavior and basic operability are the target.
- `PRODUCT_USABLE` — a coherent business-facing interface is required.
- `PRESENTATION_POLISHED` — visual refinement beyond ordinary product
  usability is part of acceptance.

`PRODUCT_USABLE` and above trigger the Auditor's mandatory real-browser
verification gate — see `.claude/agents/forge-auditor.md`. This field is not
decorative; it changes what "GREEN" is allowed to mean.

## 6. Scope

What is being built or changed, in this increment. Be specific enough that
an Engineer dispatch does not need to guess, and an Auditor can check
against it without asking the PL what was meant.

## 7. Non-Goals

What is explicitly out of scope, stated so a well-meaning Engineer does not
expand it.

## 8. Architecture

Existing structure the Engineer must work within; what may and may not
change without a PID update.

## 9. Public Repository Security

Only if the repository is public. What must never be committed (internal
infra details, secrets), and confirmation the gitleaks gate is active
(`./ops/bootstrap` from this project's own root, if it carries one).

## 10. Persistence and Durable Truth

What state this project keeps and where. Redis/fabric, if used at all, is
messaging only — state this explicitly per project, don't assume it's
understood.

## 11. Git and GitHub

Branching model, who has commit authority (the PL, per Forge doctrine —
restate it here rather than relying on it being implicit), PR flow.

## 12. Quality and Testing

Mechanical tests required. For `PRODUCT_USABLE`+, name the user-facing
acceptance criteria explicitly and phrase them as observable interactions
("clicking X reveals Y", not "the endpoint returns 200") — the Auditor's
browser-verification gate drives exactly these criteria, and a vague
criterion produces an unfalsifiable verdict.

**Name any criterion that only the browser gate can prove.** If a defect or
behaviour lives in client-side JavaScript, no server-side test can observe
it — the whole suite can pass with the defect fully live. Say so here, and
say what the mechanical tests are for instead: regression pins, not proof
of the fix. Declaring it costs a sentence; discovering it at audit costs an
Engineer dispatch spent writing tests that quietly cannot fail. See
`.claude/skills/forge/SKILL.md#2-read-or-write-the-pid`.

## 13. Acceptance Definition

What must be true for this PID to close. Reference the presentation target
from §5 explicitly: a `PRODUCT_USABLE`+ PID cannot close on source-only
review, per `.claude/agents/forge-auditor.md`.

## 14. Development Inputs

Existing code, prior PIDs, or evidence the Engineer/Auditor should read
before starting.
