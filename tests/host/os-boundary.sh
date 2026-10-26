#!/usr/bin/env bash
# ForgeV2 OS boundary check on an execution host (run as root; read-mostly).
# Uses the real forgev2-pl / forgev2-agent accounts, the forgev2-work group, the
# installed launcher and its sudo rule against a disposable fixture made by
# forge-start running as forgev2-pl. Confirms the agent account can change only
# the worktree and scratch directory, cannot alter PL-owned Git metadata or
# records, cannot read PL state or credentials, and that the sudo rule allows
# nothing but the launcher, as the agent account.
# Usage: sudo tests/host/os-boundary.sh [PLUGIN_DIR]
set -u
[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 2; }
for u in forgev2-pl forgev2-agent; do id "$u" >/dev/null 2>&1 || { echo "missing identity $u" >&2; exit 2; }; done
getent group forgev2-work >/dev/null || { echo "missing group forgev2-work" >&2; exit 2; }
SRC_PLUGIN=$(realpath "${1:-$(dirname "$0")/../../plugin}")
L=/usr/local/libexec/forgev2/agent-run
PLH=/var/lib/forgev2/pl; AGH=/var/lib/forgev2/agent
FX=$(mktemp -d /tmp/forgev2-ostest-XXXXXX); chmod 0755 "$FX"
STATE=$(mktemp -d "$PLH/.ostest-state-XXXXXX"); chown forgev2-pl:forgev2-pl "$STATE"; chmod 0700 "$STATE"
trap 'rm -rf --one-file-system -- "$FX" "$STATE"; [ -n "${SPID:-}" ] && kill "$SPID" 2>/dev/null' EXIT
pass=0; fail=0
run_as() { local u=$1; shift; (cd / && runuser -u "forgev2-$u" -- /usr/bin/env -i HOME="/var/lib/forgev2/$u" \
       USER="forgev2-$u" LOGNAME="forgev2-$u" PATH=/usr/local/bin:/usr/bin:/bin FORGE_STATE_DIR="$STATE" \
       /bin/sh -c "$*"); }
as() { run_as "$@" >/dev/null 2>&1; }
check() { # check ok|deny DESC rc
  if { [ "$1" = ok ] && [ "$3" -eq 0 ]; } || { [ "$1" = deny ] && [ "$3" -ne 0 ]; }; then
    echo "PASS $2"; pass=$((pass+1)); else echo "FAIL $2 (rc=$3)"; fail=$((fail+1)); fi; }

# Fixture: a PL-owned project traversable by the shared group, set up by forge-start as forgev2-pl.
cp -a "$SRC_PLUGIN" "$FX/plugin"; chown -R root:root "$FX/plugin"; chmod -R go-w "$FX/plugin"
install -d -o forgev2-pl -g forgev2-work -m 2750 "$FX/proj"
install -d -o forgev2-pl -g forgev2-pl -m 0755 "$FX/proj/main"
G="git -c user.name=t -c user.email=t@invalid.example"
run_as pl "cd $FX/proj/main && git init -q -b main . && echo x > a.txt && $G add -A && $G commit -qm init && \
  git remote add origin https://github.com/fixture-owner/calc.git" >/dev/null 2>&1
out=$(run_as pl "cd $FX && $FX/plugin/bin/forge-start --wo T-1 --repo fixture-owner/calc --root $FX/proj/main" 2>&1)
check ok "forge-start runs as forgev2-pl and shares the worktree" $?
WT=$FX/proj/worktrees/T-1; SCR=$FX/proj/worktrees/.forge-scratch/T-1; COMMON=$FX/proj/main/.git
LEDGER=$(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["ledger"])' 2>/dev/null)
SAFE="GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=$WT"

echo "-- sudo rule and launcher"
test "$(stat -c '%U:%G %a' /etc/sudoers.d/forgev2)" = "root:root 440" && visudo -c >/dev/null; check ok "sudo rule root-owned 0440 and valid" $?
dry=$(run_as pl "sudo -n -u forgev2-agent $L --dry-run auditor $WT" 2>&1); check ok "PL starts the launcher as the agent account" $?
printf '%s' "$dry" | python3 -c '
import json, sys
d = json.load(sys.stdin); a, e = d["argv"], d["env"]
assert a[0] == "/usr/local/bin/claude" and "--safe-mode" in a and "--strict-mcp-config" in a
assert a[a.index("--setting-sources") + 1] == "" and "--dangerously-skip-permissions" not in a
assert e["HOME"].startswith("/tmp/forgev2-") and e["CLAUDE_CONFIG_DIR"] == "/var/lib/forgev2/agent/.claude"
assert not {"FORGE_STATE_DIR", "SSH_AUTH_SOCK", "GH_TOKEN", "GITHUB_TOKEN", "ANTHROPIC_API_KEY", "SUDO_COMMAND"} & set(e)
assert d["cwd"] == sys.argv[1]' "$WT" 2>/dev/null; check ok "launcher builds the fixed command and a clean environment" $?
as pl "sudo -n true"; check deny "PL cannot sudo to root" $?
as pl "sudo -n -u forgev2-agent /bin/true"; check deny "PL cannot run other commands as the agent" $?
as pl "sudo -n -u forgev2-agent /usr/local/bin/claude --version"; check deny "PL cannot run claude directly as the agent" $?
as pl "sudo -n $L --dry-run auditor $WT"; check deny "PL cannot run the launcher as root" $?
as agent "sudo -n true"; check deny "agent has no sudo" $?
as pl "$L --dry-run auditor $WT"; check deny "launcher refuses to run as the PL account" $?
for bad in "intruder $WT" "auditor $FX/proj/main" "auditor $FX/proj/worktrees/../worktrees/T-1" "auditor $PLH" "auditor /"; do
  as pl "sudo -n -u forgev2-agent $L --dry-run $bad"; check deny "launcher refuses: $bad" $?
done
as pl "echo hi | sudo -n -u forgev2-agent $L auditor $FX/proj/main"; check deny "launcher refuses a real run on a bad worktree" $?
for p in "$L" /usr/local/libexec/forgev2/roles/auditor.md /usr/local/bin/claude /etc/sudoers.d/forgev2; do
  as agent "test -w $p" ; check deny "agent cannot modify $p" $?
  as pl "test -w $p" ; check deny "PL cannot modify $p" $?
done

echo "-- agent filesystem access"
as agent "echo y >> $WT/a.txt && echo n > $WT/new.py && mkdir $WT/pkg && echo m > $WT/pkg/m.py"; check ok "agent changes and adds worktree files" $?
as agent "echo s > $SCR/probe.txt"; check ok "agent writes its scratch directory" $?
as agent "$SAFE git -C $WT log --oneline -1 && $SAFE git -C $WT diff --stat"; check ok "agent reads Git history in the worktree" $?
as agent "echo 'gitdir: /tmp/evil' > $WT/.git"; check deny "agent cannot rewrite the worktree .git pointer in place" $?
as agent "touch $COMMON/worktrees/T-1/HEAD"; check deny "agent cannot write the worktree Git directory" $?
as agent "$SAFE git -C $WT update-ref refs/heads/evil HEAD"; check deny "agent cannot write refs" $?
as agent "touch $COMMON/objects/evil"; check deny "agent cannot write objects" $?
as agent "touch $COMMON/hooks/pre-commit"; check deny "agent cannot install hooks" $?
as agent "$SAFE git -C $WT config core.hooksPath /tmp"; check deny "agent cannot change Git config" $?
as agent "cd $WT && $SAFE $G commit -qam evil"; check deny "agent cannot commit" $?
as agent "touch $WT/.forge/x && mkdir $WT/.forge/T-1"; check deny "agent cannot write the .forge record directory" $?
as agent "mkdir $FX/proj/worktrees/evil"; check deny "agent cannot create worktrees" $?
as agent "mkdir $FX/proj/worktrees/.forge-scratch/evil"; check deny "agent cannot create scratch directories" $?
as agent "touch $FX/proj/main/evil"; check deny "agent cannot write the canonical checkout" $?
as agent "touch $FX/plugin/evil"; check deny "agent cannot write the ForgeV2 plugin" $?
as agent "cat $LEDGER"; check deny "agent cannot read the ledger" $?
as agent "ls $STATE"; check deny "agent cannot list PL state" $?
as agent "ls $PLH"; check deny "agent cannot list the PL home (credentials)" $?
as pl "ls $AGH"; check deny "PL cannot list the agent home" $?
run_as pl "exec env FORGE_PROBE=pl-secret-marker sleep 300" >/dev/null 2>&1 & sleep 1
SPID=$(pgrep -u forgev2-pl -f "sleep 300" | head -1)
as agent "cat /proc/$SPID/environ | grep -q pl-secret-marker"; check deny "agent cannot read PL process environments" $?
kill "$SPID" 2>/dev/null; SPID=
as agent "mkdir /srv/forgev2"; check deny "agent cannot create engine install path" $?
as agent "touch /srv/src/forgev2/evil"; check deny "agent cannot write engine source tree" $?
as agent "touch /usr/local/bin/evil /etc/evil"; check deny "agent cannot write system paths" $?

echo "-- PL side"
as pl "test \"\$(git -C $WT status --porcelain | wc -l)\" -ge 2"; check ok "PL sees the agent's changes" $?
as pl "cat $WT/new.py $WT/pkg/m.py"; check ok "PL can read agent-created files" $?
test ! -e /srv/forgev2; check ok "protected paths still absent" $?
echo "SUMMARY pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
