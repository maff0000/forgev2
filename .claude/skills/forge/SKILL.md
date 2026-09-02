---
name: forge
description: PL-facing delivery loop for Forge-governed projects — PID intake, Engineer/Auditor dispatch, PRODUCT RED adjudication, presentation-target gating.
---

# Forge — PL delivery loop

This is the doctrine the driving session follows while acting as PL for a
Forge-governed project. It is not application runtime code, and governed
applications must not import Forge because of it.

## 0. PL startup gate — verify before touching anything

**Hard gate, not a habit.** Before a PL takes any action on a project —
before writing a PID, before dispatching an Engineer, before touching a
single file — it verifies three things exist for that project:

1. A PID.
2. A git repository.
3. A GitHub remote.

Run `./ops/pl-startup-gate <PROJECT_ROOT>` (ships with Forge, depends on
nothing but `git` — no fabric, no Redis, no household-specific tooling,
because the mode that matters most here is a human engineer standing Forge
up cold on their own machine, on a project Forge has never seen, with none
of this repository's context available). It exits `0` only if all three are
present; otherwise it prints exactly which is missing.

**If any of the three is missing, that is a PRODUCT-AUTHORITY GAP, not an
implementation problem.** The PL does not invent a PID on its own
authority, does not quietly `git init`, does not create a GitHub repo
behind anyone's back to paper over the gap. It stops, states plainly which
of the three is missing, and returns the decision to whoever holds product
authority for that project — the Human, a PL-sponsor acting on the Human's
behalf, or whichever engineer is running Forge. This is deliberately an
explicit refuse-to-proceed check rather than an implied first step — the
difference between a framework that actually governs and one that assumes
governance already happened before it was invoked. See
`docs/ARCHITECTURE.md` for where this sits relative to the rest of the
loop.

**This gate checks existence only, not correctness.** "The PID exists" is
the gate; "is the PID actually right" (Forge's own bootstrap found a PID
field that was present and still wrong — see `docs/evidence/FORGE-BOOTSTRAP-0001.md`)
stays a separate, later concern for step 1 below, not something folded into
a hard go/no-go check. Existence-only keeps the gate cheap and unambiguous;
folding correctness in would turn a clean pass/fail into a judgment call
the gate isn't meant to make.

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

**Before dispatching, read the PID's own acceptance criteria against each
other — not just each one in isolation.** Seen twice across two increments,
same shape both times: a regression criterion written as "still behaves as
today" that quietly contradicts a "change Y" criterion stated elsewhere in
the same PID. Both times an Engineer caught the contradiction and reported
it rather than silently resolving it either way — correct Engineer
fallback behavior — but the check belongs before dispatch, not after. The
reason this is genuinely easy to miss while composing: the contradiction is
invisible from inside the section being written — a "preserve X" criterion
reads correctly on its own, a "change Y" criterion reads correctly on its
own, and the conflict exists only in the relationship between them, not in
either sentence alone. Read the finished acceptance-criteria list back as a
set, specifically hunting for a preserve/change pair that can't both hold,
before an Engineer is dispatched to discover it instead.

**Write a measured claim and an inferred claim in visibly different voices.**
Observed: a PID stated that four affected form submissions were "ordinary
buttons on the editor page." Three of them were; the fourth was reachable
by no browser gesture at all. Every other claim in that section had been
established by driving real requests, and that one had been inferred from
reading a template — but nothing in the wording distinguished them, so an
Engineer only found it mid-implementation. Inference in a PID is
legitimate; inference wearing the voice of measurement is not, because the
next reader cannot tell which claims to re-check and so re-checks none.
Marking it costs one clause — "inferred from the template, not driven."
This and the two related ways a genuinely measured number can still fail to
be evidence: `docs/EVIDENCE-DOCTRINE.md`.

**Where a criterion can only be proven in the browser, say so in the PID,
before dispatch.** Observed: a defect lived entirely in client-side
JavaScript, so no server-side test could observe it — the whole Python
suite could pass with the defect fully live. That PID declared the
limitation up front and required the Python tests be written as regression
pins and *named* as such, rather than described as proving the fix. The
alternative is discovering the limitation at audit, after an Engineer has
spent its dispatch writing tests that quietly cannot fail. Naming the
load-bearing gate in the PID is nearly free, and it also tells the Auditor
which criterion its browser run is the only evidence for.

## 3. Decompose and sequence

Break the PID's scope into bounded, independently reviewable work items.
Small enough that an Engineer dispatch can complete one without needing to
guess at intent, and an Auditor can check it against the PID without asking
what was meant.

**The default question at this step is which of these work items are
genuinely independent of each other — not whether to parallelize.**
Independent work items get dispatched concurrently, each its own isolated
worktree, as standard practice. Sequential, single-Engineer dispatch is the
*fallback* — for work items genuinely dependent on each other's output, or
where independence can't actually be established — not the default
posture. A PL that only ever dispatches one Engineer at a time on a PID
with several genuinely independent parts isn't being cautious, it's leaving
the actual point of this loop on the table.

The judgment call this puts on the PL is decomposition quality, not raw
concurrency. Spraying several Engineers at loosely-related work to look
efficient is a different, worse failure mode than the one this default
fixes — the fix is "parallelize what's actually independent," not
"maximize how many Engineers are running."

## 4. Dispatch the Engineer(s)

`Agent` tool call(s) — one per independent work item identified above,
dispatched concurrently when more than one is genuinely independent. Each
gets its own isolated worktree and its own scoped prompt: the specific work
item, the `PROJECT_ROOT` boundary, what it may and may not touch, and the
relevant PID sections. Before styling or structural changes on anything
user-facing, an Engineer should inspect the existing templates/CSS/component
conventions first, not introduce a new stack.

**`isolation: "worktree"` isolates the calling session's own repository —
that is only `PROJECT_ROOT` when there is no hub split.** Under the hub
model (`docs/FORGE-NORTH-STAR.md#central-forge--hub-not-a-single-project-tool`),
a PL boots from `/srv/forge` and is pointed at a separate `PROJECT_ROOT`;
`isolation: "worktree"` in that case still cuts a worktree, but from
Forge's own repository, not the project's. Full failure mode and the fix
are below — read this before dispatching in the hub-model case.

**Known sharp edge #1 — shared-path collision (mitigated below):**
`isolation: "worktree"` is not by itself a guaranteed boundary even when it
does isolate the right repository. During the first real concurrent
Engineer+Auditor dispatch against one repository, both ended up operating
directly against the shared `PROJECT_ROOT` working directory instead of
their assigned isolated worktrees, and collided — caught and recovered by
the PL before anything was lost, but the isolation the whole multi-Engineer
default depends on did not hold on its own. Do not trust the mechanism
alone; the two steps below ("states its worktree path explicitly" and
"verify isolation held") are required, not optional hardening.

**Known sharp edge #2 — isolated from the wrong repository entirely (hub
model, proven in practice):** sharp edge #1 assumed the worktree at least
came from the correct repository. Under the hub model it does not.
`isolation: "worktree"` cuts its worktree from the *calling session's own
root* — for a PL booted from `/srv/forge` and pointed at a separate
`PROJECT_ROOT`, that root is Forge's own repository. The Engineer lands in
a perfectly valid, cleanly isolated worktree — of the wrong project's
history. The mechanism does not error or warn; it isolates exactly as
documented, it just isolates the wrong thing. A check of the form "confirm
the Engineer is isolated from `PROJECT_ROOT`" **passes** in this failure
mode — the worktree genuinely is isolated from `PROJECT_ROOT`, just not
*of* it. ARCHITECTURE.md's claim that `isolation: "worktree"` "already
gives an Engineer dispatch its own clean git worktree" is true and not
sufficient by itself — clean isolation of the wrong repository is not what
anyone needs.

**The distinguishing check, proven in practice:** `git cat-file -t <a
commit SHA known to exist in PROJECT_ROOT's real history>`, run inside the
Engineer's worktree. If `PROJECT_ROOT`'s own commits do not resolve there,
the worktree is isolated from the wrong repository, full stop.

**Reference Engineer behavior when this precondition is broken — worth
naming explicitly, not just fixing the trigger:** proven in practice by two
Engineers dispatched under this exact failure. Both reported `blocked`
without writing a single line of the actual work item, refused to
self-rescue by cloning or fetching the correct project into the worktree to
route around it, and deliberately withheld any patch output — so an
empty/missing patch on a `blocked` report could not be misread as "produced
no diff, nothing needed." That is the exact behavior the Engineer contract
exists to produce on a broken premise: stop, don't improvise past it, don't
send an ambiguous signal. See `.claude/agents/forge-engineer.md#reference-behavior-blocked-on-a-broken-precondition`.

**Hub-model dispatch procedure — use this instead of `isolation:
"worktree"` whenever `PROJECT_ROOT` is not the PL's own session root:**

1. The PL creates the worktree itself, explicitly against `PROJECT_ROOT` —
   e.g. `git -C <PROJECT_ROOT> worktree add <absolute-path> -b <branch>` —
   never the bare `isolation: "worktree"` flag on the Agent call.
2. Before dispatching, the PL runs the distinguishing check above —
   `git cat-file -t <known-PROJECT_ROOT-commit>` — inside that worktree.
   Only dispatch the Engineer once this resolves; if it fails, the worktree
   was built from the wrong repository and must not be handed to an
   Engineer.
3. Dispatch the Engineer as a plain `Agent` call — no `isolation` flag, the
   PL already built the correct isolated worktree by hand — with that
   worktree's absolute path stated explicitly, per "Every dispatch prompt
   states its worktree path explicitly" below.

When the PL's own session root genuinely *is* `PROJECT_ROOT` — Forge
editing itself, no hub split, no separate target project to isolate from at
all — `isolation: "worktree"` remains correct and simpler to use directly;
skip the manual worktree creation above.

**Every dispatch prompt states its worktree path explicitly, and
forbids the shared path.** Tell each Engineer/Auditor its exact assigned
worktree path in absolute form, and instruct it explicitly to never
reference or operate against the shared `PROJECT_ROOT` path directly —
naming the shared path in a prompt can apparently pull a dispatch back
into it even under `isolation: "worktree"`, so the boundary has to be
stated, not assumed from the isolation flag.

**No Engineer commits — ever, regardless of how many are running.** Each
reports back with a diff in its own worktree. The PL reviews every diff —
inspect each the way you'd review any change before it enters history —
and commits them itself onto the branch the PL controls, in whatever order
and however many separate commits makes sense. Concurrent dispatch does
not loosen "PL owns git" even slightly: every diff, from every Engineer,
still passes through the same PL review before it exists in history. See
`docs/ARCHITECTURE.md` for why this is sufficient without isolated-clone
tooling.

**Verify isolation held before treating any dispatch as clean.** After
every Engineer or Auditor completes, before reviewing its actual content:
confirm its diff genuinely landed in its assigned worktree/branch, that the
worktree's history is genuinely `PROJECT_ROOT`'s (the distinguishing check
above, if it wasn't already run as a hub-model precondition), and `git
status` in the shared `PROJECT_ROOT` shows nothing unexpected. This is not
a careful PL's optional habit — it is a required step in the loop,
precisely because the isolation guarantee has already been observed to
fail silently twice, in two different ways.

If two genuinely-independent Engineers' diffs conflict on integration
despite being judged independent, that's the PL's integration problem to
resolve — and worth treating as a signal the decomposition itself was
wrong, not just a mechanical merge to push through.

If required work would cross `PROJECT_ROOT`, an Engineer should stop and
report rather than expand scope. Route that back through the PID, not
around it.

## 5. Reconcile and test

Run the project's mechanical tests against the PL-integrated commit(s)
before audit — after every dispatched Engineer's diff, whether there was
one or several, has been reviewed and committed. A RED here is not an
Auditor question yet — fix or route back to the responsible Engineer
first.

**A failed check is a claim too, and earns the same scrutiny as a
successful one.** Observed: a PL hypothesised that a pretty-printer
explained a ~12,500 byte size discrepancy, tested the hypothesis, measured
its effect as "a few hundred bytes", and recorded the cause as
*unexplained*. Refusing to assert an unverified hypothesis was the right
instinct — but the refutation was itself wrong twice over: it counted the
wrong population (it missed that the printer also runs over server-rendered
content on load) and it valued a boundary at one character where
indentation made it about 137. The mechanism had been the correct
explanation the whole time. A negative result claims less, so it attracts
less challenge, and that is precisely why it gets through unexamined.
Before recording a cause as unexplained or a hypothesis as refuted, state
what population you measured and what you assumed each unit was worth —
those are the two places this failed. See
`docs/EVIDENCE-DOCTRINE.md#refutations`.

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
target: markup that looks correct and server-side tests that pass cleanly
can both hold true while a UI control is completely dead in a real
browser — a stylesheet rule silently overriding a native attribute, a
client handler that never reads its own network response, or any similar
gap between "technically correct" and "actually works." Only a real
rendered/interactive check catches that class of defect.

**When you know something the Auditor must not be told, give it a
methodological instruction — never the finding.** Observed: an Engineer
reported a pre-existing crash, unrelated to its diff, that would fire the
moment an Auditor clicked one particular control. Both obvious options were
bad. Telling the Auditor about it would launder the Engineer's reasoning
into a supposedly independent audit — the one property the fresh dispatch
exists to preserve. Saying nothing risked the Auditor hitting the crash and
reporting a false finding against a diff that was actually correct. What
the PL did instead was remind the Auditor that a criterion reading "zero
*new* console errors" requires establishing base-commit behaviour before
attributing anything to the diff. That is true of every audit, it leaks
nothing about this one, and an Auditor following it handles the crash
correctly on its own evidence. The same shape covers instrument hazards: a
warning about stale one-shot dialog handlers in the browser tooling is
tooling hygiene, not a hint about the diff.

**The test to apply before adding anything to an Auditor dispatch prompt:**
would you give this same instruction to an Auditor on a different PID? If
yes, it is methodology, and safe. If it only makes sense because of what
you know about this particular diff, it is the finding in disguise, and
handing it over costs the audit exactly the independence it was dispatched
to provide. When it is the finding, it stays out of the prompt entirely: if
what the Engineer found needs fixing, route it as its own work item after
the audit returns, rather than smuggling it in as a hint.

## 7. Adjudicate

**Spot-check at least one Auditor finding per audit, routinely — not only
when something else contradicts it.** A real miss surfaced this: the PL
rejected an Auditor's "card copy names a non-existent region" finding only
after checking it directly, and found the Auditor had inspected `<legend>`
elements and missed a real `<h2>` heading — the PL only checked because two
separate audits happened to disagree with each other. A finding nothing
else contradicts currently gets less scrutiny by default, purely because
there is no visible trigger to check it. The check costs almost nothing —
one command, a few seconds — against the artifact directly (not against the
Engineer's account of it, not against the Auditor's own narrative of it).
That low cost is the actual argument for doing it routinely rather than
reserving it for findings that already look suspicious: an Auditor that has
never been independently checked isn't proven independent, it's just
trusted by default. This is a floor — pick at least one finding, verify it
directly — not a replacement for deeper scrutiny when something does look
off.

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

**A correction to something already cited by SHA goes at the citation's
destination, not into the original commit.** See
`docs/FORGE-NORTH-STAR.md#durable-truth` — never rewrite a commit another
part of the evidence trail already points at; append the correction where
that pointer leads.

## Anti-bloat reminder

Do not build a durable "verification history" service, a permanent
regression suite the Engineer inherits by default, or a scheduler for any
of the above. Each PID's loop is a live session doing bounded work, not a
standing system. If a project genuinely needs durable regression coverage
over time, that's a separate, explicit PID decision — this loop doesn't
create one implicitly.
