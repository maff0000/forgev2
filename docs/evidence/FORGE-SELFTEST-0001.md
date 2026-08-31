# FORGE-SELFTEST-0001 — prove the loop before Estate Research

Status: CASE 1 COMPLETE (this commit). CASE 2 PENDING — canary design blocked
on R2D2's input, per WO instruction not to decide it solo.

## Authority

Matt via Trinity, `trinity:comms:helm:wo_forge_selftest_0001`, 2026-08-31:
before Forge touches `email-builder`, Forge must be fully formed and tested
— proven to do the one thing it exists to do, not just "runs without
erroring."

## Case 1 — positive case: does the loop run at all

PID: `self-test/case-1-positive-toggle/PID.md`. A minimal Flask app, one
route, a "Show details" toggle using the native `hidden` attribute,
declared `PRODUCT_USABLE` specifically to trigger the Auditor's mandatory
browser-verification gate on a genuinely correct implementation.

### Loop executed

1. PL wrote the PID, committed and pushed (`7662bc2`).
2. PL cut an isolated worktree (`/srv/forge-worktrees/case-1-positive-toggle`,
   branch `selftest/case-1-positive-toggle`) and dispatched an Engineer
   (fresh `Agent` call, given `.claude/agents/forge-engineer.md`).
3. Engineer implemented the app, its own tests, its own `.venv`, reported
   `completed` — did not commit, did not push, per its contract.
4. PL reviewed the diff directly (read every file, checked specifically for
   any CSS `display` rule that could override `[hidden]` — none found),
   independently re-ran the test suite rather than trusting the Engineer's
   report (`2 passed`), then committed it itself: `44de2d05479006d3b28986848543f95c3afb3da7`.
5. PL pushed the branch and dispatched a **fresh** Auditor (separate `Agent`
   call, zero inherited context from the Engineer or the PL's own review —
   given only `.claude/agents/forge-auditor.md`, the commit SHA, and the
   repo).

### Auditor verdict

```
AUDIT_VERDICT: GREEN
commit_sha: 44de2d05479006d3b28986848543f95c3afb3da7
real_browser_reproduction_completed: yes
root_cause_identified: n/a
AC1_verified: yes
AC2_verified: yes
AC3_verified: yes
console_errors: none
findings: none
confidence: high
```

Independently confirmed dependency parity (`pip freeze` vs. `requirements.txt`),
re-ran the server test suite (`2 passed`), installed Playwright + Chrome for
Testing disposably into the project's own `.venv` (not added to
`requirements.txt`), and drove four real interactions against the live app
on `127.0.0.1:5199`:

| Step | Action | Panel `is_visible()` before → after | `hidden` attr | computed `display` | Console |
|---|---|---|---|---|---|
| 1 | Navigate (AC1) | — → `false` | present | `none` | none |
| 2 | Click toggle (AC2) | `false` → `true` | absent | `block` | none |
| 3 | Click toggle again (AC3) | `true` → `false` | present | `none` | none |
| 4 | Reload (round-trip check) | `false` → `false` | present | `none` | none |

Zero console errors or warnings across the full sequence. Button label and
`aria-expanded` tracked correctly at every step. App and browser processes
confirmed cleanly stopped (port checked free, no lingering Chromium
processes, no scratch artifacts left in the repo).

**This proves the mechanics of the loop work end to end**, including the
part that matters most: the Auditor drove a real browser and checked actual
computed visibility, not markup presence or a fired event handler.

### Delivery

Merged via PR into `main` — see PR reference below. Worktree removed after
merge.

## Case 2 — negative control (WORKER-015-class canary)

**Not built yet.** Per the WO, the canary design is not the PL's call to
make solo — R2D2 designed the browser-verification gate itself and is
better placed to judge what shape of defect tests it honestly versus what
would be too easy or accidentally untestable.

Design question sent: `helm:comms:r2d2:wo_forge_selftest_0001_canary_design_ask`.
Two candidate shapes proposed for her review — deliberately *not* a replay
of worker-015's literal CSS-override-on-`[hidden]` bug, since that exact
pattern is named in `forge-auditor.md`'s own spec and testing it verbatim
would show pattern-matching, not generalisation:

- an id-mismatched click handler (correct markup, no server involvement,
  wrong element targeted — nothing visibly changes);
- a Save action whose server response is correct and tested, but whose
  client-side handler never reads it or updates the DOM.

Awaiting her call before an Engineer builds it. This section will be
updated with the second Auditor dispatch's verdict once that happens —
Forge does not get pointed at `email-builder` until this section reads
`AUDIT_VERDICT: PRODUCT_RED` or `AUDIT_VERDICT: STARTUP_FAILURE`, never
`GREEN`.
