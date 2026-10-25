# FORGEV2-ACCESS-BOOTSTRAP-001 — Administrative Identity and Filesystem Boundary

**State:** Draft Work Order — no host change or engineering dispatch is authorized by this draft
**Parent PBI:** `FV2-001` — prerequisite work only; this does not implement the product capability
**Repository:** `maff0000/forgev2`
**Work Order artifact:** `work-orders/FORGEV2-ACCESS-BOOTSTRAP-001.md`
**GitHub tracking Issue:** Not yet assigned. Issue #2 is for ENGINE-PACKAGING-001 and is not this Work Order's tracking issue. A dedicated Issue URL is required before exact-version approval and execution.
**Documentation baseline:** `519b2f7559650614d25b5f16cdefdcbeea6bbc09`
**Governing FOUNDRY:** `aee86185aac6aa0d2ab7a243138c423292af191a`
**Applicable FOUNDRY sources:** [Work Order contract](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/work-order-contract.md), [secure engineering standard](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/standards/secure-engineering.md), and [Security by Design skill reference](https://github.com/maff0000/foundry/blob/aee86185aac6aa0d2ab7a243138c423292af191a/skills/security-by-design.md)
**Related decisions:** `FV2-D017` through `FV2-D021` in [DECISIONS.md](../DECISIONS.md)
**Authoritative access design:** [security/ACCESS_CONTROL.md](../security/ACCESS_CONTROL.md)
**Exact-version approval:** Pending; record the approved artifact SHA on the dedicated Issue after this artifact commit exists.

## 1. Purpose and authority

Establish only the initial non-root ForgeV2 service identities and the approved filesystem access boundary needed for later, separately authorized delivery. This is one controlled administrative change on the previously approved ForgeV2 development environment. It does not start ForgeV2, Claude Code, a plugin, an application, or an engineering Work Order.

Matt Scott is the designated administrator and sole privileged operator for this Work Order. CGPT Project Architect is the independent verifier of the recorded evidence and retains architectural acceptance. Matt retains product and operational-risk authority. Any exact-version approval must be explicit and recorded on this Work Order's dedicated GitHub Issue; this document's presence or branch does not authorize execution.

The current approved design is recorded in `FV2-D017`–`FV2-D021`: named-human identity direction; the two proposed service accounts; root reserved for administration; non-root engineering; manual bootstrap boundary and deferred autonomous cross-UID dispatch; and filesystem/credential controls not yet verified. Preserve those states. Do not report a proposed or fixture-tested control as effective on the VPS until the VPS check succeeds.

## 2. Target and verified starting conditions

- **Repository identity:** `maff0000/forgev2`; this Work Order's approved source revision is the exact-version-approved commit recorded on its dedicated Issue.
- **Source checkout:** `/srv/src/forgev2/main/`; **worktree parent:** `/srv/src/forgev2/worktrees/`. These are approved deployment-specific project paths, not global FOUNDRY defaults.
- **Administrative target:** The previously approved ForgeV2 development VPS. Its current host identity and access details are restricted operator evidence and must be reverified by Matt at execution. Do not place a hostname, IP, SSH alias, key fingerprint or access configuration in this public Work Order.
- **Expected VPS source-checkout HEAD:** `6671ef8e2558aede02a812dca4be7c8fd3dbd86a`, the last controlled source-sync result. This is a required starting baseline to reverify, not a claim that the VPS still has it. The repository's public documentation `main` has since advanced to this Work Order's documentation base; do not fetch or fast-forward the VPS during this administrative change. At execution, record repository identity, branch, exact HEAD, origin identity, cleanliness, registered worktrees and target ownership/modes in restricted pre-change evidence. If any differ from the listed expected execution state, stop for CGPT review; do not fetch, pull, reset, retarget or repair as part of this WO.
- **Last reported directory state:** The canonical checkout and Git metadata were root-owned; the worktree parent existed and was empty. This is not current verification. Recheck it before changes.
- **Protected paths:** `/srv/forgev2/` and `/srv/pacman/` must remain untouched. Their present state is not assumed; verify absence or record their actual state without reading sensitive contents. Do not create either path.
- **Current root administration:** Preserve Matt's existing root SSH access. Do not change SSH, keys, authorized-key files, firewall, users outside this WO, or IONOS settings. Verify a separate Matt administrative connection before and after the operation without publishing its details.

The exact GitHub tracking Issue and current VPS identity are unresolved at draft time. Both are entry gates, not values to infer.

## 3. Scope

### Authorized changes after all entry gates pass

1. Create only `forgev2-pl` and `forgev2-agent` as Debian system identities, each with its own private primary group, dynamically allocated UID/GID, `/usr/sbin/nologin`, no password, no sudo and a private home:
   - `/var/lib/forgev2/pl`, owned by `forgev2-pl:forgev2-pl`, mode `0700`.
   - `/var/lib/forgev2/agent`, owned by `forgev2-agent:forgev2-agent`, mode `0700`.
2. Create `/var/lib/forgev2` as an empty `root:root` parent, mode `0755`, only if absent. If it already exists with unexpected contents or ownership, stop; do not adopt or overwrite it.
3. After the disposable fixture passes, transfer ownership of only `/srv/src/forgev2/main/.git` and its contained Git administrative metadata to `forgev2-pl:forgev2-pl`. Preserve its existing permission bits unless a tested, explicitly listed metadata permission correction is necessary and approved. Do not recurse across the repository or change tracked source ownership/content.
4. Transfer only `/srv/src/forgev2/worktrees/` to `forgev2-pl:forgev2-pl` and set its mode to `0711`: PL can create/manage children; other identities can traverse a known child path but cannot list the directory. Each future WO worktree must use a separately authorized WO-specific group and child permissions; this WO does not create a production worktree or grant persistent agent membership in a general worktree group.
5. Use a disposable local Git fixture to prove the planned WO-specific group and worktree permissions, then remove that fixture and temporary fixture group/memberships.
6. Verify separate, root-controlled command invocations for both service UIDs with an explicitly constructed environment. These are shell/identity checks only; do not invoke Claude Code or ForgeV2.

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

No external human accounts; no SSH, firewall, credential, GitHub security, package, service, Claude Code, engine-installation, application, or repository-content changes; no Orchestrator automation; no specialist dispatch; no ForgeV1 changes; no changes under `/srv/forgev2/` or `/srv/pacman/`; no production worktree creation; no recursive ownership change over `/srv/src/forgev2/` or any tracked source; no Git fetch, pull, branch, commit or push on the VPS.

## 4. Roles, process boundary and execution limits

- **Administrator/operator:** Matt Scott. Performs the small, explicitly authorized root operations and records each command and result in the restricted administrator evidence.
- **Independent verifier:** CGPT Project Architect. Does not run the root commands; independently reviews sanitized before/after evidence and the positive/negative test results before acceptance.
- **Independent assurance:** CGPT must name the Auditor, Tester and DevSecOps assessors, with their identities and read/write boundaries, on the dedicated Issue before execution. Auditor independently reviews state and change evidence; Tester independently repeats the fixture and access tests; DevSecOps assesses the account, filesystem and credential boundaries. No reviewer may be silently omitted.
- **Engineer:** Not applicable to the authorized work because it changes only OS identities/permissions and contains no product or engine source implementation. CGPT must explicitly approve this role's inapplicability when approving the exact WO version.
- **PL:** The new `forgev2-pl` identity is a target of this bootstrap, not an assumed installed ForgeV2 PL runtime. Matt coordinates this one manual administrative change; this does not create autonomous PL-to-agent dispatch. PL-only Git authority is proved against a local fixture, not exercised against GitHub.
- **Specialist execution limits:** No ForgeV2 specialist agent is dispatched by this WO. Any independent review performed by an AI specialist remains subject to FOUNDRY's independent limit of four executions per specialist for this WO, including the first; fifth is prohibited, counts persist across resets, and exhaustion is FAIL with reason/evidence. The PL normally owns persisted specialist counters. As no operational PL exists yet, CGPT must resolve who holds that record before any AI reviewer is invoked; do not silently transfer that authority to the administrator.
- **Administrative attempt bound:** One controlled change window. Each planned mutation is attempted once. Any failed command, unexpected output or changed precondition is BLOCKED; no retry, alternate command, or additional mutation without a newly reviewed WO version.

Run independent identities only as distinct processes started by Matt's root-controlled administrative session. For example, after account creation:

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

1. A dedicated GitHub Issue exists for this WO and links this exact artifact path; the Issue is not #2. The reviewed commit SHA and explicit CGPT decision are recorded after the candidate commit exists. No self-referential SHA is embedded here.
2. The live GitHub `main`, candidate branch, repository identity, exact base, ancestry, clean working tree and changed-path scope have been verified. This execution uses the exact approved WO version; any later edit requires renewed approval.
3. Matt verifies the actual authorized VPS identity and access through the restricted operator record. The canonical checkout is the intended repository and path, its branch/HEAD/remote/working tree/worktree list are captured, and no user data or unexpected contents would be overwritten.
4. Current account/group state confirms both service account names and homes are unused, no conflicting UID/GID or group membership exists, and no unapproved sudo policy grants either identity privilege.
5. Exact ownership/mode manifests and Git state have been captured for the allowed targets and relevant parent paths. Root's current SSH access has been tested from an independent session.
6. The disposable fixture is in a newly allocated, empty temporary path. No live repo, hooks, inherited script, external code, network remote or real credential is used in the fixture.
7. CGPT has recorded exact-version approval, the Engineer-inapplicability rationale, independent reviewer appointments, and the person responsible for the required persisted execution records. No unresolved security or architectural blocker remains.
8. Restricted evidence storage is available. Public logs contain only sanitized outcomes and references, never host access details, credentials, fingerprints, secret contents or sensitive permission findings.

Any failed or unknown gate is **BLOCKED + reason + evidence**. Stop before mutation. The old root-owned checkout, historical host report, empty worktree report or a passing fixture does not substitute for current verification.

## 6. Disposable fixture and verification plan

Use a fresh local bare remote and working repository created with Git commands only at `/tmp/forgev2-access-bootstrap-001-fixture`; fail without touching it if that path already exists. Mark all remotes synthetic, make no network requests, run no hooks or inherited scripts. Use a temporary group named `forgev2-wo-access-bootstrap-001` containing only the two service identities:

```sh
addgroup --system forgev2-wo-access-bootstrap-001
adduser forgev2-pl forgev2-wo-access-bootstrap-001
adduser forgev2-agent forgev2-wo-access-bootstrap-001
```

Remove both supplementary memberships with `deluser <account> forgev2-wo-access-bootstrap-001`, then remove the empty fixture group with `delgroup --system --only-if-empty forgev2-wo-access-bootstrap-001`. Do not create a real ForgeV2 worktree.

The fixture's checked permission model is: PL-only ownership of the Git administrative directory and local bare remote; a PL-owned worktree root with the temporary group and mode `3770` (setgid and sticky); the `.git` pointer owned by PL and mode `0640`; and only the synthetic source tree group-writable by the WO group (directories setgid). Verify the exact object owners and modes after setup. The sticky root protects the PL-owned `.git` pointer from agent unlink/replacement; it is not accepted as proof by itself. Prove the full positive and negative table below. Do not carry fixture permissions to production worktrees in this WO.

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

## 7. Production changes after fixture passes

Re-capture and compare the exact pre-change state immediately before mutation. Stop if it changed. Then, in this order:

1. Create the two accounts and their private homes using the commands in §3. Verify `getent passwd`, `id`, `stat`, shell, dynamic IDs and absence from `sudo`.
2. As root, make only these two filesystem changes, after confirming the exact paths and their expected object types:

   ```sh
   chown -R forgev2-pl:forgev2-pl /srv/src/forgev2/main/.git
   chown forgev2-pl:forgev2-pl /srv/src/forgev2/worktrees
   chmod 0711 /srv/src/forgev2/worktrees
   ```

   The recursive `chown` is strictly confined to the Git administrative directory; it must not follow or include tracked source, linked worktrees outside `.git`, submodule contents or any other path. If inspection finds an unexpected symlink, gitdir indirection, mount, submodule complication, permission requirement, or target state, stop before `chown` and return to CGPT. Preserve existing `.git` mode bits; no other mode changes are authorized by this WO.
3. Recheck main's tracked tree/content, branch, HEAD, origin, clean state and registered worktrees. Confirm the only ownership differences are within `.git` and the stated worktree parent; no worktree was created.
4. Repeat the two separate `runuser` identity/environment checks and independent positive/negative filesystem tests against actual allowed paths. Do not execute GitHub operations, Claude Code, ForgeV2, ForgeV1, or any application code.
5. Verify Matt's root SSH access still works from a second independent session. SSH configuration and firewall state must be unchanged.

The last operation does not install an engine, create a human account, authorize a GitHub credential, or open engineering dispatch. Actual credential provisioning, Claude runtime approval and a PL process launcher remain separate gates.

## 8. Logs, evidence and communication

Use the dedicated Issue once created for sanitized status and approval provenance. Public repository records must not contain host identity/access data or restricted evidence.

Sanitized WO-specific log paths, created only if they do not already exist:

- `work-orders/logs/FORGEV2-ACCESS-BOOTSTRAP-001/ADMIN.log` — Matt writes administrative commands/results; CGPT reads.
- `work-orders/logs/FORGEV2-ACCESS-BOOTSTRAP-001/PL.log` — assigned PL writes persisted specialist execution state and aggregate status; Matt/CGPT read. No AI specialist dispatch is permitted unless the PL counter owner is resolved.
- `work-orders/logs/FORGEV2-ACCESS-BOOTSTRAP-001/AUDITOR.log` — appointed independent Auditor writes; PL/Matt/CGPT read.
- `work-orders/logs/FORGEV2-ACCESS-BOOTSTRAP-001/TESTER.log` — appointed independent Tester writes test procedure/results; PL/Matt/CGPT read.
- `work-orders/logs/FORGEV2-ACCESS-BOOTSTRAP-001/DEVSECOPS.log` — appointed independent DevSecOps reviewer writes; PL/Matt/CGPT read.

No Engineer log is applicable because Engineer is not dispatched. Store detailed pre/post host manifests, access test transcripts and any restricted security data only in Matt's restricted operator-controlled evidence location; do not publish its path or content. Reference it publicly by a non-sensitive evidence identifier. Record each reviewer PASS/FAIL, rationale, evidence reference and candidate identity. Any Engineer change would invalidate prior PASS results and restart applicable assurance; no such change is within scope.

## 9. Acceptance criteria

CGPT may accept completion only when all applicable items have independently verifiable evidence:

1. Exactly the two approved system identities exist with unique dynamically allocated IDs, private primary groups/homes, `nologin`, no password and no sudo; no human identity was created.
2. The fixture proves PL Git write authority, Engineer assigned-worktree source writes, `.git` pointer/metadata protection, PL credential denial to Engineer, and cross-directory denial, with every positive and negative result recorded.
3. Matt's separate root administrative SSH access succeeds before and after; no SSH/firewall/credential changes occurred.
4. On the actual host, only the approved targets changed: service account/home/group state; ownership within `/srv/src/forgev2/main/.git`; owner/mode of `/srv/src/forgev2/worktrees`. No tracked source content changed, no worktree was created, and `/srv/forgev2/` and `/srv/pacman/` were untouched.
5. PL and Engineer command processes ran as distinct UIDs with the declared clean environment; Engineer could not read the synthetic PL credential marker or reach PL credential files.
6. CGPT-appointed Auditor, Tester and DevSecOps reviewers report PASS against the same unchanged administrative candidate/evidence set; Engineer is explicitly approved as inapplicable. Any FAIL, missing reviewer, changed state or candidate ambiguity blocks acceptance.
7. Restricted before/after evidence supports every claim; public status claims no more than the evidence proves. The exact approved Work Order version and final outcome are recorded on its dedicated Issue.
8. Rollback is either not needed or completed and independently verified. This acceptance does not authorize engineering dispatch, Claude execution, GitHub credential use, or changes excluded by §3.

## 10. Stop conditions and rollback

Stop before further mutation and record **BLOCKED + reason + evidence** if repository/host identity, account state, permissions, Git metadata layout, worktree state, root access, fixture behavior, reviewer assignment, approval provenance, or any protected boundary differs from the gates. Do not retry a failed mutation, repair ownership, alter SSH, create an alternative group, use another host, or continue by assumption. Return the discrepancy to CGPT; Matt resolves operational/product risk decisions.

If a production mutation has begun and a later acceptance check fails, Matt performs only this rollback, recording each result:

1. Stop the two service-identity processes. Confirm no running process uses either account.
2. Preserve restricted logs and evidence outside the homes before account removal.
3. Restore the exact pre-change ownership/mode manifest: restore `root:root` ownership only within `/srv/src/forgev2/main/.git`; restore `/srv/src/forgev2/worktrees` to its recorded pre-change owner and mode (`root:root`, `0755` only if that was captured). Do not recursively alter the source checkout.
4. Remove any temporary fixture group memberships and group only after verifying it is empty; remove the fixture only by its unique marker and verify cleanup.
5. Remove the two newly created system identities only if they were created by this WO and their homes contain no retained evidence or user data: `deluser --system --remove-home forgev2-agent`, then `deluser --system --remove-home forgev2-pl`. If either matching primary group remains and is empty, remove it with `delgroup --system --only-if-empty <group>`. Otherwise lock/disable the identities, remove grants, preserve data, and report rollback as incomplete for CGPT direction. Do not remove or alter any pre-existing identity.
6. Re-run repository status, tree/content comparison, worktree listing, path ownership/mode, account/group and root SSH checks. If any baseline cannot be restored exactly, stop and report; no speculative repair.

Rollback does not touch `/srv/forgev2/`, `/srv/pacman/`, SSH configuration, credentials, firewall settings or repositories/remotes.

## 11. Approval and completion boundary

This candidate must first receive explicit CGPT exact-version approval, with artifact SHA and decision recorded on a dedicated Issue. Matt's administrator assignment, independent reviewer names, current target verification and execution-record ownership must also be present before execution. Once approved, the sole authorized operator is Matt within the bounded scope above. Any material deviation requires a new review.

After the change and independent evidence review, stop and return the completion report to CGPT and Matt. **This Work Order does not authorize ForgeV2 engineering implementation, specialist dispatch, installation, deployment, or merge.**
