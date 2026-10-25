# ForgeV2 — Access Control and Security Decision Record

**State:** Living design record — implementation and runtime approval **PENDING**
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
| Existing Matt administrator | Administration, recovery and bounded root-run bootstrap | Existing key-only root access retained; not an engineering execution account | Existing; current access independently reported |
| `forgev2-pl` | WO coordination and PL-only Git operations | Non-root, no interactive SSH, no sudo, private home and PL-only repository credential after separate approval | **APPROVED DESIGN; NOT CREATED** |
| `forgev2-agent` | Specialist source edits and mechanical tests | Non-root, no interactive SSH, no sudo, write only to assigned WO worktree; **no** PL credentials or Git metadata writes | **APPROVED DESIGN; NOT CREATED** |
| Named external engineer | Personally attributable human access when specifically appointed | Individual public key/account; no sudo or inherited project-wide access; prefer Orchestrator-facing access over host SSH where viable | **NOT REQUESTED/CREATED** |
| Independent reviewer | Auditor, Tester or DevSecOps with a separate assessment | Distinct reviewer identity/session, read-only source snapshot and no PL credential; separate permanent Unix account only if needed for on-host verification | **APPOINTMENTS PENDING** |
| Future Orchestrator | Receives approved WOs and starts appropriately isolated PL sessions | No root or unrestricted Git authority; autonomous cross-UID launch requires a separately approved mechanism | **NOT IMPLEMENTED** |

Two initially proposed Debian system accounts use dynamically allocated UIDs/GIDs, private primary groups, `/usr/sbin/nologin`, and private `0700` homes. Do not hardcode numeric IDs, share the root home, reuse root credentials, or grant `sudo`. No human or service identity is authorised merely by appearing in this design.

## 3. Execution and credential boundaries

- **Initial manual bootstrap:** Matt's root-controlled administrative session may start a **separate process** under each service identity using a reviewed command launcher. This is a temporary, attributable coordination path, not autonomous PL-to-Engineer dispatch.
- **Do not assume a Claude in-process subagent changes UID.** A subagent running under a credentialed PL process is *not* accepted as a separate operating-system security boundary. Testing plugin agent discovery does not authorise privileged production dispatch.
- **PL-only Git:** Git metadata and eventual repository-write credentials remain inaccessible to Engineer. The PL performs authorised stage/commit/push operations; Engineer edits scoped source, records results and returns to PL. A repository write key is **not** intrinsically limited to a single branch; check remote repository protections before relying on it.
- **No inherited secrets:** launch the Engineer with a clean, explicitly constructed environment without PL/home, SSH agent socket, Git askpass, token variables or private paths. Verify the actual UID, supplementary groups, environment boundary and credential-denial tests.
- **Service shell caveat:** `runuser --user NAME --login` is *not* an appropriate launcher for an account whose shell is `/usr/sbin/nologin`. Use the Debian `runuser -u NAME -- COMMAND` command form (or an independently assessed equivalent) with explicit environment control and a concrete approved executable. Validate the exact launch command before service use.
- **Claude runtime:** The existing root-local Claude installation is not available to these identities and is not an approved non-root distribution. Review its provenance, licence and dependencies, then approve a root-owned non-writable executable path accessible to service identities. Keep their configuration separate. Claude allow/deny rules are a secondary layer, not an OS permission boundary.
- **Future automation:** A privileged or otherwise trusted cross-UID dispatch broker is deliberately deferred. Until authorised and independently tested, Matt must manually start separate role processes. No broad sudoers or setuid exception is implied.

## 4. Filesystem and project boundary

| Boundary | Policy | Proof required |
| --- | --- | --- |
| Canonical engine source checkout | Remains an identified, clean `main`; inherited tracked files are not recursively reassigned | Before/after ownership, content and Git-status comparison |
| Engine-source Git administrative metadata | Proposed PL-only write ownership; exact-target review required before changing ownership | Directory is genuine Git metadata, no unexpected linked path; PL Git-positive and Engineer Git-negative tests |
| Engine-development worktrees | PL creates explicit sibling worktree from the exact approved WO commit | Repository, branch, lineage and approved WO verified |
| Assigned WO worktree | Engineer may write source only in its assigned worktree | Real write succeeds for Engineer; `.git` pointer, Git administrative metadata, parent and sibling remain protected |
| Installed ForgeV2 engine | Not writable by delivery identities; installed location is not part of this bootstrap | Negative write test or equivalent demonstrated DAC boundary |
| PACMAN and other projects | Independent identities and grants; no access inherited from ForgeV2 engine development | Negative cross-project access checks when those projects exist |
| Service homes/credentials | Private owner-only homes; PL secrets not visible to Engineer/reviewers | Ownership/mode checks and non-disclosing access-denial tests |

**Unproven design:** The proposed ownership change restricted to the canonical checkout's `.git` directory, PL ownership of the sibling worktree parent, and per-WO Unix groups may be sufficient. The details of `.git` pointer protection, Git metadata access and group-write modes must be proven on a **disposable fixture first**. A sticky/setgid directory alone is not accepted as evidence. Do not apply a broad recursive ownership change to source, and do not treat an untested layout as secure.

## 5. Human onboarding and revocation

For each external human, Matt must approve the individual and project scope before an account is created. Use a unique Unix username, independent public key, no sudo, and only explicitly granted project resources. If host SSH is required, apply a separately reviewed account-class policy and preserve a second working Matt administrative login before any reload. Matt alone controls provider-side ingress rules. Orchestrator-only access is preferred where practical.

The **restricted** access register records person, Unix identity, role, project/WO, request and approval references, assigned resources, public-key fingerprint, grant time, review time and revocation status. Do not put those particulars or secrets in this public file. Revocation includes disabling the individual's access, ending existing sessions, removing project grants and separately revoking any independent GitHub access; preserve delivery evidence.

## 6. Bounded bootstrap and acceptance

The initial administrative access bootstrap should:

1. Capture exact current identity, permissions, links, Git and SSH state; retain recoverable backups for every scoped change.
2. Create **only** the two approved non-login system identities and private homes; verify no sudo and no human SSH access.
3. Demonstrate the Git ownership/group scheme on a disposable worktree before modifying production source metadata. Stop if PL Git operations and Engineer Git denial cannot both be achieved.
4. Apply only separately approved, explicit source-metadata/worktree-parent ownership and permissions. Keep source content, `main`, existing SSH, host firewall, installed-engine and PACMAN boundaries unchanged.
5. Verify separate PL and Engineer UID execution with a clean environment; no session is allowed to inherit PL credentials.
6. Test positives and negatives: PL Git metadata access; Engineer assigned-file edits; Engineer denial for Git refs, `.git` pointer replacement, PL secrets/home, other worktrees, canonical checkout, protected engine and other projects; no sudo; reviewer read-only behaviour when reviewer execution is authorised.
7. Report every changed path/account/group, exact commands, independent results, remaining blockers and reversible rollback procedure in **restricted** operational evidence. Record a public-safe status and evidence reference here.

**Not in this bootstrap:** GitHub credential creation, CLI installation or approval, Orchestrator process automation, external human onboarding, host firewall, SSH policy changes, engine installation, application implementation or ENGINE-PACKAGING-001 specialist dispatch. These require their own authority and acceptance.

## 7. Decision and evidence ledger

| Date (Europe/London) | Record | State | Evidence / next decision |
| --- | --- | --- | --- |
| 2026-10-25 | Matt selected individually identifiable external engineers and least-privilege access, withdrawing the earlier preference for root-run engineering | **APPROVED DIRECTION** | Conversation decision; to be recorded in project governance. No host change inferred. |
| 2026-10-25 | Two non-login identities, `forgev2-pl` and `forgev2-agent`, proposed after read-only VPS assessment | **DESIGN ACCEPTED FOR REVIEW; NOT IMPLEMENTED** | `FORGEV2-ACCESS-001`; no independent runtime test. |
| 2026-10-25 | Root-managed manual process launch proposed for first WO; automated cross-UID launch deferred | **PROPOSED BOOTSTRAP EXCEPTION** | Validate command syntax, environment isolation, identity and log attribution; approval required before dispatch. |
| 2026-10-25 | Scoped Git ownership and WO-group scheme proposed | **UNPROVEN** | Disposable positive/negative fixture tests before owner/group mutation. |
| 2026-10-25 | Non-root Claude executable, PL GitHub credential, reviewer appointments and external-code review | **BLOCKED** | Separate provenance, security, role and credential approvals required. |

## 8. Updating this record

After each controlled change or test, append a dated ledger entry with exact decision authority, scope, candidate/host evidence reference (restricted where necessary), observed PASS/FAIL, and unresolved blocker. Promote **PROPOSED → VERIFIED → ACCEPTED** only after the corresponding evidence and CGPT/Matt acceptance. Never rewrite reported history to make an untested control appear implemented. Changes to this public document require an approved review branch and must not silently amend FOUNDRY or ENGINE-PACKAGING-001.

References: [Debian adduser](https://manpages.debian.org/bookworm/adduser/adduser.8.en.html), [Debian runuser](https://manpages.debian.org/bookworm/util-linux/runuser.1.en.html), [GitHub deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys), [Claude Code permissions](https://code.claude.com/docs/en/permissions), [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing).
