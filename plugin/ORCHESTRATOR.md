# ForgeV2 Orchestrator handoff contract

How an existing Orchestrator (any Claude session or script that assigns work)
hands one Work Order to ForgeV2 and acts on the result. ForgeV2 adds no
Orchestrator of its own, and no service, queue or daemon.

**Status:** the plugin entry point and this contract are tested with headless
runs (`docs/evidence/FORGEV2-PLUGIN-BUILD-001.md`). A handoff from Matt's
Orchestrator has **not** been run yet.

## Identity and subscription

- The PL runs as an ordinary `claude` process using the Claude login that the
  account running it already has. ForgeV2 uses no API keys, extra subscriptions
  or separate Claude accounts. Specialists are subagents inside that PL process.
- On execution hosts, start the PL as the non-root `forgev2-pl` account, which
  holds the repository's Git push access. Do not start it as root, and do not
  pass credentials in the Work Order, the prompt or the environment.
- The guard hook is a policy layer inside that one process. It does not give
  OS isolation between PL and Engineer. See "Security model" in `README.md`.

## 1. Pass a Work Order

Write one Work Order file in the format in `README.md` ("Work Order format").
The required fields are `WO`, `REPO` (exact `owner/name`) and `ROOT` (the canonical
checkout), plus the change and the acceptance criteria. Give `KNOWN_COMMIT` when
you know it. Use one file per WO, and keep it outside the target repository.

## 2. Start the PL

Start one fresh PL process per Work Order, and never resume or reuse a session:

```sh
cd "$ROOT" && claude -p \
  --add-dir "$(dirname "$ROOT")/worktrees" \
  --allowedTools "Bash Read Write Edit Glob Grep Agent" \
  --output-format json \
  "/forgev2:deliver /path/to/WO-123.md" < /dev/null
```

Add `--plugin-dir /path/to/forgev2/plugin` if the plugin is not installed. The PL
does not ask questions mid-run. It returns only when it has reached a final status.

## 3. Validate the response

With `--output-format json`, stdout is **one JSON object**, not a status line.
Parse it and validate it before acting:

1. The process exited 0 and stdout parses as JSON.
2. `type == "result"`, `subtype == "success"` and `is_error == false`.
3. The first line of the `result` string matches exactly
   `# <WO> - (DELIVERED|ESCALATED|BLOCKED)`, and `<WO>` is the Work Order you sent.
4. If the WO reached the worktree stage,
   `<worktrees>/<WO>/.forge/<WO>/ledger.json` has `"outcome"` equal to that
   status. The ledger is authoritative. A `BLOCKED` result at the identity gate
   or at intake has no ledger.

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
