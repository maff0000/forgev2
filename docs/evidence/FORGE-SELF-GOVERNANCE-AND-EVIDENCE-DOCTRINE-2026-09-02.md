# Forge Self-Governance + Evidence Doctrine — Audit Evidence

Audit of `PID.md` (Forge's own) and the evidence-doctrine increment. One
audit, dispatched fresh into a PL-built worktree with zero inherited
Engineer context, followed by a repair dispatch.

## A. Structured evidence block

```
AUDIT_VERDICT: GREEN
commit_sha: 3496de99432b6362de89b457553a6a89456ad011
base_compared: b2142b3c1169a2e20a2e4692e10031b0f4ed6224
browser_gate_applicable: no (PID §5 — Forge ships no rendered surface)
duplication_check_independently_performed: yes (mechanical + semantic)
13.1_traceable_to_observed_failure: yes, with qualification (F4)
13.2_mechanism_travels_with_rule: partial (F2)
13.3_states_what_to_do_when_it_fires: partial (F1)
13.4_lives_where_its_reader_meets_it: yes
13.5_no_duplication_or_contradiction: yes
13.6_creates_no_standing_system: yes (rule 14 scoping judged real, not nominal)
13.7_checkable_by_a_later_reader: partial (F1, F3)
13.8_survives_independent_read: yes — this report
findings: 5, none blocking. All five repaired in 3fe0c26.
confidence: high
```

Repaired at `3fe0c26`. `3496de9` is cited by SHA above and was not
rewritten — see `docs/FORGE-NORTH-STAR.md#durable-truth`.

## B. What this increment did

Forge failed its own startup gate. `ops/pl-startup-gate` refuses to let a
PL act on a project without a PID, and `/srv/forge` had none — a gap that
stood through every increment in this repository, **including the one that
wrote the gate**. `PID.md` (`37f6822`) closes it.

Two template fields are adapted rather than answered, with a §0 saying so:
Forge has no end users, so §4 names its four actual readers; Forge has no
rendered surface, so §5 declares no presentation target for Forge itself
and instead binds Forge to the targets of projects it governs. §13 defines
what "done" means for a doctrine change, and is what this audit tested
against.

`3496de9` then folded in seven lessons from a five-increment run against a
governed project.

## C. The audit's primary job — duplication (§13.5)

Two doctrine commits (`61b68a0`, `b2142b3`) landed from a different author
shortly before this increment. **The author of a diff is the worst-placed
party to check it for duplication, which is why §13.8 exists.**

The Auditor did not accept the author's claim. It extracted every added
line from both ranges, normalised to lowercase word streams, and compared
8-gram shingle sets: **28 shingles overlapping, 0.59% of the new diff**. It
then reconstructed every overlapping passage rather than trusting the
percentage.

Result: five overlaps are pre-existing Auditor gate steps appearing as
additions only because inserting a step renumbered them (bodies
byte-identical, leading digit changed); one is a citation string; one is
`PID.md` §13.2 deliberately *quoting* the fingerprint rule as its worked
example of "mechanism, not only the rule."

**The Engineer's claim was accurate in substance but imprecise in
wording** — it said the only shared text was renumbered steps; there were
two further hits, both legitimate. Nothing concealed, but the claim was
tighter than the fact.

A semantic pass followed, which shingles cannot do: four genuine
adjacencies checked, none duplicative. Notably
`EVIDENCE-DOCTRINE.md#refutations` *cites* the prior durable-truth doctrine
rather than restating it — positive evidence the prior commits were
actually read.

## D. The five findings, and why F1 is the model

**F1 — self-demonstrating, and the most valuable kind of doctrine
finding.** The Auditor tried to apply the new non-vacuity step to a
feature-addition case and **could not tell what to do**: the step is
written entirely from a bug-fix frame ("confirm the check still fails
against the unfixed behaviour"), but a feature absent at base makes the
check fail trivially. The `n/a` value existed in the evidence block with no
text saying when it applied.

Separately, step 4 said failing to establish non-vacuity "is a finding, not
a pass" while the **Verdict rules** — the text that actually defines
GREEN — never mentioned it. An Auditor could record
`non_vacuity_established: no` and return GREEN without breaking a stated
rule.

"This reads well but I could not tell how to follow it" is a legitimate and
high-value finding on a doctrine change, and only a reader without the
author's context can produce it.

**F2 — the artifact contradicted its own commit message.** `3496de9`
claimed each role file carried its obligation "with a compressed incident,
so the rule stands even if the reader never opens the doc." Only Provenance
had one. The Auditor's evidence is unanswerable and specific to its
position: *"my own system prompt is `forge-auditor.md`, and I would not
have opened `docs/EVIDENCE-DOCTRINE.md` had this task not told me to."* A
pointer to a `docs/` file is a rule the dispatch must **choose** to follow.

Repaired in the artifact, not by weakening the claim.

**F3 — a rule nobody could be shown to have followed.** `SKILL.md` §6's
authoring test ("would you give this same instruction to an Auditor on a
different PID?") is applied privately at compose time and leaves no
artifact; the dispatch prompt was preserved nowhere. §13.7 requires a later
reader be able to tell. §8 now requires the Auditor's dispatch prompt to
land in the evidence trail beside its verdict.

**F4 — the finding the PL asked for and got.** None of the seven additions
cited a locatable record. `61b68a0` named its source evidence file;
`3496de9` named nothing. As written, §13.1 promised more than the diff
delivered: **doctrine traceable to an incident narrated by its author** is
a weaker claim than "traceable." Nine citations added.

**F5** — one restated kill mandate, cut.

## E. A trim target that failed its own doctrine

The audit recommended removing "roughly 40-60 lines with no mechanism
lost", and the PL passed that to the repair dispatch as a target.

**The Engineer pushed back rather than meeting it, and was right.** The
audit's own itemised fat — rule 8's wall, rule 14's anecdote, the doc
preamble, the F5 clause — totals about 20-24 lines, not 40-60. The headline
number was not attributable to the itemisation that was supposed to support
it. Reaching net -40 would have required deleting the doc's recovery
bullets, which are what §13.3 requires and which appear nowhere else.

That is precisely the **Attribution** failure this increment's own doctrine
describes: a number including contributions that were never established.
The doctrine caught its own auditor, one dispatch after being written.

Outcome: net **+49 lines** while repairing five findings, four of which are
additive by construction. Rule 14 compressed 17→13 with every mechanism
intact. The PL accepted the pushback rather than pressing a target its
source could not support.

## F. Rule 14's first outing

The repair Engineer reported rule 14 as **`n/a`, with its reasoning
stated** rather than omitted: it added no automated tests, and `PID.md` §12
says outright that no mechanical test can establish a doctrine change
correct. It also named what the load-bearing gate actually is — PL review
and an independent read against §13.

That is the rule working as intended on its first use: a scoped trigger
that does not fire, reported rather than silently skipped.

## G. Method note — the PL was bound by its own PID

`PID.md` §11 states that a change to Forge is "a PID, a dispatch, an
independent review and an evidence trail — not an edit because the PL
happened to think of something."

The PL wrote that in `37f6822` and was bound by it immediately: rather than
authoring the doctrine directly — which would have been faster, since the
PL held the incidents — it dispatched an Engineer with the incidents and
§13 as the acceptance standard. The substantive reason is §4: **a rule that
reads clearly only to whoever wrote it has failed**, and an author cannot
test that on their own prose.

Both dispatches were verified in both directions before use:
`PROJECT_ROOT`'s commits resolve inside each worktree, and a commit
existing only in the governed project does not. No Engineer committed
anything.

**One PL error, caught and corrected:** a `cd` into the Engineer's worktree
persisted through a compound command, so `git merge --ff-only` ran inside
that worktree and merged its branch into itself. It reported "Already up to
date" and the following `git log` looked correct because it too ran in the
worktree. The commit was stranded off the PL branch. Caught by checking
both branches explicitly rather than trusting output just read — the same
discipline `EVIDENCE-DOCTRINE.md#provenance` demands of a measurement.

## H. Open — for the Human, not adjudicated here

**Nothing in Forge governs the aggregate size of its own doctrine.** The
Auditor measured this increment at +31% across the three role files, plus a
new referenced document — **+54% total in one increment**, the fourth
doctrine batch in a single day.

§13.1 keeps each addition individually honest. §7's non-goals list
*systems*, not *pages*. So Forge's anti-bloat doctrine polices mechanisms
it will never build while ignoring the prose it produces every increment.
A doctrine surface a fresh dispatch must read end-to-end has a working
limit, and no rule fires when it is reached.

The Auditor proposed a consolidation trigger in §13 or §7: past a
threshold, the next doctrine change compresses before it adds. The repair
Engineer independently identified the same lever from the other side —
whether `EVIDENCE-DOCTRINE.md` should keep full narrations now that all
three role files carry compressed ones with citations.

**Deliberately not acted on.** It is a new governing rule originated by the
review, not a repair of what was written, and it changes how Forge
constrains itself. That is a Human decision.

## I. Carried forward

1. The consolidation question in §H.
2. `port_released_verified` sits in an evidence block scoped to
   `PRODUCT_USABLE`+ audits. An Auditor on a `FUNCTIONAL_ONLY` PID that
   starts a server has step 10's obligation but no field to record it in.
3. `.claude/agents/forge-auditor.md` hard-codes `/srv/forge/...` as a
   location, which reads oddly beside the hub-model material added later.
   Pre-existing.
4. Two pre-existing broken anchors, at `docs/ARCHITECTURE.md:18` and
   `.claude/skills/forge/SKILL.md:145`. Untouched by this increment;
   identified by the Auditor's cross-reference sweep.
