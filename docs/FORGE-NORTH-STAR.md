# Forge — North Star Architecture

## Purpose

Forge is a lightweight development-control system for taking software
projects from Human/CGPT-defined product intent to independently scrutinised
delivery.

Its purpose is to let a Human point Forge at a new, existing, incomplete, or
partially broken project while the PL establishes repository truth, holds the
PID as authority, decomposes and sequences work, dispatches Engineer
subagents for bounded implementation, reconciles changes, runs tests, obtains
independent Auditor scrutiny, routes valid repairs, and maintains clean
Git/GitHub history before returning a delivery candidate.

The destination is:

```text
Human + CGPT
     ↓
    PID
     ↓
     PL
     ↓
Engineer subagents (bounded implementation)
     ↓
reconciliation + tests
     ↓
independent Auditor subagent
     ↓
bounded repair when required
     ↓
GitHub delivery candidate
     ↓
Human + CGPT final scrutiny
```

Human involvement belongs at product authority and final acceptance, not at
routine implementation or repair decisions.

## Core doctrine

**Capability first. Architecture second.**

Forge is built only around empirically proven capabilities. Every mechanism
must solve an observed problem. Existing platform capabilities and standard
tools are preferred over custom machinery.

For user-facing work, technical correctness alone does not imply product
acceptance. Human/CGPT may issue a `PRODUCT RED` finding against a
technically GREEN implementation, returning it to the bounded repair loop.
User-facing PIDs must declare a presentation target — `FUNCTIONAL_ONLY`,
`PRODUCT_USABLE`, or `PRESENTATION_POLISHED` — per
`.claude/skills/forge/SKILL.md`. This exists because markup that looks correct and
server-side tests that pass cleanly are not sufficient evidence that a
user-facing feature actually works: a control can carry the right markup
while a stylesheet rule elsewhere silently overrides its visible state, and
every check that only inspects rendered HTML or server responses will
report GREEN while the control is completely dead the moment a real person
opens the page. Forge's Auditor carries mandatory real-browser verification
for `PRODUCT_USABLE`+ as a day-one requirement, not later polish — see
`.claude/agents/forge-auditor.md`.

## Authority model

### Human + CGPT

Own product intent, PID definition, major product/architectural authority,
and final independent scrutiny. CGPT additionally reviews Forge's own
framework code (this repository) independently, as an outside second
opinion on the framework's own soundness — a distinct role from CGPT's
per-project product-authority role above.

### PL (Project Lead)

The PL is the driving Claude Code session itself, operating under this
doctrine set. It owns repository discovery, decomposition, sequencing,
Engineer/Auditor dispatch, reconciliation, testing, Git, PR lifecycle, and
acceptance or rejection inside the delivery loop.

**The PL alone commits, branches, and manages the PR lifecycle.** Engineers
implement inside an authorised scope; they do not commit to the canonical
branch, do not touch Git history, and do not have GitHub authority.

### Engineer

The Engineer owns bounded implementation within the authorised scope. It does
not own product authority, Git lifecycle, or final acceptance. See
`docs/ARCHITECTURE.md` for how this is enforced by construction rather than
by convention alone.

### Auditor

The Auditor independently challenges implementation against the PID and
repository truth. It does not edit during audit. A RED finding is evidence
for the PL to adjudicate and route to a fresh repair Engineer.

## Durable truth

Forge must be reconstructable from repository contents, PID, constraints,
committed evidence, and Git history. Git is durable code, history, and
evidence truth. GitHub is durable external collaboration and scrutiny truth.
Transient runtime state is not architectural truth. Redis or another live
state mechanism may be introduced only if an observed operational problem
genuinely requires it, and even then never for anything durable — this is a
hard constraint, not a preference. It is the direct fix for what retired
PBGv2: an auto-resume/timer mechanism that treated Redis as durable
coordination state instead of a message bus, and burned a week of tokens in
one night.

## Project integration model

Forge's own code is not copied into governed applications, and applications
do not import or depend on Forge. A governed project may carry a small
self-describing control envelope such as:

```text
project/
├── .forge/
│   ├── project.yaml
│   ├── CURRENT-TRUTH.md
│   └── constraints.md
├── docs/
│   ├── PID-...
│   └── evidence/
├── application code
└── tests
```

The exact `.forge/` contract is not frozen. It will be introduced
incrementally only when real projects prove which information is necessary —
Forge's own bootstrap did not need one, so none exists yet.

## Central Forge — hub, not a single-project tool

Forge remains a separate project/runtime responsible for the PL doctrine,
Engineer/Auditor subagent definitions, execution doctrine, clean workspace
strategy, and Git/GitHub delivery. Multiple projects must be able to proceed
independently without contaminating one another.

```text
                    Forge
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Project A   Project B   Project C
        .forge/     .forge/     .forge/
```

**`/srv/forge` is where a PL boots from — never a project directory.** A
project such as an email-builder application is a `PROJECT_ROOT` a given
PL session is *told to operate on*, passed as a parameter (to
`ops/pl-startup-gate` and to every Engineer/Auditor dispatch), never the
directory a PL session itself is launched or rooted in. A Human boots a
PL from the hub and points it at a project, rather than opening a session
inside each project in turn.

**Concurrent PLs on different projects work by construction, not by added
machinery.** Verified directly, not assumed: `ops/pl-startup-gate` takes
`PROJECT_ROOT` as its only parameter and holds no state of its own between
invocations — no lock file, no `/tmp` state, nothing written anywhere. The
Engineer and Auditor definitions contain no hardcoded project path and no
shared/global/singleton assumption. Nothing in this doctrine set uses
Redis, a daemon, or any mechanism a second, independent PL session could
collide with. Each PL is simply an independent Claude Code session, booted
from `/srv/forge` with the `forge` skill discoverable, given a different
`PROJECT_ROOT`. Multiple such sessions running at once, each against a
different project, share nothing to contaminate — the same one-hub,
many-independent-spokes shape as the diagram above.

This does not cover two PLs working the *same* project concurrently — that
is a within-project coordination question (branch/worktree naming
collisions are possible there) distinct from the hub model this section
states, and not yet exercised or proven.

## Workspace doctrine

The developer working directory is not necessarily the delivery workspace.
The preferred flow is:

```text
authoritative GitHub baseline
         ↓
fresh isolated clone
         ↓
dedicated feature branch
         ↓
PL / Engineers / Auditor
         ↓
tests and evidence
         ↓
GitHub PR
```

This protects dirty worktrees, parallel projects, Git provenance, and
reproducibility.

## Claude-native execution doctrine

Bounded implementation and independent audit are Claude Code subagent
dispatches, not a custom orchestration layer:

```text
PL
  ↓
Engineer dispatch — Agent tool, isolation: worktree, scoped prompt
  ↓
diff reviewed and committed by the PL (Engineer never commits)
  ↓
Auditor dispatch — fresh Agent call, zero inherited context
  ↓
GREEN verdict, or RED routed to a fresh repair Engineer
```

Forge does not include a local-model benchmark or delegation harness.
Claude Code's native subagent dispatch already provides an independent
second set of eyes on any change. Reintroduce local-model delegation only
if a real, observed capability gap proves it is needed.

## Anti-bloat doctrine

Do not introduce without observed need:

- broker infrastructure or a generic worker runtime;
- nested sandboxing, project registries, or provider abstractions;
- workflow DSLs, Redis orchestration, schedulers, or lease machinery;
- autonomous daemons or a generic Forge SDK copied into projects;
- an async GitHub-issue resume poller — Forge's PL is a live session, not an
  unattended daemon, until an observed need says otherwise.

Standard operating-system, Git, Python, container, and GitHub primitives are
preferred.

## Half-built project workflow

Recovering and continuing partially built projects is a primary use case:

```text
point Forge at repository
       ↓
DISCOVER
       ↓
establish CURRENT-TRUTH
       ↓
identify working / broken / unfinished state
       ↓
Human + CGPT decide next useful outcome
       ↓
PID
       ↓
PL delivery loop
```

Forge must not assume old documentation or local worktrees are correct;
repository and runtime evidence establish truth. A stale `PROJECT_ROOT`
field is exactly the kind of thing that looks harmless until an Engineer
or Auditor trusts it over the actual repository state — verify against
real git history (remotes, commit timestamps), not a prior document.

## Multi-project goal

Each independent project should have its own authoritative repository, PID,
isolated delivery workspace, PL loop, Git branch/PR, and evidence trail. No
project should require Forge application code to be embedded in it.

## Proven state

`docs/evidence/FORGE-SELFTEST-0001.md` demonstrated the delivery loop end
to end on two self-test PIDs: a genuinely correct implementation returned
`GREEN` with real-browser verification, and a genuinely blind,
independently-verified defect of the exact class the browser-verification
gate exists to catch — designed with R2D2, never shown to the Auditor in
advance — returned `PRODUCT_RED` for the right reason. This proves the
mechanics run and that the gate generalises rather than recognising only
one illustrative example. It does not yet prove Forge on a real external
project with a real product owner; that remains the next real test, not
assumed from this one.

## Current direction

Do not build the final framework from speculation. Progress bit by bit
through useful projects. The immediate proving ground is finishing
`email-builder` for Estate Research: process is reportedly nearly right, but
unattractive and buggy — the actual test of whether Forge closed the gap
its mandatory browser-verification gate exists to close, or just moved it.

## North-star success condition

Forge succeeds when a Human can say:

> Here is what I want this product to become.

Forge then discovers the state, executes the development loop, independently
scrutinises delivery — including in a real rendered browser for anything
user-facing — preserves clean Git/GitHub truth, and returns a trustworthy
delivery candidate while the Human remains outside routine implementation and
repair work.
