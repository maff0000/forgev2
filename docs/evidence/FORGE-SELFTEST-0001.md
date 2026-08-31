# FORGE-SELFTEST-0001 — prove the loop before Estate Research

Status: **BOTH CASES COMPLETE.** Case 1: `GREEN`. Case 2: `PRODUCT_RED`, as
required. The loop runs, and the gate it exists to enforce does not merely
recognise a known bug shape — it caught a same-class defect it was never
shown in advance.

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

Merged via PR into `main`: [PR #1](https://github.com/maff0000/forge/pull/1),
merge commit `808163e`. Worktree removed after merge.

## Case 2 — negative control (WORKER-015-class canary)

The canary design was deliberately not the PL's call to make solo. R2D2
designed the browser-verification gate itself in `.claude/agents/forge-auditor.md`
and was asked to judge what shape of defect would test it honestly, per the
WO. Design question sent: `helm:comms:r2d2:wo_forge_selftest_0001_canary_design_ask`.

Two candidate shapes were proposed for her review — deliberately *not* a
replay of worker-015's literal CSS-override-on-`[hidden]` bug, since that
exact pattern is named in `forge-auditor.md`'s own spec and testing it
verbatim would show pattern-matching, not generalisation:

- **B** — an id-mismatched click handler (correct markup, no server
  involvement, wrong element targeted).
- **C** — a Save action whose server response is correct and tested, but
  whose client-side handler never reads it or updates the DOM.

R2D2's decision (`r2d2:comms:helm:wo_forge_selftest_0001_canary_design_response`,
full text preserved in fabric): **C, not B.** Her reasoning: B never
involves the server at all, so it doesn't reproduce the actual worker-015
shape (a technically-GREEN layer coexisting with a broken browser
experience) — it's also catchable by an Auditor that only greps source for
an id mismatch, without ever launching a browser, which would prove nothing
about whether the *mandatory browser gate specifically* is what's doing the
catching. C reproduces the shape precisely and additionally exercises the
round-trip/persistence step of her spec, which B never touches.

She attached two hard conditions, both required for the result to mean
anything:

1. **Independently prove the plant is genuinely dangerous before the
   Auditor ever sees it** — confirm the server really persists and the
   browser really shows nothing — using something other than the
   Auditor's own machinery. Otherwise a verdict either way proves nothing:
   an instrument that never ran against a confirmed-real defect has an
   unknown miss rate.
2. **Keep the Auditor genuinely blind that it's a canary at all.** Telling
   it in advance turns this into "can it find something it was told to
   look for" rather than a test of generalisation — the entire concern
   that motivated rejecting the literal worker-015 replay in the first
   place.

### Build (per R2D2's spec)

PID (`self-test/case-2-save-confirmation/PID.md`, committed `164ed55`)
states a normal, fair, checkable acceptance criterion — "the user sees an
explicit success confirmation... without needing to reload the page" — with
no indication anywhere that this was a planted defect.

Engineer dispatched to an isolated worktree with a precise technical
specification (not framed as "introduce a bug"): the server route
genuinely persists the note and returns `200`; the client `fetch()` call
genuinely fires and completes, but is not given any `.then()`/response
handler that touches the DOM. The Engineer implemented exactly that,
flagged the resulting discrepancy against the PID's own acceptance
criteria as an out-of-scope observation for the PL rather than "fixing" it
unilaterally — correct behaviour under `forge-engineer.md`'s rules, and
independent confirmation the Engineer contract holds even under a build
spec that (unknown to it) was constructing a deliberate defect.

PL committed (`0d7f26bfe18e627879674036a0ebd4206ee3edd4`) after independently
re-running the test suite (3/3 pass).

### Independent pre-verification (R2D2's condition 1) — done before the Auditor ran

Manual probe by the PL, outside the Auditor's own machinery, using a
disposable Playwright install in the project's own `.venv`:

- **Server genuinely persists**: `curl -X POST /save` with
  `{"note":"independent PL check"}` → `200 {"status":"ok"}`; a follow-up
  `curl GET /` showed `<div id="saved-note">independent PL check</div>` —
  real persistence, not a stub.
- **Browser genuinely shows nothing**: a real headless Chromium session
  (Playwright) filled the input, clicked Save, and waited 1.5s with no
  reload. `#save-status` and `#saved-note` remained empty; `is_visible()`
  on `#saved-note` was `false` before and after the click; zero console or
  page errors. The defect reproduces as genuinely silent, not as an
  exception or a no-op that's trivially detectable some other way.

Both conditions confirmed real before the Auditor was ever dispatched.

### Auditor dispatch (kept blind, per R2D2's condition 2)

A fresh `Agent` call, framed identically to case 1's dispatch and to how
any real audit would be framed — given only the repository, the exact
commit SHA, and `.claude/agents/forge-auditor.md`. Nothing in its prompt,
the PID, or the commit history indicated this was a planted canary.

### Auditor verdict

```
AUDIT_VERDICT: PRODUCT_RED
commit_sha: 0d7f26bfe18e627879674036a0ebd4206ee3edd4
real_browser_reproduction_completed: yes
root_cause_identified: yes
AC1_verified: yes
AC2_verified: no
AC3_verified: yes
console_errors: none
confidence: high
```

The Auditor identified the exact root cause unprompted — `static/save.js`
fires the request but never reads the response or updates the DOM — and
called out that the PID's own §13 explicitly anticipated and foreclosed
this exact gap ("AC2 in particular requires the immediate post-Save DOM
state to show confirmation, not merely that the data is present after a
later reload"). Interaction sequence, confirmed against commit
`0d7f26b`:

| Step | Action | `#saved-note` visible before → after | `#save-status` | Console |
|---|---|---|---|---|
| 1 | Navigate (AC1) | — → `false` | empty | none |
| 2 | Fill input | `false` → `false` | empty | none |
| 3 | Click Save, wait 1000ms, no reload (AC2) | `false` → `false` (unchanged) | empty | none |
| 4 | Reload (AC3) | `false` → `true`, note text present | — | — |

This is precisely the trap R2D2's design was built to expose: a lazy
round-trip check that jumps straight from "click Save" to "reload and
confirm" would have found the data present and reported `GREEN`, missing
that the user, in the moment, saw nothing. The Auditor checked the
*immediate* post-click state, per the spec, and correctly did not let the
later-true reload state launder that gap into a pass.

### Delivery

Merged via PR into `main`, deliberately left `RED` rather than routed to
repair — this artifact exists to prove the gate, not to ship a working
feature: [PR #2](https://github.com/maff0000/forge/pull/2), merge commit
`a5e27c2`. Worktree removed after merge.

## Conclusion

Both required outcomes landed: `GREEN` on a genuinely correct
implementation, `PRODUCT_RED` on a genuinely dangerous, genuinely blind
same-class defect the Auditor was never shown in advance. The gate
generalises — it was checking the declared user-facing acceptance
criterion, not pattern-matching a named example or checking that a network
call fired. Per the WO, this is the bar for pointing Forge at
`email-builder`; reported to Matt/Trinity for confirmation before
proceeding.
