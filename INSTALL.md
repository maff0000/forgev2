# ForgeV2 — installation checklist for Claude

ForgeV2 is **AI-first**. This is a task list for Claude, **not** a self-installer or a new governance workflow. Matt supplies the target and authorises material changes; Claude carries out routine installation, fixes ordinary problems, tests, and reports the outcome.

**Release status:** The ForgeV2 plugin is in `plugin/` (manifest `plugin/.claude-plugin/plugin.json`, version in that file). It is pending independent review; install it from the reviewed commit only. Usage, Work Order format and the Orchestrator command are in [plugin/README.md](plugin/README.md).

## Commands Claude uses

```sh
claude plugin validate <checkout>/plugin            # must pass
claude plugin marketplace add <checkout>            # or: maff0000/forgev2 (GitHub)
claude plugin install forgev2@forgev2               # or load per run with --plugin-dir <checkout>/plugin
claude plugin details forgev2                       # expect skill deliver and the PreToolUse hook
python3 -m unittest discover -s <checkout>/tests    # plugin self-tests
sudo <checkout>/tests/host/os-boundary.sh <checkout>/plugin   # execution host only
```

Prerequisites on the execution host: the one-time host set-up below, `git`, `python3`, gitleaks installed root-owned at `/usr/local/bin/gitleaks` from the official release after checking the archive against the release-published SHA-256 (v8.30.1 linux x64: archive `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`, binary `88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509`; the plugin refuses any other build unless its SHA-256 is listed in `FORGE_GITLEAKS_SHA256`), and push access for `forgev2-pl` to the target repository.

## One-time host set-up (root, with Matt's approval)

ForgeV2 runs the PL as `forgev2-pl` and every specialist as `forgev2-agent` (both existing system accounts with 0700 homes). Claude carries out steps 1-4 and records the output; step 5 is Matt's.

```sh
# 1. Shared group for the worktrees
groupadd --system forgev2-work
usermod -aG forgev2-work forgev2-pl; usermod -aG forgev2-work forgev2-agent
# 2. Claude Code for both accounts: a root-owned copy of the verified binary already installed for root
install -o root -g root -m 0755 ~/.local/share/claude/versions/<version> /usr/local/bin/claude
# 3. The launcher and role definitions, from the reviewed checkout
install -d -o root -g root -m 0755 /usr/local/libexec/forgev2 /usr/local/libexec/forgev2/roles
install -o root -g root -m 0755 <checkout>/plugin/libexec/agent-run /usr/local/libexec/forgev2/
install -o root -g root -m 0644 <checkout>/plugin/roles/*.md /usr/local/libexec/forgev2/roles/
# 4. The sudo rule: the PL may run only the launcher, only as the agent account
echo 'forgev2-pl ALL=(forgev2-agent) NOPASSWD: /usr/local/libexec/forgev2/agent-run' > /tmp/forgev2.sudoers
visudo -cf /tmp/forgev2.sudoers && install -o root -g root -m 0440 /tmp/forgev2.sudoers /etc/sudoers.d/forgev2
visudo -c && sudo -l -U forgev2-pl
```

5. **Matt** logs each account into his existing subscription (one browser sign-in each; no login is copied between accounts):

```sh
sudo -u forgev2-pl -H sh -c 'cd && DISABLE_AUTOUPDATER=1 /usr/local/bin/claude auth login'
sudo -u forgev2-agent -H sh -c 'cd && CLAUDE_CONFIG_DIR=$HOME/.claude DISABLE_AUTOUPDATER=1 /usr/local/bin/claude auth login'
```

The agent account's login must be in `/var/lib/forgev2/agent/.claude` (hence `CLAUDE_CONFIG_DIR`), because the launcher gives every specialist run a fresh, empty HOME and points Claude at that directory. After any plugin update, re-run step 3; `forge-dispatch` refuses to start specialists while the installed launcher or roles differ from the plugin's copies. Verify with `sudo <checkout>/tests/host/os-boundary.sh <checkout>/plugin`.

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
