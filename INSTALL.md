# ForgeV2 — installation checklist for Claude

ForgeV2 is **AI-first**. This is a task list for Claude, **not** a self-installer or a new governance workflow. Matt supplies the target and authorises material changes; Claude carries out routine installation, fixes ordinary problems, tests, and reports the outcome.

**Release status:** The ForgeV2 plugin is in `plugin/` (manifest `plugin/.claude-plugin/plugin.json`, version in that file). It is pending independent review; install it from the reviewed commit only. Usage, Work Order format and the Orchestrator command are in [plugin/README.md](plugin/README.md).

## Commands Claude uses

```sh
claude plugin validate <checkout>/plugin            # must pass
claude plugin marketplace add <checkout>            # or: maff0000/forgev2 (GitHub)
claude plugin install forgev2@forgev2               # or load per run with --plugin-dir <checkout>/plugin
claude plugin details forgev2                       # expect skill deliver; agents engineer, auditor, tester, devsecops
python3 -m unittest discover -s <checkout>/tests    # plugin self-tests
sudo <checkout>/tests/host/os-boundary.sh <checkout>/plugin   # execution host only
```

Prerequisites on the execution host: Claude Code with Matt's existing login for the account that runs the PL, `git`, `python3`, `gitleaks` on `PATH`, and push access for that account to the target repository.

## Matt's one-line request

> Claude, review `https://github.com/maff0000/forgev2`, follow its `INSTALL.md`, install the approved ForgeV2 version on the named target, connect it to my existing Orchestrator, test it, and report PASS or the specific blocker. Reuse my working Claude subscription; do not create another login, subscription, or API key.

## Claude's to-do list

1. **Discover the environment:** Identify the approved host, current Orchestrator/Claude setup, and whether this machine is the controller or an execution VPS. Reuse the existing control plane; do not duplicate the Orchestrator.
2. **Inspect source:** Verify repository identity (`maff0000/forgev2`), selected version, source integrity, and target paths. Preserve dirty work and the working ForgeV1 installation. Read only the relevant repo instructions.
3. **Confirm product readiness:** Find and inspect the versioned `plugin/` package, its manifest, roles, and skills. If missing, report **NOT YET INSTALLABLE** and stop. Do not improvise a plugin.
4. **Check prerequisites:** Verify the compatible Claude CLI, needed tools, Git access, and any existing configured service identities. Prefer what already works. The Orchestrator initiates the PL using Matt's existing Claude subscription; do not require separate role subscriptions. Keep PL Git credentials away from Engineer.
5. **Install and configure:** Follow [Claude's official plugin guidance](https://code.claude.com/docs/en/plugins), validate the actual package, and make it available to the existing Orchestrator/PL. Reuse established non-root worktree boundaries on execution hosts; do not change unrelated services or the provider-managed firewall.
6. **Test:** Confirm the installed plugin/version, role discovery, Orchestrator → PL initiation, correct repository rejection cases, and PL/Engineer filesystem separation with disposable fixtures. Do not deploy an application as an installation test.
7. **Finish:** Report version and exact SHA, changed paths, tests, PASS/FAIL, and any genuine blockers. If already installed correctly, say **ALREADY INSTALLED — VERIFIED**. Never claim success from documentation alone.

## Stop only for material reasons

Ask Matt for **one consolidated approval** when new privileged host changes, credentials, or materially destructive operations are required. Stop on unknown host identity, missing software, failed isolation tests, or an unsatisfied security-critical prerequisite. Otherwise proceed autonomously with recoverable corrections. Do not change ForgeV1, protected engine/application roots, or engineer on unrelated projects without explicit authority.
