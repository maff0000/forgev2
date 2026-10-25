#!/usr/bin/env bash
# ForgeV2 OS boundary check on an execution host (run as root; read-mostly).
# Uses the existing forgev2-pl / forgev2-agent identities against a disposable
# fixture and confirms the Engineer identity cannot alter PL-owned Git metadata,
# read PL credentials, or write engine/protected/other-project paths.
# Usage: sudo tests/host/os-boundary.sh [PLUGIN_DIR]
set -u
[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 2; }
for u in forgev2-pl forgev2-agent; do id "$u" >/dev/null 2>&1 || { echo "missing identity $u" >&2; exit 2; }; done
PLUGIN_DIR=$(realpath "${1:-$(dirname "$0")/../../plugin}")
FX=$(mktemp -d /tmp/forgev2-ostest-XXXXXX); chmod 0755 "$FX"
trap 'rm -rf --one-file-system -- "$FX"' EXIT
pass=0; fail=0
as() { local u=$1; shift; (cd / && runuser -u "forgev2-$u" -- /usr/bin/env -i HOME="/var/lib/forgev2/$u" \
       USER="forgev2-$u" LOGNAME="forgev2-$u" PATH=/usr/bin:/bin /bin/sh -c "$*") >/dev/null 2>&1; }
check() { # check ok|deny DESC rc
  if { [ "$1" = ok ] && [ "$3" -eq 0 ]; } || { [ "$1" = deny ] && [ "$3" -ne 0 ]; }; then
    echo "PASS $2"; pass=$((pass+1)); else echo "FAIL $2 (rc=$3)"; fail=$((fail+1)); fi; }
C="-c user.name=t -c user.email=t@invalid.example -c core.hooksPath=/dev/null"; G="git $C"

# Fixture: root-owned canonical checkout, PL-owned .git and worktree parent, PL-only credential marker.
mkdir -p "$FX/main" "$FX/other-project" "$FX/pl-home"
(cd "$FX/main" && git init -q -b main . && echo x > a.txt && $G add -A && $G commit -qm init) >/dev/null
chmod -R a+rX "$FX/main"
chown -R forgev2-pl:forgev2-pl "$FX/main/.git"
install -d -o forgev2-pl -g forgev2-pl -m 0711 "$FX/worktrees"
chown forgev2-pl:forgev2-pl "$FX/pl-home"; chmod 0700 "$FX/pl-home"
install -o forgev2-pl -g forgev2-pl -m 0600 /dev/null "$FX/pl-home/token"; echo SYNTHETIC > "$FX/pl-home/token"
GD="git --git-dir=$FX/main/.git"

as pl "umask 0007; $GD $C worktree add -q -b forge/T $FX/worktrees/T main"; check ok "PL creates WO worktree" $?
as pl "cd $FX/worktrees/T && echo y >> a.txt && $G commit -qam pl-change"; check ok "PL commits in WO worktree" $?
as agent "$GD update-ref refs/heads/evil HEAD"; check deny "Engineer cannot write refs" $?
as agent "touch $FX/main/.git/objects/evil"; check deny "Engineer cannot write objects" $?
as agent "touch $FX/main/.git/hooks/pre-commit"; check deny "Engineer cannot install hooks" $?
as agent "$GD config core.hooksPath /tmp"; check deny "Engineer cannot change Git config" $?
as agent "cd $FX/main && GIT_DIR=$FX/main/.git $G commit --allow-empty -qm evil"; check deny "Engineer cannot commit" $?
as agent "cat $FX/pl-home/token"; check deny "Engineer cannot read PL credential" $?
as agent "ls /var/lib/forgev2/pl"; check deny "Engineer cannot list real PL home" $?
as agent "touch $FX/main/evil"; check deny "Engineer cannot write canonical checkout" $?
as agent "touch $FX/other-project/evil"; check deny "Engineer cannot write unrelated project" $?
as agent "mkdir $FX/worktrees/evil"; check deny "Engineer cannot create worktrees" $?
as agent "touch $PLUGIN_DIR/evil"; check deny "Engineer cannot write the ForgeV2 plugin" $?
as agent "mkdir /srv/forgev2"; check deny "Engineer cannot create engine install path" $?
as agent "mkdir /srv/pacman"; check deny "Engineer cannot create other application root" $?
as agent "touch /srv/src/forgev2/evil"; check deny "Engineer cannot write engine source tree" $?
as agent "sudo -n true"; check deny "Engineer has no sudo" $?
as agent 'test -z "$SSH_AUTH_SOCK$GH_TOKEN$GITHUB_TOKEN$GIT_ASKPASS"'; check ok "Engineer env carries no credentials" $?
test ! -e /srv/forgev2 && test ! -e /srv/pacman; check ok "Protected paths still absent" $?
echo "SUMMARY pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
