"""ForgeV2 plugin tests: identity gate, ledger loop limits, guard, commit/push gates.

Run: python3 -m unittest discover -s tests -v
Uses throwaway repositories under a temp dir; nothing touches a real remote.
"""
import json
import os
import random
import shutil
import string
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO, "plugin")
BIN = os.path.join(PLUGIN, "bin")
GUARD = os.path.join(PLUGIN, "hooks", "guard.py")
sys.path.insert(0, os.path.join(PLUGIN, "lib"))
import forgelib as F  # noqa: E402

OWNER_REPO = "fixture-owner/calc"
SESSION = "test-session-0001"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forgev2-test-")
        self.env = dict(os.environ, HOME=self.tmp, FORGE_STATE_DIR=os.path.join(self.tmp, "state"),
                        CLAUDE_CODE_SESSION_ID=SESSION, GIT_CONFIG_NOSYSTEM="1",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@invalid.example",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@invalid.example",
                        PATH=BIN + os.pathsep + os.environ["PATH"])
        os.environ["FORGE_STATE_DIR"] = self.env["FORGE_STATE_DIR"]
        self.root = os.path.join(self.tmp, "src", "calc")
        os.makedirs(self.root)
        self.sh("git init -q -b main . && echo 'def add(a, b):\n    return a + b' > calc.py && "
                "git add -A && git commit -qm init", cwd=self.root)
        self.sh(f"git remote add origin https://github.com/{OWNER_REPO}.git", cwd=self.root)
        self.base = self.sh("git rev-parse HEAD", cwd=self.root).stdout.strip()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def sh(self, cmd, cwd=None, check=True):
        r = subprocess.run(cmd, shell=True, cwd=cwd or self.tmp, env=self.env, capture_output=True, text=True)
        if check and r.returncode:
            raise AssertionError(f"{cmd!r} failed: {r.stdout}{r.stderr}")
        return r

    def run_bin(self, name, *args, cwd=None):
        return subprocess.run([os.path.join(BIN, name), *args], cwd=cwd or self.tmp, env=self.env,
                              capture_output=True, text=True)

    def start(self, *extra, repo=OWNER_REPO):
        return self.run_bin("forge-start", "--wo", "WO-1", "--repo", repo, "--root", self.root, *extra)

    def started(self):
        r = self.start("--known-commit", self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        info = json.loads(r.stdout)
        self.wt, self.ledger = info["worktree"], info["ledger"]
        return info

    def guard(self, tool, tool_input, agent=None):
        ev = {"session_id": SESSION, "tool_name": tool, "tool_input": tool_input, "hook_event_name": "PreToolUse"}
        if agent:
            ev["agent_type"] = f"forgev2:{agent}"
        r = subprocess.run([sys.executable, "-I", GUARD], input=json.dumps(ev), env=self.env,
                           capture_output=True, text=True)
        self.assertIn(r.returncode, (0, 2), r.stderr)
        if r.returncode == 2:
            return "deny"
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        return out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")

    def spawn(self, role):
        return self.guard("Agent", {"subagent_type": f"forgev2:{role}", "prompt": "x", "description": "x"})

    def ledger_cmd(self, *args):
        return self.run_bin("forge-ledger", *args)

    def commit_change(self, text="x = 1\n", name="feature.py"):
        with open(os.path.join(self.wt, name), "a") as f:
            f.write(text)
        return self.run_bin("forge-commit", "-m", "change")


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


class RemoteParsing(unittest.TestCase):
    def test_accepts_canonical_forms(self):
        for url in ("https://github.com/Fixture-Owner/calc.git", "https://github.com/fixture-owner/calc",
                    "git@github.com:fixture-owner/calc.git", "ssh://git@github.com/fixture-owner/calc.git",
                    "https://x-access-token@github.com/fixture-owner/calc.git"):
            self.assertEqual(F.parse_github_remote(url), OWNER_REPO, url)

    def test_rejects_lookalikes_and_non_github(self):
        for url in ("https://github.com.evil.example/fixture-owner/calc.git",
                    "https://evilgithub.com/fixture-owner/calc.git",
                    "http://github.com/fixture-owner/calc.git",
                    "https://github.com/fixture-owner/calc/extra.git",
                    "https://gitlab.com/fixture-owner/calc.git",
                    "/srv/repos/github.com/fixture-owner/calc.git",
                    "file:///github.com/fixture-owner/calc.git",
                    "git@github.com:fixture-owner/../calc.git",
                    "https://github.com/fixture-owner/calc.git?github.com", ""):
            self.assertIsNone(F.parse_github_remote(url), url)


class IdentityGate(Base):
    def test_correct_repository_starts_worktree(self):
        info = self.started()
        self.assertTrue(info["session_bound"])
        self.assertEqual(self.sh("git branch --show-current", cwd=self.wt).stdout.strip(), "forge/WO-1")
        self.assertFalse(info["resumed"])

    def test_rejections(self):
        cases = {
            "wrong owner": dict(repo="other-owner/calc"),
            "wrong name": dict(repo="fixture-owner/calculator"),
            "bad known commit": dict(extra=("--known-commit", "0" * 40)),
        }
        for label, c in cases.items():
            r = self.start(*c.get("extra", ()), repo=c.get("repo", OWNER_REPO))
            self.assertEqual(r.returncode, 1, label)
            self.assertIn("REJECTED", r.stderr, label)

    def test_rejects_lookalike_remote(self):
        self.sh("git remote set-url origin https://github.com.evil.example/fixture-owner/calc.git", cwd=self.root)
        self.assertIn("identity mismatch", self.start().stderr)

    def test_rejects_redirected_push_url(self):
        self.sh(f"git remote set-url --push origin {self.tmp}/elsewhere.git", cwd=self.root)
        self.assertIn("push URL", self.start().stderr)

    def test_rejects_subdirectory_as_root(self):
        os.makedirs(os.path.join(self.root, "sub"))
        r = self.run_bin("forge-start", "--wo", "WO-1", "--repo", OWNER_REPO, "--root", os.path.join(self.root, "sub"))
        self.assertIn("not the repository top level", r.stderr)

    def test_rejects_unrelated_existing_directory(self):
        os.makedirs(os.path.join(self.tmp, "src", "worktrees", "WO-1"))
        self.assertIn("not a ForgeV2 worktree", self.start().stderr)

    def test_resume_keeps_counts(self):
        self.started()
        self.assertEqual(self.spawn("engineer"), "allow")
        r = self.start()
        self.assertEqual(r.returncode, 0, r.stderr)
        info = json.loads(r.stdout)
        self.assertTrue(info["resumed"])
        self.assertEqual(info["counts"]["engineer"], 1)


class LoopLimits(Base):
    def test_no_dispatch_without_work_order(self):
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_engineer_capped_at_four(self):
        self.started()
        self.assertEqual([self.spawn("engineer") for _ in range(5)], ["allow"] * 4 + ["deny"])

    def test_reviewers_need_committed_candidate(self):
        self.started()
        self.spawn("engineer")
        self.assertEqual(self.spawn("auditor"), "deny")           # nothing committed yet
        self.assertEqual(self.commit_change().returncode, 0)
        with open(os.path.join(self.wt, "feature.py"), "a") as f:  # uncommitted change after candidate
            f.write("y = 2\n")
        self.assertEqual(self.spawn("tester"), "deny")
        self.sh("git checkout -q -- feature.py", cwd=self.wt)
        self.assertEqual(self.spawn("tester"), "allow")

    def test_uncounted_helpers_refused_while_open(self):
        self.started()
        self.assertEqual(self.guard("Agent", {"subagent_type": "general-purpose", "prompt": "x"}), "deny")
        self.assertEqual(self.guard("SendMessage", {"to": "a1", "message": "continue"}), "deny")
        self.assertEqual(self.guard("Agent", {"subagent_type": "forgev2:auditor"}, agent="engineer"), "deny")

    def _round(self, auditor="pass", tester="pass", devsecops="pass", findings=None):
        findings = findings or {}
        self.assertEqual(self.spawn("engineer"), "allow")
        self.ledger_cmd("record", "engineer", "completed")
        self.assertEqual(self.commit_change(text=f"# round {random.random()}\n").returncode, 0)
        for role, outcome in (("auditor", auditor), ("tester", tester), ("devsecops", devsecops)):
            self.assertEqual(self.spawn(role), "allow", role)
            args = ["record", role, outcome] + sum((["--finding", f] for f in findings.get(role, [])), [])
            r = self.ledger_cmd(*args)
            self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(self.ledger_cmd("next").stdout)

    def test_findings_then_correction_then_deliver(self):
        self.started()
        d = self._round(tester="findings", findings={"tester": ["zero-div:blocking"]})
        self.assertEqual(d["decision"], "CORRECT")
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 1)  # refused while findings open
        d = self._round()
        self.assertEqual(d["decision"], "DELIVER")
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 0)
        self.assertEqual(self.spawn("engineer"), "deny")  # closed

    def test_correction_invalidates_prior_pass(self):
        self.started()
        self._round(auditor="findings", findings={"auditor": ["scope-creep:blocking"]})
        self.spawn("engineer")
        self.ledger_cmd("record", "engineer", "completed")
        self.commit_change(text="# fix\n")
        d = json.loads(self.ledger_cmd("next").stdout)
        self.assertEqual(d["decision"], "REVIEW")  # tester/devsecops PASS from round 1 no longer count
        self.assertIn("tester", d["reason"])

    def test_repeated_finding_escalates_no_progress(self):
        self.started()
        self._round(tester="findings", findings={"tester": ["zero-div:blocking"]})
        d = self._round(tester="findings", findings={"tester": ["zero-div:blocking"]})
        self.assertEqual(d["decision"], "ESCALATE")
        self.assertIn("no progress", d["reason"])

    def test_limit_escalates_after_four_rounds(self):
        self.started()
        for i in range(4):
            d = self._round(auditor="findings", findings={"auditor": [f"issue-{i}:blocking"]})
        self.assertEqual(d["decision"], "ESCALATE")
        self.assertIn("limit", d["reason"])
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_advisory_and_rejected_do_not_block(self):
        self.started()
        d = self._round(auditor="pass", findings={"auditor": ["naming:advisory"]})
        self.assertEqual(d["decision"], "DELIVER")

    def test_inconclusive_twice_escalates(self):
        self.started()
        self._round(tester="inconclusive")
        d = self._round(tester="inconclusive")
        self.assertEqual(d["decision"], "ESCALATE")

    def test_record_validation(self):
        self.started()
        self.spawn("engineer")
        self.assertEqual(self.ledger_cmd("record", "auditor", "pass").returncode, 1)  # not dispatched
        self.assertEqual(self.ledger_cmd("record", "engineer", "pass").returncode, 1)  # wrong outcome


class Guard(Base):
    def setUp(self):
        super().setUp()
        self.started()
        self.scratch = load(self.ledger)["scratch"]

    def test_engineer_git_writes_denied(self):
        for cmd in ("git commit -am x", "git push origin HEAD", "git reset --hard", "git checkout main",
                    "git stash", "git branch evil", "git tag v1", "git config user.name x",
                    "git -C /tmp commit -m x", "git --git-dir=/x/.git log", "/usr/bin/git commit -m x",
                    "cd src && git add . && git commit -m x", "sh -c 'git commit -m x'",
                    "bash -c \"echo hi; git push\"", "git worktree add ../x", "git remote add x y",
                    "git update-ref refs/heads/x HEAD", "rm -rf .git/hooks", "cat .git/config",
                    "GIT_DIR=/x git log", "git commit --no-verify -m x", "echo 'unbalanced",
                    "ls | xargs git add", "find . -name '*.py' -exec git add {} ;", "FOO=1 git commit -m x",
                    "env -i git push", "timeout 5 git push", "true && git commit -m x", "(git commit -m x)",
                    "if true; then git commit -m x; fi", "eval 'git commit -m x'",
                    "su -c 'git push' forgev2-pl", "/bin/bash -lc 'cd x && git commit -am y'"):
            self.assertEqual(self.guard("Bash", {"command": cmd}, "engineer"), "deny", cmd)

    def test_engineer_reads_and_tests_allowed(self):
        for cmd in ("git status", "git diff HEAD~1", "git log --oneline -3", f"git -C {self.wt} show HEAD",
                    "git branch --show-current", "git config --get user.name", "git worktree list",
                    "python3 -m pytest -q", "cat .gitignore", "ls .github", "env FOO=1 python3 x.py",
                    f"gitleaks git --log-opts=HEAD~1..HEAD --redact --no-banner {self.wt}",
                    "echo git commit is PL-only", "grep -rn 'git push' docs"):
            self.assertEqual(self.guard("Bash", {"command": cmd}, "engineer"), "allow", cmd)

    def test_credentials_and_pl_tools_denied(self):
        for cmd in ("cat ~/.ssh/id_ed25519", "cat /var/lib/forgev2/pl/token", "printenv", "env",
                    "echo $GH_TOKEN", "cat ~/.git-credentials", "cat /proc/1/environ",
                    "forge-ledger record tester pass", "echo x > .forge/WO-1/ledger.json",
                    "cat ~/.claude/.credentials.json", "ls ~/.config/gh"):
            self.assertEqual(self.guard("Bash", {"command": cmd}, "engineer"), "deny", cmd)
        self.assertEqual(self.guard("Read", {"file_path": os.path.expanduser("~/.ssh/id_rsa")}, "tester"), "deny")

    def test_engineer_edit_scope(self):
        ok = os.path.join(self.wt, "calc.py")
        self.assertEqual(self.guard("Edit", {"file_path": ok}, "engineer"), "allow")
        for p in (os.path.join(self.root, "calc.py"), "/etc/passwd", os.path.join(self.wt, ".git"),
                  os.path.join(self.wt, ".forge", "WO-1", "ledger.json"), os.path.join(self.wt, "..", "x.py")):
            self.assertEqual(self.guard("Write", {"file_path": p, "content": ""}, "engineer"), "deny", p)

    def test_engineer_symlink_escape_denied(self):
        os.symlink(self.root, os.path.join(self.wt, "escape"))
        p = os.path.join(self.wt, "escape", "calc.py")
        self.assertEqual(self.guard("Edit", {"file_path": p}, "engineer"), "deny")

    def test_reviewers_read_only(self):
        for role in ("auditor", "tester", "devsecops"):
            self.assertEqual(self.guard("Write", {"file_path": os.path.join(self.wt, "calc.py")}, role), "deny")
            self.assertEqual(self.guard("Bash", {"command": "git commit -m x"}, role), "deny")
        self.assertEqual(self.guard("Write", {"file_path": os.path.join(self.scratch, "t.py")}, "tester"), "allow")

    def test_pl_session_not_restricted(self):
        self.assertEqual(self.guard("Bash", {"command": "git commit -m x"}), "allow")

    def test_unknown_role_and_no_ledger_fail_closed(self):
        self.assertEqual(self.guard("Agent", {"subagent_type": "forgev2:intruder"}), "deny")
        os.remove(F.session_pointer(SESSION))
        self.assertEqual(self.guard("Bash", {"command": "ls"}, "engineer"), "deny")
        self.assertEqual(self.guard("Edit", {"file_path": os.path.join(self.wt, "calc.py")}, "engineer"), "deny")

    def test_malformed_input_blocks(self):
        r = subprocess.run([sys.executable, "-I", GUARD], input="not json", env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


class CommitAndPush(Base):
    def setUp(self):
        super().setUp()
        self.started()

    def test_commit_sets_candidate_and_excludes_record(self):
        r = self.commit_change()
        self.assertEqual(r.returncode, 0, r.stderr)
        d = load(self.ledger)
        self.assertEqual(d["candidate"], self.sh("git rev-parse HEAD", cwd=self.wt).stdout.strip())
        files = self.sh("git show --name-only --format= HEAD", cwd=self.wt).stdout.split()
        self.assertEqual(files, ["feature.py"])

    def test_secret_blocks_commit(self):
        token = "ghp_" + "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(36))
        r = self.commit_change(text=f'TOKEN = "{token}"\n', name="config.py")
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks", r.stderr)
        self.assertNotIn(token, r.stderr + r.stdout)  # redacted
        self.assertEqual(self.sh("git rev-parse HEAD", cwd=self.wt).stdout.strip(), self.base)

    def test_after_close_only_records_commit(self):
        self.commit_change()
        d = load(self.ledger)
        d["outcome"] = "ESCALATED"
        save(self.ledger, d)
        self.assertIn("unreviewed", self.commit_change(text="z = 3\n").stderr)
        self.sh("git checkout -q -- feature.py", cwd=self.wt)
        r = self.run_bin("forge-commit", "-m", "record")
        self.assertEqual(r.returncode, 0, r.stderr)
        files = self.sh("git show --name-only --format= HEAD", cwd=self.wt).stdout.split()
        self.assertTrue(files and all(f.startswith(".forge/") for f in files), files)

    def test_push_requires_closed_work_order(self):
        self.assertIn("close the Work Order", self.run_bin("forge-push").stderr)

    def test_push_rechecks_identity(self):
        d = load(self.ledger)
        d["outcome"] = "ESCALATED"
        save(self.ledger, d)
        self.run_bin("forge-commit", "-m", "record")
        self.sh(f"git remote set-url --push origin {self.tmp}/attacker.git", cwd=self.root)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("push URL", r.stderr)


if __name__ == "__main__":
    unittest.main()
