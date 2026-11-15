# FV2-SYNC-001 — Trusted PL-owned synchronisation of exact approved Git baseline

**WORK ORDER CANDIDATE — engineering authority requires the subsequent explicit CGPT exact-commit approval on [ForgeV2 Issue #7](https://github.com/maff0000/forgev2/issues/7).**

## Problem, decision and outcome

FOUNDRY-approved application WOs cannot execute when the PL's canonical checkout is stale, because `forge-start` creates a WO worktree from local `main` without fetching and the PL guard forbids ordinary Git writes. The root Rogue session's `runuser ... git pull --ff-only` is denied by Claude's `[Undermining Oversight]` classifier. It is inappropriate to ask Matt to perform routine Git synchronisation manually.

**Outcome:** one normal ForgeV2 PL startup can, entirely within the trusted PL-owned plugin tooling, validate and fast-forward a clean canonical `main` from the expected GitHub repository to an **explicitly approved SHA** before creating the WO branch. It then executes a Work Order under existing independent-review and ledger rules. No Rogue-as-PL Git operation or classifier workaround.

The distinction is architectural: a trusted plugin command run **as the PL in the sanctioned PL session** owns its normal Git administration. Rogue continues to orchestrate but does not impersonate `forgev2-pl`. A rejected call to this supported tool remains BLOCKED; never use alternative wrappers or permission edits to hide a denial.

## Authoritative identity and constraints

- **WO:** `FV2-SYNC-001`
- **REPO:** `maff0000/forgev2`.
- **ISSUE:** https://github.com/maff0000/forgev2/issues/7
- **Source base:** `63b6b8ab6c6d3c12d1ef3f0aeabe2ca22fbefb82` (actual GitHub main and IONOS protected install on 2026-11-15). Reverify before work.
- **Development location:** **not** `/srv/forgev2/src` or any running ForgeV2 engine checkout. Use a separate `forgev2-pl`-owned (or properly authorised independent engineering PL) development checkout and isolated worktrees, verified by Rogue and named in the implementation intake. Actual development HOST/ROOT/WORKTREES must be populated from inspected evidence at dispatch; no guessed path or target-host substitution.
- **Delivery branch:** `forge/FV2-SYNC-001` only. No forced pushes, no changes to current protected live engine without a separately approved installation gate.
- **Governing FOUNDRY:** `maff0000/foundry` `GOVERNANCE.md`, `standards/work-order-contract.md`, `standards/secure-engineering.md` and `delivery/rogue-handoff.md`; FOUNDRY main reference `84fedf0a74017237aa1bd650d8560350c91c7f0e` at drafting; reverify.
- **Authority:** Matt expressly directed “fix it. this is a foundry/forgev2 failing someone and it is stupid” on 2026-11-15, referring to the inability of Rogue/PL to sync a stale checkout after an exact WO was approved. CGPT is responsible for the bounded engine correction and acceptance under adopted FOUNDRY governance. Matt's direction is not blanket permission to install unreviewed code, change access policies, bypass Claude's tool classifier or alter unrelated projects.
- **Credential boundary:** dedicated PL account and repo-specific Git authentication for engine development must be independently verified; the existing BLG deploy key cannot be reused for the ForgeV2 repository. No root Rogue Git credential may be passed into the PL.

## Implemented code scope

Only:
1. `plugin/bin/forge-start`
2. `plugin/lib/forgelib.py`
3. `plugin/skills/deliver/SKILL.md`
4. `plugin/README.md`
5. `plugin/ORCHESTRATOR.md`
6. `tests/test_forgev2.py` and narrowly scoped `tests/host/**` test fixture(s) if necessary
7. This WO and directly relevant delivery evidence under `docs/evidence/**` / `.forge/FV2-SYNC-001/**` as permitted by ForgeV2 delivery-record protocol.

No new third-party dependency, new login/subscription, root daemon, standalone always-on sync service, broad Git permission, altered specialist sandbox, changed execution counters, new merge authority or modifications to any application repository.

## Required implementation

A. **Explicit opt-in, pinned startup.** Add `forge-start --sync-main <EXPECTED_FULL_40_HEX_SHA>` for NEW WOs. This is not a fetch of “latest”; the SHA must be supplied by an approved WO/Architect record. A malformed/absent expected SHA when `--sync-main` is requested causes FAIL. Legacy `forge-start` with no sync option keeps its existing behaviour and test compatibility; document the hazard of stale local main and standardise the pinned form in the PL skill for WOs with exact main baseline.

B. **Safe sequencing before network/write.** In existing `forge-start`, before any fetch: require a non-root PL process, check actual hostname/verified target paths; `forgelib.check_repo` including exact single canonical `origin` fetch and push, effective URL rewrite rejection and non-redirected credentials; confirm top-level repo and PL owner; `HEAD` symbolic branch exactly `main`; clean canonical checkout including untracked files; no existing ledger for this WO and no conflicting active WO/sync attempt. Obtain a PL-private per-repo lock before any sync/worktree operation, retaining it across both to avoid races.

C. **Fetch and exact remote check.** In the trusted PL Python tool, run Git via subprocess argument arrays, never a shell; use the existing sanitised Git environment and existing repo-local `core.sshCommand`. Fetch only `refs/heads/main` from verified `origin`, with tags and submodule recursion disabled, fixed command/timeout and no user-supplied option injection. Disable repository-controlled hooks and fsmonitor for trusted mutations. Resolve the fetched commit object and require it to be **exactly** `--sync-main` SHA. If GitHub main moves, fail `REMOTE_BASE_CHANGED`; do not silently pick a newer (unapproved) tip.

D. **True FF or stop.** Check local `main` HEAD is an ancestor of the exact fetched commit. Fail before changing local main for any divergence, unexpected checkout state, branch mismatch, auth/network error or missing object. Fast-forward only using a fixed safe Git operation; NO reset, force, rebase, clean or merge commit. Verify clean working tree, canonical remote and new local HEAD exactly equal to the pinned approved SHA *before* creating a worktree or ledger. Journal whether the sync was a no-op or fast-forward and its old/new HEADs.

E. **Work Order identity and resume.** Create `forge/<WO>` exclusively from verified new local main, store `base_sha` and sync provenance in the protected ledger, and retain existing four-execution counters. Resuming an existing WO **never** performs another remote fetch or changes its recorded base. A mismatched supplied expected SHA for a resume is an error rather than permission to reinterpret work. No change to `forge-commit` / `forge-push` guard rules: specialists still cannot modify Git.

F. **Fail closed, no new infrastructure.** Every Git failure returns `BLOCKED`/specific reason before specialist dispatch. Do not print private key material, environment variables or sensitive remote output. The plugin stays portable to other FOUNDRY projects; there is no special BLG path or client-specific bypass in generic engine code.

## Must-pass tests and review

1. Offline local bare-remote fixture: stale clean `main` → pinned expected ref → correct FF and worktree base. Repeat same pinned SHA is no-op. Run without GitHub access; no production keys in tests.
2. Remote SHA newer/different from expected -> deterministic fail before main/worktree changes; no picking latest.
3. Dirty or untracked canonical changes; main divergence; wrong local branch; missing/full SHA mismatch; malformed SHA; unexpected remote URLs, URL rewrite; host mismatch, PL ownership mismatch and root execution -> fail closed.
4. Failure and interruption cases: no network, auth denied, fetch timeout, concurrent starts, post-fetch remote movement, hook/config injection probes, symlink roots or gitdir.
5. Existing ledger resume -> no fetch/no base change/no counter reset; only one new WO worktree and ledger on successful startup.
6. Verify invariant: all subsequent forge-commit/forge-push identity and gitleaks gates unchanged; guard still rejects direct PL git pull/fetch; all specialists remain offline/socket-less.
7. `python3 -m unittest discover -s tests -v` (complete engine suite) and real isolated PL-host smoke tests with intentionally stale checkout and test-only credentials; negative cases independently witnessed.
8. Independent Engineer, Auditor, Tester and DevSecOps on an unchanged committed head, identical candidate SHA and valid per-role execution counters. Any changed head restarts applicable review. A code review by CGPT alone is not independent verification.

## Longer-term automation and operational requirements

- The approved application WO must expose its exact expected base SHA in the intake/PL prompt; `KNOWN_COMMIT` alone is an ancestry/identity marker, not a remote-tip assertion. The new option must be distinguishable and tested.
- A fast-forward is routine **PL Git administration**, not new product scope. The PL may proceed without Matt's keyboard actions when this trust boundary is genuinely enforced.
- Rogue must monitor terminal status without asking Matt for another `runuser` or one-off Bash script; ChatGPT session wake-up and multi-project Gateway routing are separate limitations and not “fixed” by this WO.

## Stop, handover and deployment

The mission continues autonomously through the approved bounded code/test/review cycle once development PL authentication, correct host/ROOT/WORKTREES and normal platform permissions are genuinely verified. Report `BLOCKED` only for true missing access, origin identity, failed negative tests, exhausted specialist counters or policy/tool refusal; do not bypass them.

Rogue returns one `READY_FOR_CGPT` report with exact PR/candidate SHA, full tests, same-head independent verdicts, path diff and rollout/rollback plan. **No self-merge or live installation**. CGPT must separately review and approve the candidate; installation onto the root-owned protected ForgeV2 host is a distinct controlled operation. Preserve original installed SHA `63b6b8a` and tested rollback.

Pilot final acceptance: installed verified build can start BLG-WO-004 from pinned `22264ee4c7d8797b0900c1f98fd14887b05f0e1c` on the existing PL checkout without Matt acting as Git operator; it rejects incorrect remote tips and dirty/local-divergent branches. Only after this test may BLG-WO-004 resume. No change to that application's already-approved WO authority is implied.

**Exact version:** After this file is committed, CGPT must explicitly approve its full commit SHA and blob in [Issue #7](https://github.com/maff0000/forgev2/issues/7). Any subsequent amendment to this WO requires a new exact approval before dispatch.
