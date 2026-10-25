# FORGEV2-ACCESS-BOOTSTRAP-001 — Administrative Identity and Filesystem Boundary

**State:** Supervised-execution amendment review candidate — no host change or engineering dispatch is authorized by this candidate
**Parent PBI:** `FV2-001` — prerequisite work only; this does not implement the product capability
**Repository:** `maff0000/forgev2`
**Work Order artifact:** `work-orders/FORGEV2-ACCESS-BOOTSTRAP-001.md`
**GitHub tracking Issue:** [Issue #3](https://github.com/maff0000/forgev2/issues/3).
**Documentation baseline:** `519b2f7559650614d25b5f16cdefdcbeea6bbc09`
**Governing FOUNDRY:** `aee86185aac6aa0d2ab7a243138c423292af191a`
**Applicable FOUNDRY sources:** [Work Order contract](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/work-order-contract.md), [secure engineering standard](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/secure-engineering.md), and [Security by Design skill reference](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/skills/security-by-design.md)
**Related decisions:** `FV2-D017` through `FV2-D022` in [DECISIONS.md](../DECISIONS.md)
**Authoritative access design:** [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md)
**Previous exact-version approval:** The prior Work Order version was accepted at `b3b7f3e91232b1ab1498f3285f687bb0334d4ee0` on [Issue #3](https://github.com/maff0000/forgev2/issues/3). This execution-arrangement amendment requires fresh exact-version review; record its approved artifact SHA and decision on Issue #3 after the candidate commit exists.

## 1. Purpose and authority

Establish only the initial non-root ForgeV2 service identities and the approved filesystem access boundary needed for later, separately authorized delivery. This is one controlled administrative change on the previously approved ForgeV2 development environment. Under `FV2-D022`, Matt may use the existing root-local Claude Code installation as a directly supervised command executor for this Work Order only, after all applicable gates pass. It does not start ForgeV2, a ForgeV2 plugin or agent, an application, or an engineering Work Order.

Matt Scott is the designated administrator and sole privileged operator for this Work Order. CGPT Project Architect is the independent verifier of the recorded evidence and retains architectural acceptance. Matt retains product and operational-risk authority. Any exact-version approval must be explicit and recorded on this Work Order's GitHub Issue at [Issue #3](https://github.com/maff0000/forgev2/issues/3); this document's presence or branch does not authorize execution.

The current approved design is recorded in `FV2-D017`–`FV2-D021`: named-human identity direction; the two proposed service accounts; root reserved for administration; non-root engineering; manual bootstrap boundary and deferred autonomous cross-UID dispatch; and filesystem/credential controls not yet verified. Preserve those states. Do not report a proposed or fixture-tested control as effective on the VPS until the VPS check succeeds.

## 2. Target and verified starting conditions

- **Repository identity:** `maff0000/forgev2`; this Work Order's approved source revision is the exact-version-approved commit recorded on [Issue #3](https://github.com/maff0000/forgev2/issues/3).
- **Source checkout:** `/srv/src/forgev2/main/`; **worktree parent:** `/srv/src/forgev2/worktrees/`. These are approved deployment-specific project paths, not global FOUNDRY defaults.
- **Administrative target:** The previously approved ForgeV2 development VPS. Its current host identity and access details are restricted operator evidence and must be reverified by Matt at execution. Do not place a hostname, IP, SSH alias, key fingerprint or access configuration in this public Work Order.
- **Expected VPS source-checkout HEAD:** `6671ef8e2558aede02a812dca4be7c8fd3dbd86a`, the last controlled source-sync result. This is a required starting baseline to reverify, not a claim that the VPS still has it. The repository's public documentation `main` has since advanced to this Work Order's documentation base; do not fetch or fast-forward the VPS during this administrative change. At execution, record repository identity, branch, exact HEAD, origin identity, cleanliness, registered worktrees and target ownership/modes in restricted pre-change evidence. If any differ from the listed expected execution state, stop for CGPT review; do not fetch, pull, reset, retarget or repair as part of this WO.
- **Last reported directory state:** The canonical checkout and Git metadata were root-owned; the worktree parent existed and was empty. This is not current verification. Recheck it before changes.
- **Protected paths:** `/srv/forgev2/` and `/srv/pacman/` must remain untouched. Their present state is not assumed; verify absence or record their actual state without reading sensitive contents. Do not create either path.
- **Current root administration:** Preserve Matt's existing root SSH access. Do not change SSH, keys, authorized-key files, firewall, users outside this WO, or IONOS settings. Verify a separate Matt administrative connection before and after the operation without publishing its details.

The current VPS identity is unresolved at draft time and remains an entry gate, not a value to infer. Use [Issue #3](https://github.com/maff0000/forgev2/issues/3) as the Work Order tracking and approval record.

## 3. Scope

### Authorized changes after all entry gates pass

1. After all entry gates and the pre-change capture pass, create only `forgev2-pl` and `forgev2-agent` as Debian system identities, each with its own private primary group, dynamically allocated UID/GID, `/usr/sbin/nologin`, no password, no sudo and a private home:
   - `/var/lib/forgev2/pl`, owned by `forgev2-pl:forgev2-pl`, mode `0700`.
   - `/var/lib/forgev2/agent`, owned by `forgev2-agent:forgev2-agent`, mode `0700`.
2. Create the restricted log root under `/var/log/forgev2-access-bootstrap-001/logs/` after baseline capture; this evidence path is outside the source checkout and engine installation.
3. Use a production-equivalent disposable Git fixture with those identities and temporary WO-specific group membership. Freeze and review the fixture results before touching live Git metadata or worktree-parent permissions.
4. Only after fixture PASS and CGPT's recorded fixture review, transfer ownership of only `/srv/src/forgev2/main/.git` and its contained Git administrative metadata to `forgev2-pl:forgev2-pl`. Preserve its existing permission bits. Do not recurse across the repository or change tracked source ownership/content.
5. Transfer only `/srv/src/forgev2/worktrees/` to `forgev2-pl:forgev2-pl` and set its mode to `0711`: PL can create/manage children; other identities can traverse a known child path but cannot list the directory. Each future WO worktree must use a separately authorized WO-specific group and child permissions; this WO does not create a production worktree or grant persistent agent membership in a general worktree group.
6. Verify production boundaries and Matt's administrative access, then freeze a single administrative candidate identity for independent review. Never write logs or test artifacts under `/srv/src/forgev2/main/` or `/srv/forgev2/`.

### Exact proposed account commands

Run only after capturing pre-change state and confirming both names and home paths are unused. If `/var/lib/forgev2` is absent, create the parent first; if it exists, verify it is the expected empty `root:root` directory and leave it unchanged:

```sh
install -d -o root -g root -m 0755 /var/lib/forgev2  # only when absent after preflight
adduser --system --group --home /var/lib/forgev2/pl \
  --shell /usr/sbin/nologin --no-create-home forgev2-pl
adduser --system --group --home /var/lib/forgev2/agent \
  --shell /usr/sbin/nologin --no-create-home forgev2-agent
install -d -o forgev2-pl -g forgev2-pl -m 0700 /var/lib/forgev2/pl
install -d -o forgev2-agent -g forgev2-agent -m 0700 /var/lib/forgev2/agent
```

If `/var/lib/forgev2` already exists as the expected empty root-owned parent, leave it unchanged. Do not force UID/GID numbers or add either account to `sudo`, SSH-login groups, or unrelated groups.

### Explicit exclusions

No external human accounts; no SSH, firewall, credential, GitHub security, package, service, Claude Code installation or configuration changes; no Claude Code use except as the directly supervised command executor permitted by `FV2-D022`; no ForgeV2 plugin, engine agent, ForgeV1, or application execution; no Orchestrator automation; no specialist dispatch; no engine-installation or application changes; no changes under `/srv/forgev2/` or `/srv/pacman/`; no production worktree creation; no recursive ownership change over `/srv/src/forgev2/` or any tracked source; no Git fetch, pull, branch, commit or push against the live ForgeV2 repository or any GitHub remote. Git operations are permitted only in the disposable local fixture described in §6.

## 4. Roles, process boundary and execution limits

- **Administrator/operator:** Matt Scott. Performs the small, explicitly authorized root operations and records each command and result in the restricted administrator evidence.
- **Supervised command executor:** The existing root-local Claude Code installation may be proposed to issue commands for this administrative Work Order only. Matt remains the accountable administrator and must explicitly approve each privileged command or tightly bounded stage before execution; stage approval identifies the exact commands, targets, and stop conditions it covers. Claude has no authority to select, expand, substitute, retry, or approve privileged changes. There is no unattended execution, permission bypass, persistent blanket command approval, or alternative execution route. Before any use, verify and record in restricted evidence the exact executable, version, ownership, configuration, and relevant session-state side effects. Existing Claude provenance and security uncertainty remains a gate; this decision is not runtime or supply-chain approval. Unexpected session-state writes or effects outside the approved scope are a stop condition. Do not run a ForgeV2 plugin, engine agent, or application.
- **Independent verifier:** CGPT Project Architect. Does not run the root commands; independently reviews sanitized before/after evidence and the positive/negative test results before acceptance.
- **Independent assurance:** CGPT must name the Auditor, Tester and DevSecOps assessors, with their identities and read/write boundaries, on [Issue #3](https://github.com/maff0000/forgev2/issues/3) before execution. Auditor independently reviews state and change evidence; Tester independently repeats the fixture and access tests; DevSecOps assesses the account, filesystem and credential boundaries. No reviewer may be silently omitted.
- **Engineer:** Not applicable to the authorized work because it changes only OS identities/permissions and contains no product or engine source implementation. CGPT must explicitly approve this role's inapplicability when approving the exact WO version.
- **PL:** The new `forgev2-pl` identity is a target of this bootstrap, not an assumed installed ForgeV2 PL runtime. Matt coordinates this one manual administrative change; this does not create autonomous PL-to-agent dispatch. PL-only Git authority is proved against a local fixture, not exercised against GitHub.
- **Specialist execution limits:** No ForgeV2 specialist agent is dispatched by this WO. Any independent review performed by an AI specialist remains subject to FOUNDRY's independent limit of four executions per specialist for this WO, including the first; fifth is prohibited, counts persist across resets, and exhaustion is FAIL with reason/evidence. The PL normally owns persisted specialist counters. As no operational PL exists yet, CGPT must assign the counter owner before any AI reviewer is invoked; do not silently transfer that authority to the administrator. Auditor, Tester, and DevSecOps must be appointed and remain independent of the executing Claude session. Reviewer identities, counter ownership, and restricted evidence handling must be recorded before any mutation.
- **Administrative attempt bound:** One controlled change window. Each planned mutation is attempted once. Any failed command, unexpected output or changed precondition is BLOCKED; no retry, alternate command, or additional mutation without a newly reviewed WO version.

### Mandatory supervised checkpoints

1. **Pre-execution:** Reverify authority, exact approved Work Order, host/repository state, all entry gates, reviewer appointments, execution-counter ownership, restricted evidence handling, and the approved Claude executable/version/configuration/session-state evidence. Matt explicitly approves starting the bounded stage.
2. **Accounts:** Matt explicitly approves the account-creation command or tightly bounded account-creation stage; verify both service identities and homes before continuing.
3. **Fixture:** Matt explicitly approves fixture setup and each planned fixture command or bounded test stage. Run the positive and negative tests exactly within §6; freeze the results.
4. **Fixture acceptance:** Stop until CGPT records acceptance of the frozen fixture evidence. No live Git ownership or worktree-parent change may precede that acceptance.
5. **Live permissions:** Matt explicitly approves each live permission command or tightly bounded permission-change stage. Recheck the captured baseline first; stop on any difference.
6. **Evidence and assurance:** Freeze the final evidence candidate and obtain independent Auditor, Tester, and DevSecOps assessments against it. Reviewer work remains outside the executing Claude session.

At every checkpoint, a failed command/test, changed environment, unexpected path, missing approval, or failed prerequisite means stop and report **BLOCKED + reason + evidence**. No retry or alternate execution route is permitted. Rollback uses only the exact targets and captured baseline in §10, under Matt's explicit authorization and the same supervised execution boundary. If that execution route is unavailable, stop and obtain CGPT/Matt direction; do not substitute another route.

Run independent identities only as distinct processes started by Matt's root-controlled administrative session, including through the supervised executor only after Matt approves the exact command or bounded stage. For example, after account creation:

```sh
runuser -u forgev2-pl -- /usr/bin/env -i \
  HOME=/var/lib/forgev2/pl USER=forgev2-pl LOGNAME=forgev2-pl \
  PATH=/usr/bin:/bin TERM=dumb /bin/sh
runuser -u forgev2-agent -- /usr/bin/env -i \
  HOME=/var/lib/forgev2/agent USER=forgev2-agent LOGNAME=forgev2-agent \
  PATH=/usr/bin:/bin TERM=dumb /bin/sh
```

These invocations intentionally start separate non-login shells. The agent environment must contain no `SSH_AUTH_SOCK`, `GIT_ASKPASS`, GitHub token variables, PL home, or other inherited credential path. Do not infer that a subprocess or Claude subagent changes UID. Autonomous cross-UID dispatch remains deferred under `FV2-D020`.

## 5. Entry gates

Before any change, Matt records evidence that all gates pass:

1. [Issue #3](https://github.com/maff0000/forgev2/issues/3) links this exact artifact path. The reviewed commit SHA and explicit CGPT decision are recorded after the candidate commit exists. No self-referential SHA is embedded here.
2. The live GitHub `main`, candidate branch, repository identity, exact base, ancestry, clean working tree and changed-path scope have been verified. This execution uses the exact approved WO version; any later edit requires renewed approval.
3. Matt verifies the actual authorized VPS identity and access through the restricted operator record. The canonical checkout is the intended repository and path, its branch/HEAD/remote/working tree/worktree list are captured, and no user data or unexpected contents would be overwritten.
4. Current account/group state confirms both service account names and homes are unused, no conflicting UID/GID or group membership exists, and no unapproved sudo policy grants either identity privilege.
5. Exact ownership/mode manifests and Git state have been captured for the allowed targets and relevant parent paths. Root's current SSH access has been tested from an independent session.
6. The disposable fixture is in a newly allocated, empty temporary path. No live repo, hooks, inherited script, external code, network remote or real credential is used in the fixture.
7. CGPT has recorded exact-version approval, the Engineer-inapplicability rationale, independent reviewer appointments and separation from the executing Claude session, the persisted execution-counter owner, and the restricted evidence handler. The exact Claude executable, version, ownership, configuration, and relevant session-state side effects have been verified and recorded; its provenance/security gate is resolved for this bounded use. Matt has explicitly approved the supervised execution arrangement and no unresolved security or architectural blocker remains.
8. Restricted evidence storage is available. Public logs contain only sanitized outcomes and references, never host access details, credentials, fingerprints, secret contents or sensitive permission findings.

Any failed or unknown gate is **BLOCKED + reason + evidence**. Stop before mutation. The old root-owned checkout, historical host report, empty worktree report or a passing fixture does not substitute for current verification.

## 6. Disposable fixture and verification plan

The two service accounts and homes are created after §5 entry-gate verification and pre-change capture, before fixture work. Then create the WO log root outside both the source checkout and engine installation, with owner `root:root` and mode `0700`; fail if it already exists. The initial pre-change capture is made by Matt before either mutation and retained in the restricted operator evidence store. Create the log root with:

```sh
install -d -o root -g root -m 0700 /var/log/forgev2-access-bootstrap-001/logs
```

Next, build a fresh local bare remote and working repository using Git commands only at `/tmp/forgev2-access-bootstrap-001-fixture`; fail without touching it if that path already exists. Mark all remotes synthetic, make no network requests, run no hooks or inherited scripts. Use a temporary group named `forgev2-wo-access-bootstrap-001` containing only the two service identities:

```sh
addgroup --system forgev2-wo-access-bootstrap-001
adduser forgev2-pl forgev2-wo-access-bootstrap-001
adduser forgev2-agent forgev2-wo-access-bootstrap-001
```

Keep the fixture and group available until CGPT has reviewed the frozen fixture snapshot. After snapshot review passes, remove both memberships and the empty group, then remove the fixture by its unique marker and verify cleanup before touching production metadata:

```sh
deluser forgev2-pl forgev2-wo-access-bootstrap-001
deluser forgev2-agent forgev2-wo-access-bootstrap-001
delgroup --system --only-if-empty forgev2-wo-access-bootstrap-001
```

Do not create a real ForgeV2 worktree.

The fixture must reproduce the production topology: a root-owned canonical checkout directory and root-owned tracked source; PL-owned Git administrative metadata; a PL-owned sibling worktree parent; separate PL and Engineer UIDs; and a temporary WO group. Create a real linked worktree beneath the fixture's sibling parent. The fixture's checked permission model is: PL-only ownership of Git administrative metadata and the local bare remote; a PL-owned worktree root with the temporary group and mode `3770` (setgid and sticky); the `.git` pointer owned by PL and mode `0640`; and only the synthetic source tree group-writable by the WO group (directories setgid). Verify exact object owners and modes after setup. The sticky root protects the PL-owned `.git` pointer from agent unlink/replacement; it is not accepted as proof by itself.

As PL, test repository safety and the required operations explicitly: inspect the canonical root-owned checkout without changing it; use only the approved explicit Git-directory/worktree operation to create, inspect and remove the fixture worktree; and demonstrate PL can update fixture refs and push to the local bare remote. As administrator, verify the same fixture's expected repository identity, ownership, refs, worktree registration and clean state. As Engineer, demonstrate source-file writes in the assigned fixture worktree while writes to Git administrative metadata, refs, index, hooks, the `.git` pointer, parent and sibling worktrees fail. No `safe.directory` wildcard, broad ownership change, or persistent/global Git configuration change may be added to make a test pass. If Git rejects the planned PL operation under the approved ownership model, stop and report BLOCKED to CGPT; do not weaken the fixture or live boundaries. Do not carry fixture permissions to production worktrees in this WO.

Freeze the fixture setup, command transcript, owner/mode manifest and test results as a read-only fixture evidence snapshot. CGPT reviews that snapshot before the live metadata/worktree-parent changes. If any fixture check fails, do not touch live Git metadata or `/srv/src/forgev2/worktrees`; follow the bounded rollback for accounts and fixture resources already created.

The fixture must demonstrate:

| Check | Positive result required | Negative result required |
| --- | --- | --- |
| Distinct process identity | `id` and process credentials show PL and Engineer have different nonzero UIDs and intended groups | Neither identity runs as root or gains `sudo`; `sudo -n -l` grants neither privilege |
| PL Git authority | PL can create a branch, stage, commit and push to the fixture's local bare remote | Agent cannot write refs, index, objects, hooks, or remote refs; no GitHub operation occurs |
| Engineer worktree access | Agent can create, edit and remove files only within its assigned fixture worktree group | Agent cannot write the fixture parent, another WO child, or PL-owned files outside assigned writable source paths |
| `.git` pointer protection | PL can read/use its worktree pointer and Git metadata | Agent cannot replace, unlink or modify the `.git` pointer or Git administrative metadata, and cannot commit/push |
| Credential separation | PL can read a clearly synthetic mode-`0600` marker in a PL-only test home | Agent cannot read that marker or PL home; agent environment has no credential variables or SSH agent socket |
| Cross-directory boundary | PL can traverse/create only where its test grant permits | Agent cannot write canonical source, sibling fixture, root/admin home, or protected engine/application paths; absent protected paths remain absent |
| Environment hygiene | Both sessions contain only the declared environment allowlist | No PL variables, credential paths, SSH socket, askpass variables, or root environment values are present in agent process |

Record test commands, effective UID/GID/groups, filesystem owner/mode observations, exit status and sanitized evidence. If a negative test succeeds unexpectedly, or a positive test cannot be demonstrated, stop; do not weaken permissions to make the test pass. Delete only the uniquely marked disposable fixture after independent review and verify its cleanup. Do not use ACL tooling or install packages; `setfacl`/`getfacl` were not present in the prior read-only inspection.

## 7. Production changes after fixture review

Only after the fixture snapshot receives CGPT review and PASS, re-capture and compare the exact pre-change state immediately before the two live permission changes. Stop if it changed. Accounts and homes already exist from the earlier authorized step. Then:

1. Reconfirm `getent passwd`, `id`, `stat`, shell, dynamic IDs, group memberships and absence from `sudo` for both service identities.
2. As root, make only these two filesystem changes, after confirming the exact paths and their expected object types:

   ```sh
   chown -R forgev2-pl:forgev2-pl /srv/src/forgev2/main/.git
   chown forgev2-pl:forgev2-pl /srv/src/forgev2/worktrees
   chmod 0711 /srv/src/forgev2/worktrees
   ```

   The recursive `chown` is strictly confined to the Git administrative directory; it must not follow or include tracked source, linked worktrees outside `.git`, submodule contents or any other path. If inspection finds an unexpected symlink, gitdir indirection, mount, submodule complication, permission requirement, or target state, stop before `chown` and return to CGPT. Preserve existing `.git` mode bits; no other mode changes are authorized by this WO.
3. Recheck main's tracked tree/content, branch, HEAD, origin, clean state and registered worktrees. Confirm the only production ownership/mode differences are within `.git` and the stated worktree parent; no production worktree was created.
4. Repeat the two separate `runuser` identity/environment checks and independent positive/negative filesystem tests against actual allowed paths. Claude Code may act only as the supervised command executor under `FV2-D022`; do not execute GitHub operations, a ForgeV2 plugin or agent, ForgeV1, or any application code.
5. Verify Matt's root SSH access still works from a second independent session. SSH configuration and firewall state must be unchanged.
6. Freeze a read-only administrative evidence manifest at `/var/log/forgev2-access-bootstrap-001/evidence/ADMIN-CANDIDATE-MANIFEST.txt`. It lists the exact final account/group state, allowed ownership/mode changes, repository identity/HEAD/tracked-tree digest, fixture snapshot digest, production checks, Matt's explicit command/stage approvals, the supervised executor identity and verified runtime details, and SHA-256 digests of the underlying restricted evidence files. Compute `sha256sum /var/log/forgev2-access-bootstrap-001/evidence/ADMIN-CANDIDATE-MANIFEST.txt`; that digest is the single **Administrative Candidate ID**. Make the manifest and referenced evidence read-only before review. All three independent reviewers, working separately from the executing Claude session, assess that same ID. Their role logs are separate from the frozen manifest. Any subsequent account or permission change requires a new manifest/Candidate ID and invalidates every prior reviewer PASS.

The last operation does not install an engine, create a human account, authorize a GitHub credential, or open engineering dispatch. Claude runtime or supply-chain approval beyond the narrowly supervised command-executor use remains a separate gate, as does any PL process launcher.

## 8. Logs, evidence and communication

Use [Issue #3](https://github.com/maff0000/forgev2/issues/3) for sanitized status and approval provenance. Public repository records must not contain host identity/access data or restricted evidence. All WO-specific logs are created only under `/var/log/forgev2-access-bootstrap-001/logs/`, outside `/srv/src/forgev2/main/` and `/srv/forgev2/`. Matt creates the log directory as `root:root` mode `0700`; log files are `root:root` mode `0600`. If the directory exists before this WO, stop rather than reuse it. Create the evidence directory only after final production verification, at `/var/log/forgev2-access-bootstrap-001/evidence/`, with owner `root:root` mode `0700`. No log, manifest, or test artifact may be written into the canonical checkout or engine installation.

- `ADMIN.log` — Matt authors and writes the administrative command/results record; CGPT reads.
- `PL.log` — no PL agent/runtime is dispatched. Matt records `PL not dispatched; specialist invocation count zero` and the administrative coordination state. This is not represented as a PL-authored delivery log or a transfer of PL authority. CGPT/Matt read.
- `AUDITOR.log` — the appointed independent Auditor authors the findings; Matt stores the reviewer-supplied record verbatim and records its source/identity, receipt time and digest. CGPT/Matt read.
- `TESTER.log` — the appointed independent Tester authors the fixture and independent verification results; Matt stores the reviewer-supplied record verbatim and records its source/identity, receipt time and digest. CGPT/Matt read.
- `DEVSECOPS.log` — the appointed independent DevSecOps reviewer authors the security assessment; Matt stores the reviewer-supplied record verbatim and records its source/identity, receipt time and digest. CGPT/Matt read.

No Engineer log is applicable because Engineer is not dispatched. Detailed pre/post host manifests and any restricted security data remain in Matt's restricted operator evidence store; do not publish its location or contents. The frozen evidence manifest described in §7 and its referenced restricted files are read-only during review. Its SHA-256 is the single Administrative Candidate ID recorded in each reviewer log and on [Issue #3](https://github.com/maff0000/forgev2/issues/3). Reviewer reports are separate records and do not change that candidate. Any subsequent account or permission change creates a new candidate identity and invalidates all prior PASS results.

## 9. Acceptance criteria

CGPT may accept completion only when all applicable items have independently verifiable evidence:

1. Exactly the two approved system identities exist with unique dynamically allocated IDs, private primary groups/homes, `nologin`, no password and no sudo; no human identity was created.
2. The fixture proves PL Git write authority, Engineer assigned-worktree source writes, `.git` pointer/metadata protection, PL credential denial to Engineer, and cross-directory denial, with every positive and negative result recorded.
3. Matt's separate root administrative SSH access succeeds before and after; no SSH/firewall/credential changes occurred.
4. On the actual host, only the approved targets changed: service account/home/group state; ownership within `/srv/src/forgev2/main/.git`; owner/mode of `/srv/src/forgev2/worktrees`; and the restricted `/var/log/forgev2-access-bootstrap-001/evidence/` directory. No tracked source content changed, no worktree was created, and `/srv/forgev2/` and `/srv/pacman/` were untouched.
5. PL and Engineer command processes ran as distinct UIDs with the declared clean environment; Engineer could not read the synthetic PL credential marker or reach PL credential files.
6. CGPT-appointed Auditor, Tester and DevSecOps reviewers report PASS against the same unchanged administrative candidate/evidence set; Engineer is explicitly approved as inapplicable. Any FAIL, missing reviewer, changed state or candidate ambiguity blocks acceptance.
7. Restricted before/after evidence supports every claim; public status claims no more than the evidence proves. The exact approved Work Order version and final outcome are recorded on [Issue #3](https://github.com/maff0000/forgev2/issues/3).
8. Rollback is either not needed or completed and independently verified. This acceptance does not authorize engineering dispatch, ForgeV2 plugin or engine-agent execution, GitHub credential use, or changes excluded by §3.

## 10. Stop conditions and rollback

Stop before further mutation and record **BLOCKED + reason + evidence** if repository/host identity, account state, permissions, Git metadata layout, worktree state, root access, fixture behavior, reviewer assignment, approval provenance, or any protected boundary differs from the gates. Do not retry a failed mutation, repair ownership, alter SSH, create an alternative group, use another host, or continue by assumption. Return the discrepancy to CGPT; Matt resolves operational/product risk decisions.

If a production mutation has begun and a later acceptance check fails, Matt performs only this rollback, recording each result:

1. Stop the two service-identity processes. Confirm no running process uses either account.
2. Preserve restricted logs and evidence outside the homes before account removal.
3. If fixture testing failed **before** production permission changes, do not touch `/srv/src/forgev2/main/.git` or `/srv/src/forgev2/worktrees`; verify they still match the pre-change manifest. If production permission changes began, restore the exact pre-change ownership/mode manifest: restore ownership only within `/srv/src/forgev2/main/.git`; restore `/srv/src/forgev2/worktrees` to its captured owner/mode (`root:root`, `0755` only if that was captured). Do not recursively alter the source checkout.
4. Remove temporary fixture group memberships and the group only after verifying it is empty; remove the fixture only by its unique marker and verify cleanup.
5. Remove the two newly created system identities only if they were created by this WO and their homes contain no retained evidence or user data: `deluser --system --remove-home forgev2-agent`, then `deluser --system --remove-home forgev2-pl`. If either matching primary group remains and is empty, remove it with `delgroup --system --only-if-empty <group>`. Otherwise lock/disable the identities, remove grants, preserve data, and report rollback as incomplete for CGPT direction. Do not remove or alter any pre-existing identity.
6. Retain the root-only `/var/log/forgev2-access-bootstrap-001/` evidence as the rollback record; it is the only intentional new path retained after a rollback. Re-run repository status, tree/content comparison, worktree listing, path ownership/mode, account/group and root SSH checks. If any baseline cannot be restored exactly, stop and report; no speculative repair.

Rollback does not touch `/srv/forgev2/`, `/srv/pacman/`, SSH configuration, credentials, firewall settings or repositories/remotes.

## 11. Approval and completion boundary

This candidate must first receive explicit CGPT exact-version approval, with artifact SHA and decision recorded on [Issue #3](https://github.com/maff0000/forgev2/issues/3). Matt's administrator assignment, independent reviewer names, current target verification and execution-record ownership must also be present before execution. Once approved, the sole authorized operator is Matt within the bounded scope above. Any material deviation requires a new review.

After the change and independent evidence review, stop and return the completion report to CGPT and Matt. **This Work Order does not authorize ForgeV2 engineering implementation, specialist dispatch, plugin or engine-agent execution, installation, deployment, or merge.**
