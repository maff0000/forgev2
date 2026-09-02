# Forge — Project Initiation Document

Forge-governed, by itself. This PID follows `docs/PID-TEMPLATE.md`, adapted
where a field written for an application project does not honestly apply to
a delivery-control framework. Where a field is adapted, §0 says why.

## 0. Why this PID is adapted, and why it exists at all

`ops/pl-startup-gate` refuses to let a PL act on any project lacking a PID,
a git repository and a GitHub remote. Run against `/srv/forge`, it failed:
Forge governed other projects while not being governed itself. That gap
stood through every increment in this repository's history, including the
one that wrote the gate.

Two fields are adapted rather than answered mechanically:

- **§4 Users.** Forge has no end users. Its readers are PL sessions,
  Engineer and Auditor dispatches, and the human standing it up cold. That
  is who §4 describes.
- **§5 Presentation Target.** Forge has no user-facing rendered surface, so
  no target applies to Forge itself. Declaring one anyway would be the
  mechanical box-tick this framework exists to prevent. What §5 does state
  is Forge's obligation to the presentation targets of the projects it
  governs.

Filling those in with plausible-sounding application answers would have
passed the gate while making the document worse. The gate checks existence,
not correctness (`SKILL.md` §0) — passing it honestly is the PL's job, not
the script's.

## 1. Identity

```text
PROJECT_ROOT:

/srv/forge

GitHub repository:

maff0000/forge

Remote:

https://github.com/maff0000/forge.git
```

Verified against `git remote -v` and `git log` in this repository at the
time of writing, not carried from another document. Forge's own bootstrap
found a stale `PROJECT_ROOT` field this way once
(`docs/evidence/FORGE-BOOTSTRAP-0001.md`); the template's warning on this
field is there because of it.

## 2. Purpose

Forge is a delivery-control framework for Claude Code. Given a project with
product intent defined in a PID, it runs a bounded
implementation-and-independent-audit loop toward a delivery candidate,
while a Human retains product authority and final acceptance.

It is doctrine, agent contracts and a handful of dependency-free operator
scripts. It is not application runtime, and governed applications never
import it.

## 3. Target Outcome

A human — including one who has never seen this repository — can clone it,
run `./ops/bootstrap`, point a PL session at a project with a PID, and get
the same governed loop everyone else gets: bounded Engineer dispatches, a
genuinely independent audit, PL-owned git history, and an evidence trail
that survives the session that produced it.

"Done" for Forge as a whole is not a fixed feature set. It is that the loop
holds under real delivery pressure, and that each failure of it observed in
practice becomes doctrine before it can recur. §13 defines what "done"
means for one such change.

## 4. Readers (adapted from §4 Users — see §0)

Forge is read by four parties, and a change to it must work for all four:

1. **A PL session** driving the loop — reads `.claude/skills/forge/SKILL.md`
   as its operating procedure.
2. **An Engineer dispatch** — reads `.claude/agents/forge-engineer.md`,
   with no memory of why any rule exists.
3. **An Auditor dispatch** — reads `.claude/agents/forge-auditor.md`, fresh,
   deliberately uninformed about the Engineer's reasoning.
4. **A human engineer standing Forge up cold**, on their own machine, on a
   project Forge has never seen, with none of this repository's context
   available. `ops/pl-startup-gate` depends on nothing but `git` and a POSIX
   shell precisely for this reader.

Reader 2 and reader 3 matter most for doctrine wording: neither has the
context that made a rule obvious. A rule that reads clearly only to whoever
wrote it has failed.

## 5. Presentation Target (adapted — see §0)

**Not applicable to Forge itself.** Forge ships no rendered surface; there
is nothing for a browser gate to verify. Declaring `FUNCTIONAL_ONLY` would
imply Forge had a user-facing surface it had chosen not to polish, which is
false.

**Forge's obligation is to other projects' targets.** A change to Forge must
not weaken:

- the presentation-target field itself, or its gating of the Auditor's
  real-browser requirement (`SKILL.md` §2, §6);
- the Auditor's mandatory browser verification at `PRODUCT_USABLE` and
  above (`.claude/agents/forge-auditor.md`);
- the rule that source-only review can never close a `PRODUCT_USABLE` PID.

That machinery is the sharpest thing Forge does. Weakening it is a
scope-change decision for the Human, never an implementation convenience.

## 6. Scope of a change to Forge

In scope:

- doctrine (`docs/`, `.claude/skills/forge/SKILL.md`);
- agent contracts (`.claude/agents/`);
- the operator scripts in `ops/`, which must stay dependency-free;
- committed git hooks in `scripts/hooks/`;
- self-test fixtures in `self-test/`, which exist to prove the loop
  end-to-end and are not Forge's product.

## 7. Non-Goals

Forge is not, and does not acquire: a scheduler; a durable
verification-history service; a standing regression suite that Engineers
inherit by default; a local-model benchmark or delegation harness; a task
queue; a dashboard; a runtime library for governed applications.

`docs/FORGE-NORTH-STAR.md#anti-bloat-doctrine` governs. The Claude-native
subagent loop already provides independent review; a second delegation
layer would duplicate it without a proven need.

**The specific failure mode this guards against:** a lesson learned in one
increment becoming a permanent mechanism everyone pays for afterwards. A
doctrine sentence that a dispatch reads is almost always the right shape;
a service that runs is almost never.

## 8. Architecture

See `docs/ARCHITECTURE.md`. In brief: the PL owns git and product
adjudication; Engineers implement in isolated worktrees with no commit
authority; Auditors review fresh, with zero inherited Engineer context.
Isolation and independence are the two properties everything else rests on,
and both have failed in practice before — see
`docs/ARCHITECTURE.md#auditor-isolation` and the worktree-isolation history
in `SKILL.md` §4.

## 9. Public Repository Security

The canonical GitHub repository is public. Never commit secrets, customer
data, private host information, or governed projects' application content.
`scripts/hooks/pre-commit` runs `gitleaks` and is wired via `core.hooksPath`
so the control is part of Forge's history rather than host-local
convenience.

Evidence files may name paths, commit SHAs and observed failures. They must
not carry a governed project's customer content.

## 10. Durable Truth

Everything lives in this repository: doctrine, decisions, evidence. Redis
or fabric may carry live messaging during a session; it holds nothing
durable. If it isn't in git, it didn't happen.

**And "in git" is necessary, not sufficient** — a correction goes where the
citation leads, not merely somewhere trackable. See
`docs/FORGE-NORTH-STAR.md#durable-truth`.

## 11. Git and GitHub

Canonical repository `maff0000/forge`, canonical branch `main`. Work
branches merge to `main` by PR. Commit authority rests with the PL, exactly
as for governed projects: an Engineer dispatched against Forge reports a
diff and does not commit it.

Forge holds itself to its own loop. A change to Forge is a PID, a dispatch,
an independent review and an evidence trail — not an edit because the PL
happened to think of something.

## 12. Quality and Verification

Forge's mechanical surface is small and honest about it:

- `./ops/pl-startup-gate <root>` must exit 0 only when PID, git repository
  and GitHub remote are all present, and must name precisely what is
  missing otherwise.
- `./ops/bootstrap` must remain executable and dependency-light.
- `self-test/` fixtures must remain runnable end-to-end.

**There is no mechanical test that a doctrine change is correct**, and this
PID does not pretend otherwise. Doctrine is verified by independent review
against §13, by a reader who did not write it. That is the honest
counterpart to the rule that a governed project's `PRODUCT_USABLE` criteria
cannot be closed by source review: here, the reviewable artifact is prose,
and the reviewer is an Auditor dispatch reading it as reader 2 or 3 from §4
would.

## 13. Acceptance Definition — what "done" means for a doctrine change

A doctrine change is complete only when all of the following hold. This is
the section the rest of this PID exists to support.

1. **It is traceable to an observed failure, not a hypothetical.** Doctrine
   earns its place by having cost something. A rule with no incident behind
   it is speculation, and speculation is how a framework bloats.
2. **It names the mechanism, not only the rule.** "Fingerprint the server"
   is a rule; "a port answering is not proof of which build answered, and a
   stale server from a prior dispatch nearly produced a false PRODUCT RED"
   is the mechanism. Reader 2 and reader 3 (§4) have no memory of the
   incident, so the mechanism has to travel with the rule or the rule
   erodes into ritual.
3. **It states what to do when the check fires**, not only how to detect the
   condition. A detection rule with no recovery leaves the next dispatch
   stuck at exactly the moment it most needs direction.
4. **It lives where its reader will meet it.** PL procedure in `SKILL.md`;
   Engineer obligations in `forge-engineer.md`; Auditor obligations in
   `forge-auditor.md`; cross-cutting principle in `docs/`. A rule filed
   where its actor does not read is not doctrine, it is a note.
5. **It does not duplicate or contradict doctrine already present.** Check
   what has already landed before writing — including doctrine landed by
   another author between sessions.
6. **It creates no standing system** (§7).
7. **It is checkable.** A later reader must be able to tell whether a given
   dispatch actually followed it. A rule no one can be shown to have broken
   cannot be enforced or improved.
8. **It survives an independent read.** An Auditor dispatch, given the
   diff and this PID, agrees the change meets 1–7 — specifically including
   the duplication check in 5, which the author is worst placed to perform.

## 14. Authority

Matt is Human/Product Authority for Forge. The PL may write, decompose,
implement, review and integrate doctrine changes inside this PID.

The PL must return to the Human before: weakening the presentation-target
machinery (§5); adding anything in §7's non-goals; changing the
authority model in `docs/FORGE-NORTH-STAR.md#authority-model`; or changing
what `ops/pl-startup-gate` requires.
