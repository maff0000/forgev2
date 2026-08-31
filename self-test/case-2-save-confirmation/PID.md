# Forge Self-Test Case 2 — Project Initiation Document

Part of `WO-FORGE-SELFTEST-0001`. A small synthetic target inside Forge's
own repo, used to prove the delivery loop before Forge is pointed at
`email-builder`.

## 1. Identity

```text
PROJECT_ROOT:

/srv/forge/self-test/case-2-save-confirmation

GitHub repository:

maff0000/forge (self-test target inside the Forge repo itself)

Remote:

https://github.com/maff0000/forge.git
```

## 2. Purpose

A minimal note-saving feature: a single text field and a Save button.

## 3. Target Outcome

A user can type a short note, click Save, and know — without reloading the
page — that it was saved.

## 4. Users

None — self-test only.

## 5. Presentation Target

`PRODUCT_USABLE`.

## 6. Scope

- One route (`/`) rendering a page with a text input and a "Save" button.
- One route (`POST /save`) that accepts the note text and persists it
  server-side.
- After clicking Save, the user sees an explicit success confirmation — a
  visible status message and/or the saved note reflected on the page —
  without needing to reload the page.
- Reloading the page after a save shows the previously saved note is still
  present (persistence check).

## 7. Non-Goals

Multiple notes, editing, deleting, authentication, or any styling beyond
basic legibility.

## 8. Architecture

Flask, server-rendered HTML, one small JS handler for the Save action.
In-memory persistence on the server process is sufficient — no database
required. Own `requirements.txt` and `.venv`, isolated to this directory.

## 9. Public Repository Security

Applies — this lives inside the public `forge` repo. No secrets, no infra
details.

## 10. Persistence and Durable Truth

Server-side in-memory store for the note text, scoped to this self-test
process. Not a durable data store — sufficient only to prove the
save-then-reload behaviour within one running instance.

## 11. Git and GitHub

The PL commits, per standard Forge doctrine.

## 12. Quality and Testing

Server-side test asserting `POST /save` returns success and that the note
is retrievable afterward. Acceptance criteria for the Auditor's browser
gate:

- **AC1**: on initial page load, no note is shown and no confirmation is
  present.
- **AC2**: after typing a note and clicking Save, the user sees an
  explicit visible confirmation (a status message and/or the note appearing
  on the page) immediately — without reloading.
- **AC3**: reloading the page after a save shows the previously saved note.

## 13. Acceptance Definition

GREEN requires: server tests pass, AND the Auditor's real-browser
verification confirms AC1–AC3 by driving the actual interaction and
checking resulting visible state at each step — per
`.claude/agents/forge-auditor.md`. AC2 in particular requires the
*immediate* post-Save DOM state to show confirmation, not merely that the
data is present after a later reload.

## 14. Development Inputs

`.claude/agents/forge-engineer.md`, `.claude/agents/forge-auditor.md`,
`skills/forge/SKILL.md`.
