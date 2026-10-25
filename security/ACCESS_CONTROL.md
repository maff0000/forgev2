# ForgeV2 — Access Control and Security Decision Record

**State:** Living security record — initial administrative identities and scoped filesystem controls **IMPLEMENTED AND INDEPENDENTLY VERIFIED**; engineering runtime and delivery approval **PENDING**
**Updated:** 2026-10-25
**Governing framework:** FOUNDRY `aee86185aac6aa0d2ab7a243138c423292af191a`
**Engine source baseline:** `6671ef8e2558aede02a812dca4be7c8fd3dbd86a`
**Related Work Order:** `work-orders/ENGINE-PACKAGING-001.md`, approved for documentation merge only; specialist dispatch remains blocked.

This is the public-safe, evolving record of ForgeV2 human identities, delivery-process identities, permissions, recommendations, outstanding decisions, verification, and accepted changes. It is **not** an operational secrets inventory, a claim of enforcement, or authorisation to modify the host. Detailed host evidence, credentials, key fingerprints, network source rules, individual user records, and unresolved exposure findings belong in a restricted operator-controlled evidence record.

## 1. Objectives and authority

1. Attribute human requests and host access to a **named individual**, never a shared engineering login.
2. Reserve `root` for Matt's administration, recovery and specifically approved bootstrap actions; agent engineering must not run as root.
3. Separate Project Lead (PL) Git authority and credentials from Engineer execution. Specialists must not gain PL's SSH agent, credential files, tokens, Git metadata write authority or privileged launcher.
4. Keep installed engine files protected, and keep each application/project workspace independent of the engine and other projects.
5. Preserve the FOUNDRY chain: approved WO, PL-governed branch, independent Auditor/Tester/DevSecOps assessment, exact-candidate evidence, and four executions maximum per specialist.
6. Keep normal engineering non-interactive through **bounded worktree permissions and assessed Claude settings**, without disabling operating-system protections.
7. Use the IONOS-managed network perimeter selected by Matt; this record does not approve a host firewall or any network rule change.

**Authority:** Matt approves people and material operational risk. CGPT owns the project-specific security architecture and acceptance gates. An independently approved administrative bootstrap must precede host-user, permission, SSH, credential or executable changes. ENGINE-PACKAGING-001 explicitly excludes such host modifications.

## 2. Initial identity model

| Identity | Purpose | Access intent | Status |
| --- | --- | --- | --- |
| Existing Matt administrator | Administration, recovery and bounded root-run bootstrap | Matt remains accountable. A directly supervised root-local Claude Code session served only as command executor for the completed `FORGEV2-ACCESS-BOOTSTRAP-001` run under the Issue #3 one-run exception; this does not authorize further use or engineering execution. | Existing; bootstrap use completed; no continuing executor authority |
| `forgev2-pl` | WO coordination and PL-only Git operations | Non-root, no interactive SSH, no sudo, private home; the administrative bootstrap created no GitHub credential | **CREATED; scoped identity and filesystem controls independently verified** |
| `forgev2-agent` | Specialist source edits and mechanical tests | Non-root, no interactive SSH, no sudo, separate private home; no PL credential or Git metadata write access | **CREATED; scoped identity and filesystem controls independently verified** |
| Named external engineer | Personally attributable human access when specifically appointed | Individual public key/account; no sudo or inherited project-wide access; prefer Orchestrator-facing access over host SSH where viable | **NOT REQUESTED/CREATED** |
| Independent reviewer | Auditor, Tester or DevSecOps with a separate assessment | Distinct reviewer identity/session, read-only source snapshot and no PL credential; separate permanent Unix account only if needed for on-host verification | **Consolidated bootstrap assessment completed under one-run exception; separate future delivery reviewers still require appointment** |
| Future Orchestrator | Receives approved WOs and starts appropriately isolated PL sessions | No root or unrestricted Git authority; autonomous cross-UID launch requires a separately approved mechanism | **NOT IMPLEMENTED** |

The two Debian system accounts use dynamically allocated UIDs/GIDs, private primary groups, `/usr/sbin/nologin`, locked passwords, and private `0700` homes; the reviewed bootstrap evidence verified these properties and absence of sudo grants. Do not hardcode numeric IDs, share the root home, reuse root credentials, or grant `sudo`. No human or service identity is authorised merely by appearing in this design.

## 3. Execution and credential boundaries

- **Initial manual bootstrap:** Matt's root-controlled administrative session may start a **separate process** under each service identity using a reviewed command launcher. For `FORGEV2-ACCESS-BOOTSTRAP-001`, commands are issued only through the supervised executor arrangement in `FV2-D022`, after Matt's explicit approval. The service processes remain separate OS identities; this is a temporary, attributable coordination path, not autonomous PL-to-Engineer dispatch.
- **Supervised administrative command execution (`FV2-D022`):** For `FORGEV2-ACCESS-BOOTSTRAP-001` only, the existing root-local Claude Code installation may be proposed as a command executor under Matt's direct supervision. Matt remains the accountable and approving administrator and explicitly approves each privileged command or tightly bounded stage. Claude cannot select, expand, substitute, retry, or approve privileged changes. Unattended execution, permission bypass, persistent blanket command approval, and alternate execution routes are prohibited. Before use, verify and record the exact executable, version, ownership, configuration, and relevant session-state side effects in restricted evidence. Existing Claude provenance/security uncertainty remains a gate; this decision is not blanket runtime or supply-chain approval. Auditor, Tester, and DevSecOps remain independent of the executing session. No ForgeV2 plugin, engine agent, or application may be run under this decision.
- **Accepted one-run exception:** For the completed bootstrap only, Matt's Issue #3 authorization replaced per-command/stage approvals, intermediate fixture acceptance and pre-execution reviewer appointments, and accepted Mr Smiley's consolidated post-execution assessment. This exception does not change the general `FV2-D022` rule, authorize further Claude use, or create ongoing reviewer appointments.
- **Do not assume a Claude in-process subagent changes UID.** A subagent running under a credentialed PL process is *not* accepted as a separate operating-system security boundary. Testing plugin agent discovery does not authorise privileged production dispatch.
- **PL-only Git:** Git metadata and eventual repository-write credentials remain inaccessible to Engineer. The PL performs authorised stage/commit/push operations; Engineer edits scoped source, records results and returns to PL. A repository write key is **not** intrinsically limited to a single branch; check remote repository protections before relying on it.
- **No inherited secrets:** launch the Engineer with a clean, explicitly constructed environment without PL/home, SSH agent socket, Git askpass, token variables or private paths. Verify the actual UID, supplementary groups, environment boundary and credential-denial tests.
- **Service shell caveat:** `runuser --user NAME --login` is *not* an appropriate launcher for an account whose shell is `/usr/sbin/nologin`. Use the Debian `runuser -u NAME -- COMMAND` command form (or an independently assessed equivalent) with explicit environment control and a concrete approved executable. Validate the exact launch command before service use.
- **Claude runtime:** The existing root-local Claude installation is not available to these identities and is not an approved non-root distribution. Review its provenance, licence and dependencies, then approve a root-owned non-writable executable path accessible to service identities. Keep their configuration separate. Claude allow/deny rules are a secondary layer, not an OS permission boundary.
- **Future automation:** A privileged or otherwise trusted cross-UID dispatch broker is deliberately deferred. Until authorised and independently tested, Matt must manually start separate role processes. No broad sudoers or setuid exception is implied.

## 4. Filesystem and project boundary

| Boundary | Policy | Proof required |
| --- | --- | --- |
| Canonical engine source checkout | Remains an identified, clean `main`; inherited tracked files were not recursively reassigned | The completed bootstrap independently verified unchanged HEAD, tracked contents and registered-worktree state |
| Engine-source Git administrative metadata | The approved `.git` metadata subtree is PL-owned and Engineer-non-writable | Independently verified through scoped ownership inspection and negative Engineer write checks. Root's ordinary `git -C` discovery reports dubious ownership; use an explicit Git directory or narrow one-shot safe-directory setting for authorised read-only inspection. |
| Engine-development worktrees | PL creates explicit sibling worktrees from the exact approved WO commit | Verify repository, branch, lineage and approved WO for each future worktree |
| Assigned WO worktree | Engineer may write source only in its assigned worktree | Disposable fixture verified source-write access and denial of Git metadata, pointer, parent and sibling writes; no production worktree was created by the bootstrap |
| Installed ForgeV2 engine | Not writable by delivery identities; installed location is not part of this bootstrap | Protected paths were absent and service identities had no access; installed-engine protections remain to be verified when an engine is installed |
| PACMAN and other projects | Independent identities and grants; no access inherited from ForgeV2 engine development | Negative cross-project access checks when those projects exist |
| Service homes/credentials | Private owner-only homes; PL secrets not visible to Engineer/reviewers | Ownership/mode checks and non-disclosing access-denial tests |

**Implemented and independently verified boundary:** Ownership changed only within the canonical checkout's `.git` directory; the sibling worktree parent is PL-owned with mode `0711`; tracked source ownership and contents were preserved. The disposable fixture and post-change checks verified PL Git authority and Engineer denial of Git administrative writes and protected-path writes. This does not establish a ready engineering runtime, installed-engine isolation, credential availability, or permissions for future worktrees.

**Future worktree permission rule:** Before Engineer access, the PL must create the worktree using the approved WO-specific group. Shared WO source must have that group and the required group read/write modes. Git administrative metadata must remain PL-controlled and never be Engineer-writable. Git operations and source-editing operations can create different owners and modes; the PL must normalise and inspect final ownership and modes, then test Engineer source access and Git-metadata denial before granting access. Do not assume one `umask` satisfies both requirements. Keep the `.git` pointer protected from Engineer replacement, and do not apply broad recursive ownership changes.

## 5. Human onboarding and revocation

For each external human, Matt must approve the individual and project scope before an account is created. Use a unique Unix username, independent public key, no sudo, and only explicitly granted project resources. If host SSH is required, apply a separately reviewed account-class policy and preserve a second working Matt administrative login before any reload. Matt alone controls provider-side ingress rules. Orchestrator-only access is preferred where practical.

The **restricted** access register records person, Unix identity, role, project/WO, request and approval references, assigned resources, public-key fingerprint, grant time, review time and revocation status. Do not put those particulars or secrets in this public file. Revocation includes disabling the individual's access, ending existing sessions, removing project grants and separately revoking any independent GitHub access; preserve delivery evidence.

## 6. Bounded bootstrap and acceptance

The completed initial administrative access bootstrap captured the pre-change state, created only the two approved non-login identities and private homes, tested the Git ownership/group scheme in a disposable fixture, and applied only the scoped `.git` ownership and worktree-parent changes. It verified separate PL and Engineer UIDs, the declared clean environment and PL credential separation. Fixture and live checks covered PL Git access, Engineer source writes in the fixture, Engineer denial of Git metadata and pointer writes, and denial of protected paths. Tracked source, Git lineage, SSH policy, provider firewall, installed-engine and PACMAN boundaries remained unchanged. Account/group and filesystem evidence, independent results and rollback information are retained in the restricted evidence store; public records contain only sanitized outcomes and candidate references.

**Remaining engineering prerequisites:** GitHub credential creation/approval, CLI installation or approval, Orchestrator process automation, external human onboarding, SSH policy changes, engine installation, application implementation and ENGINE-PACKAGING-001 specialist dispatch remain outside the completed bootstrap and require their own authority and acceptance. The infrastructure-provider-managed network perimeter remains the approved approach; no host-firewall requirement is introduced.

## 7. Decision and evidence ledger

| Date (Europe/London) | Record | State | Evidence / next decision |
| --- | --- | --- | --- |
| 2026-10-25 | Matt selected individually identifiable external engineers and least-privilege access, withdrawing the earlier preference for root-run engineering | **APPROVED DIRECTION** | Conversation decision; to be recorded in project governance. No host change inferred. |
| 2026-10-25 | Two non-login identities, `forgev2-pl` and `forgev2-agent`, proposed after read-only VPS assessment | **AT ENTRY: DESIGN ACCEPTED FOR REVIEW; NOT IMPLEMENTED** | Historical state before the authorized bootstrap; see the later execution outcome below. |
| 2026-10-25 | Root-managed manual process launch proposed for first WO; automated cross-UID launch deferred | **AT ENTRY: PROPOSED BOOTSTRAP EXCEPTION** | Historical state before execution; the one-run exception and completed use are recorded below. |
| 2026-10-25 | Scoped Git ownership and WO-group scheme proposed | **AT ENTRY: UNPROVEN** | Historical state before fixture and production verification; see the later execution outcome below. |
| 2026-10-25 | Non-root Claude executable, PL GitHub credential, reviewer appointments and external-code review | **BLOCKED** | Separate provenance, security, role and credential approvals required. |
| 2026-10-25 | `FV2-D022` — supervised administrative execution for `FORGEV2-ACCESS-BOOTSTRAP-001` only | **ORIGINAL ARRANGEMENT; SUPERSEDED FOR THIS RUN BY ONE-RUN EXCEPTION** | Matt remained accountable; Claude had no change-selection or approval authority. The Issue #3 exception was limited to this run and grants no continuing executor authority. |
| 2026-10-25 | `FORGEV2-ACCESS-BOOTSTRAP-001` execution and assurance outcome | **TECHNICAL CONTROLS ACCEPTED PASS; DOCUMENTATION CLOSEOUT IN REVIEW** | Matt's one-run exception on [Issue #3](https://github.com/maff0000/forgev2/issues/3#issuecomment-6397756576) replaced per-command approvals, intermediate fixture acceptance and pre-execution reviewer appointments for this run only. Mr Smiley's consolidated independent Auditor/Tester/Security assessment passed against Administrative Candidate ID `0b9201cfc8be419b8b655fb3bf4c2023825ce3f891a33ba3d636f2f985c9c944`; CGPT accepted the technical controls and correction disposition. The two identities and scoped filesystem boundary are implemented and verified. No engineering dispatch or runtime approval follows. Known limitations and future worktree permission requirements are stated above. |

## 8. Updating this record

After each controlled change or test, append a dated ledger entry with exact decision authority, scope, candidate/host evidence reference (restricted where necessary), observed PASS/FAIL, and unresolved blocker. Promote **PROPOSED → VERIFIED → ACCEPTED** only after the corresponding evidence and CGPT/Matt acceptance. Never rewrite reported history to make an untested control appear implemented. Changes to this public document require an approved review branch and must not silently amend FOUNDRY or ENGINE-PACKAGING-001.

References: [Debian adduser](https://manpages.debian.org/bookworm/adduser/adduser.8.en.html), [Debian runuser](https://manpages.debian.org/bookworm/util-linux/runuser.1.en.html), [GitHub deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys), [Claude Code permissions](https://code.claude.com/docs/en/permissions), [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing).
