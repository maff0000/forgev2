# ForgeV2 Orchestrator handoff contract

How an existing Orchestrator (any Claude session or script that assigns work)
hands one Work Order to ForgeV2 and acts on the result. ForgeV2 adds no
Orchestrator of its own, and no service, queue or daemon.

**Status:** the plugin entry point and this contract are tested with headless
runs (`docs/evidence/FORGEV2-PLUGIN-BUILD-001.md`). A handoff from Matt's
Orchestrator has **not** been run yet.

## Identity and subscription

- ForgeV2 uses one Claude login: the `forgev2-pl` account's login to Matt's
  existing subscription. The PL runs under it, and so does every specialist, as
  a separate sandboxed `claude` process. ForgeV2 uses no API keys, extra
  subscriptions or separate Claude accounts, and the login is never copied or
  passed to a specialist. It persists between Work Orders; no login per run.
- `forgev2-pl` holds Git push access for the target repository and nothing
  more. The PL tools refuse to run as root unless `FORGE_ALLOW_ROOT=1`, which is
  for development hosts only. Never pass credentials in the Work Order, the
  prompt or the environment.
- The host needs the one-time set-up in `INSTALL.md`: bubblewrap and socat,
  `/usr/local/bin/claude`, an approved gitleaks, and the login. The plugin is
  installed in `forgev2-pl`'s user scope.
- Keep projects outside the PL's home and state directories (specialists cannot
  read those). `ROOT` and its `.git` are owned by `forgev2-pl`; `forge-start`
  creates `$(dirname "$ROOT")/worktrees`.

## 1. Pass a Work Order

Write one Work Order file in the format in `README.md` ("Work Order format").
The required fields are `WO`, `REPO` (exact `owner/name`) and `ROOT` (the canonical
checkout), plus the change and the acceptance criteria. Give `KNOWN_COMMIT` when
you know it. Use one file per WO, and keep it outside the target repository.

## 2. Start the PL

Start one fresh PL process per Work Order as `forgev2-pl`, and never resume or
reuse a session:

```sh
sudo -u forgev2-pl -H sh -c 'cd && exec env DISABLE_AUTOUPDATER=1 \
  BASH_DEFAULT_TIMEOUT_MS=2400000 BASH_MAX_TIMEOUT_MS=2400000 \
  /usr/local/bin/claude -p \
  --add-dir "$1" --add-dir "$(dirname "$1")/worktrees" \
  --allowedTools "Bash Read Write Edit Glob Grep" \
  --output-format json \
  "/forgev2:deliver $2" < /dev/null' sh "$ROOT" /path/to/WO-123.md
```

Start it in the PL's home directory, never inside `ROOT` or a worktree: Claude
loads project settings and CLAUDE.md from its starting directory, and worktree
contents are written by the agent account. The Bash timeouts let one
`forge-dispatch` call wait for a specialist (up to 30 minutes each). The Work
Order file must be readable by `forgev2-pl`. The Orchestrator itself may run as
any account allowed to start a process as `forgev2-pl` (here, root). The PL does not ask questions
mid-run. It returns only when it has reached a final status.

## 3. Validate the response

With `--output-format json`, stdout is **one JSON object**, not a status line.
Parse it and validate it before acting:

1. The process exited 0 and stdout parses as JSON.
2. `type == "result"`, `subtype == "success"` and `is_error == false`.
3. The first line of the `result` string matches exactly
   `# <WO> - (DELIVERED|ESCALATED|BLOCKED)`, and `<WO>` is the Work Order you sent.
4. If the WO reached the worktree stage, the ledger copy committed with the
   delivery record, `<worktrees>/<WO>/.forge/<WO>/ledger.json`, has `"outcome"`
   equal to that status. (The authoritative ledger is in the PL account's private
   state directory.) A `BLOCKED` result at the identity gate or at intake has no
   ledger.

If any check fails, treat the run as **BLOCKED (malformed PL result)**. Keep
stdout and stderr, and do not retry automatically. `session_id` and
`total_cost_usd` are worth logging. `total_cost_usd` is Claude Code's modelled
API-equivalent figure, not necessarily a separate charge on a subscription.

## 4. Act on the status

| Status | Meaning | Orchestrator action |
| --- | --- | --- |
| `DELIVERED` | All three reviewers passed the final candidate on `forge/<WO>` | Report the branch and PR to Matt for merge. Never merge it yourself |
| `ESCALATED` | The loop stopped: no progress, INCONCLUSIVE twice, or 4 executions | Read the open findings, then either issue a new, narrower WO or ask Matt |
| `BLOCKED` | A precondition failed: identity, WO fields, scope, or a permission | Fix the named precondition if it is within your authority, otherwise ask Matt |

Do not edit ForgeV2's ledger, worktrees or `forge/*` branches yourself.

## Role-file snippet

Paste this into the Orchestrator's role or skill file:

> **Software changes go to ForgeV2.** Write a Work Order file in the format in
> ForgeV2's `plugin/README.md`, then start a fresh PL with the command in
> `plugin/ORCHESTRATOR.md` (one process per WO; never reuse a session). Parse
> stdout as JSON and validate it as in `ORCHESTRATOR.md` section 3; anything
> that fails validation is BLOCKED. Then act on the status:
> `DELIVERED` - report the branch/PR to Matt for merge.
> `ESCALATED` - read the open findings; either issue a new, narrower WO or ask Matt.
> `BLOCKED` - fix the named precondition if it is within your authority, otherwise ask Matt.
> Do not edit ForgeV2's ledger or branches yourself.
