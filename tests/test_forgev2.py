"""ForgeV2 plugin tests: identity gate, ledger and loop rules, guard, commit/push gates.

Run: python3 -m unittest discover -s tests -v
Prerequisite: an approved gitleaks build at /usr/local/bin or /usr/bin (see INSTALL.md);
without it every commit-path test fails with an explicit message, by design.
Uses throwaway repositories under a temp dir; pushes are stopped at the transport
(GIT_ALLOW_PROTOCOL=file), so nothing reaches a real remote.
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
try:
    F.gitleaks_bin()
    GITLEAKS_PROBLEM = None
except F.ForgeError as e:
    GITLEAKS_PROBLEM = str(e)


def token():
    return "ghp_" + "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(36))


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forgev2-test-")
        os.chmod(self.tmp, 0o700)
        self.env = dict(os.environ, HOME=self.tmp, FORGE_STATE_DIR=os.path.join(self.tmp, "state"),
                        CLAUDE_CODE_SESSION_ID=SESSION, GIT_CONFIG_NOSYSTEM="1", FORGE_ALLOW_ROOT="1",
                        GIT_ALLOW_PROTOCOL="file", GIT_TERMINAL_PROMPT="0",
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@invalid.example",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@invalid.example",
                        PATH=BIN + os.pathsep + os.environ["PATH"])
        self._saved = {k: os.environ.get(k) for k in ("FORGE_STATE_DIR", "HOME", "FORGE_ALLOW_ROOT")}
        os.environ.update(FORGE_STATE_DIR=self.env["FORGE_STATE_DIR"], HOME=self.tmp, FORGE_ALLOW_ROOT="1")
        self.root = os.path.join(self.tmp, "src", "calc")
        os.makedirs(self.root)
        self.sh("git init -q -b main . && echo 'def add(a, b):\n    return a + b' > calc.py && "
                "git add -A && git commit -qm init", cwd=self.root)
        self.sh(f"git remote add origin https://github.com/{OWNER_REPO}.git", cwd=self.root)
        self.base = self.sh("git rev-parse HEAD", cwd=self.root).stdout.strip()

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def need_gitleaks(self):
        if GITLEAKS_PROBLEM:
            self.fail(f"PREREQUISITE MISSING - install an approved gitleaks (INSTALL.md): {GITLEAKS_PROBLEM}")

    def sh(self, cmd, cwd=None, check=True):
        r = subprocess.run(cmd, shell=True, cwd=cwd or self.tmp, env=self.env, capture_output=True, text=True)
        if check and r.returncode:
            raise AssertionError(f"{cmd!r} failed: {r.stdout}{r.stderr}")
        return r

    def run_bin(self, name, *args, cwd=None, env=None):
        return subprocess.run([os.path.join(BIN, name), *args], cwd=cwd or self.tmp, env=env or self.env,
                              capture_output=True, text=True)

    def start(self, *extra, repo=OWNER_REPO, env=None):
        return self.run_bin("forge-start", "--wo", "WO-1", "--repo", repo, "--root", self.root, *extra, env=env)

    def started(self):
        r = self.start("--known-commit", self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        info = json.loads(r.stdout)
        self.wt, self.ledger, self.scratch = info["worktree"], info["ledger"], info["scratch"]
        return info

    def guard(self, tool, tool_input, agent=None, cwd=None):
        ev = {"session_id": SESSION, "tool_name": tool, "tool_input": tool_input, "hook_event_name": "PreToolUse",
              "cwd": cwd or self.root}
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

    def head(self):
        return self.sh("git rev-parse HEAD", cwd=self.wt).stdout.strip()

    def write(self, name, text, mode="a"):
        with open(os.path.join(self.wt, name), mode) as f:
            f.write(text)

    def engineer(self, text=None, name="feature.py", outcome="completed"):
        self.assertEqual(self.spawn("engineer"), "allow")
        if text is not None:
            self.write(name, text)
        r = self.ledger_cmd("record", "engineer", outcome)
        self.assertEqual(r.returncode, 0, r.stderr)

    def commit(self, msg="change"):
        return self.run_bin("forge-commit", "-m", msg)

    def build(self, text=None):
        self.need_gitleaks()
        self.engineer(text if text is not None else f"# change {random.random()}\n")
        r = self.commit()
        self.assertEqual(r.returncode, 0, r.stderr)

    def review(self, results=None, findings=None):
        results, findings = results or {}, findings or {}
        for role in F.REVIEWERS:
            self.assertEqual(self.spawn(role), "allow", role)
            args = ["record", role, results.get(role, "pass")]
            for f in findings.get(role, []):
                args += ["--finding", f]
            r = self.ledger_cmd(*args)
            self.assertEqual(r.returncode, 0, r.stderr)
        return self.next()

    def next(self):
        return json.loads(self.ledger_cmd("next").stdout)

    def deliver(self):
        self.started()
        self.build()
        self.assertEqual(self.review()["decision"], "DELIVER")
        r = self.ledger_cmd("close", "DELIVERED")
        self.assertEqual(r.returncode, 0, r.stderr)


class Prerequisites(unittest.TestCase):
    def test_gitleaks_installed_and_approved(self):
        self.assertIsNone(GITLEAKS_PROBLEM, "install an approved gitleaks build (INSTALL.md)")

    def test_missing_or_unapproved_gitleaks_refused(self):
        paths, digests = F.GITLEAKS_PATHS, F.GITLEAKS_SHA256
        try:
            F.GITLEAKS_PATHS = ("/nonexistent/gitleaks",)
            self.assertRaisesRegex(F.ForgeError, "not installed", F.gitleaks_bin)
            F.GITLEAKS_PATHS, F.GITLEAKS_SHA256 = paths, {}
            if not GITLEAKS_PROBLEM:
                self.assertRaisesRegex(F.ForgeError, "not an approved", F.gitleaks_bin)
        finally:
            F.GITLEAKS_PATHS, F.GITLEAKS_SHA256 = paths, digests


class RemoteParsing(unittest.TestCase):
    def test_accepts_canonical_forms(self):
        for url in ("https://github.com/Fixture-Owner/calc.git", "https://github.com/fixture-owner/calc",
                    "git@github.com:fixture-owner/calc.git", "ssh://git@github.com/fixture-owner/calc.git",
                    "https://x-access-token@github.com/fixture-owner/calc.git"):
            self.assertEqual(F.parse_github_remote(url), OWNER_REPO, url)

    def test_rejects_lookalikes_non_github_and_embedded_secrets(self):
        for url in ("https://github.com.evil.example/fixture-owner/calc.git",
                    "https://evilgithub.com/fixture-owner/calc.git",
                    "http://github.com/fixture-owner/calc.git",
                    "https://github.com/fixture-owner/calc/extra.git",
                    "https://gitlab.com/fixture-owner/calc.git",
                    "/srv/repos/github.com/fixture-owner/calc.git",
                    "file:///github.com/fixture-owner/calc.git",
                    "git@github.com:fixture-owner/../calc.git",
                    "https://github.com/fixture-owner/calc.git?github.com",
                    "https://user:" + token() + "@github.com/fixture-owner/calc.git", ""):
            self.assertIsNone(F.parse_github_remote(url), url)


class IdentityGate(Base):
    def test_correct_repository_starts_worktree(self):
        info = self.started()
        self.assertTrue(info["session_bound"])
        self.assertEqual(self.sh("git branch --show-current", cwd=self.wt).stdout.strip(), "forge/WO-1")
        self.assertFalse(info["resumed"])

    def test_ledger_and_scratch_outside_worktree_and_home(self):
        self.started()
        self.assertFalse(os.path.realpath(self.ledger).startswith(os.path.realpath(self.wt) + os.sep))
        self.assertFalse(os.path.exists(os.path.join(self.wt, ".forge")))
        self.assertFalse(os.path.realpath(self.scratch).startswith(os.path.realpath(self.env["FORGE_STATE_DIR"])))
        self.assertEqual(os.stat(self.env["FORGE_STATE_DIR"]).st_mode & 0o777, 0o700)

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

    def test_rejects_additional_push_url(self):
        self.sh(f"git remote set-url --add --push origin https://github.com/{OWNER_REPO}.git", cwd=self.root)
        self.sh("git remote set-url --add --push origin https://github.com/evil/calc.git", cwd=self.root)
        self.assertIn("exactly one push URL", self.start().stderr)

    def test_rejects_url_rewriting(self):
        self.sh(f"git config url.{self.tmp}/evil.git.pushInsteadOf https://github.com/{OWNER_REPO}.git",
                cwd=self.root)
        self.assertIn("URL rewriting", self.start().stderr)

    def test_rejects_subdirectory_as_root(self):
        os.makedirs(os.path.join(self.root, "sub"))
        r = self.run_bin("forge-start", "--wo", "WO-1", "--repo", OWNER_REPO, "--root", os.path.join(self.root, "sub"))
        self.assertIn("not the repository top level", r.stderr)

    def test_rejects_unrelated_existing_directory(self):
        os.makedirs(os.path.join(self.tmp, "src", "worktrees", "WO-1"))
        self.assertIn("no ForgeV2 ledger", self.start().stderr)

    def test_rejects_base_with_records_for_same_wo(self):
        os.makedirs(os.path.join(self.root, ".forge", "WO-1"))
        save(os.path.join(self.root, ".forge", "WO-1", "ledger.json"), {"limit": 1000})
        self.sh("git add -A && git commit -qm planted", cwd=self.root)
        r = self.start()
        self.assertEqual(r.returncode, 1)
        self.assertIn("already contains records", r.stderr)

    def test_refuses_root_without_override(self):
        env = dict(self.env)
        env.pop("FORGE_ALLOW_ROOT")
        r = self.start(env=env)
        if os.geteuid() == 0:
            self.assertEqual(r.returncode, 1)
            self.assertIn("must not run as root", r.stderr)
        else:
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_resume_keeps_counts(self):
        self.started()
        self.assertEqual(self.spawn("engineer"), "allow")
        r = self.start()
        self.assertEqual(r.returncode, 0, r.stderr)
        info = json.loads(r.stdout)
        self.assertTrue(info["resumed"])
        self.assertEqual(info["counts"]["engineer"], 1)


class LedgerRules(Base):
    def test_no_dispatch_without_work_order(self):
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_engineer_capped_at_four(self):
        self.started()
        got = []
        for _ in range(5):
            got.append(self.spawn("engineer"))
            if got[-1] == "allow":
                self.ledger_cmd("record", "engineer", "void")
        self.assertEqual(got, ["allow"] * 4 + ["deny"])

    def test_limit_in_ledger_is_ignored(self):
        self.started()
        d = load(self.ledger)
        d["limit"], d["counts"]["engineer"] = 99, 4
        save(self.ledger, d)
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_result_needs_its_own_dispatch(self):
        self.started()
        self.assertEqual(self.ledger_cmd("record", "engineer", "completed").returncode, 1)  # not dispatched
        self.spawn("engineer")
        self.assertEqual(self.spawn("engineer"), "deny")                                   # result pending
        self.assertEqual(self.ledger_cmd("record", "engineer", "completed").returncode, 0)
        self.assertEqual(self.ledger_cmd("record", "engineer", "completed").returncode, 1)  # one per dispatch

    def test_pass_cannot_be_recorded_without_fresh_review(self):
        """Audit finding 1: after a correction, earlier dispatches cannot vouch for the new candidate."""
        self.started()
        self.build()
        self.assertEqual(self.review({"auditor": "findings"}, {"auditor": ["bug:blocking"]})["decision"], "CORRECT")
        self.build()
        for role in F.REVIEWERS:
            self.assertEqual(self.ledger_cmd("record", role, "pass").returncode, 1, role)
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 1)
        self.assertEqual(self.ledger_cmd("record", "auditor", "pass").returncode, 1)

    def test_blocking_result_cannot_be_overwritten(self):
        self.started()
        self.build()
        self.review({"auditor": "findings"}, {"auditor": ["bug:blocking"]})
        self.assertEqual(self.ledger_cmd("record", "auditor", "pass").returncode, 1)
        self.assertEqual(self.spawn("auditor"), "deny")  # next step is CORRECT, not REVIEW
        self.assertEqual(self.next()["decision"], "CORRECT")

    def test_candidate_cannot_change_while_review_pending(self):
        self.started()
        self.build()
        self.assertEqual(self.spawn("auditor"), "allow")
        self.write("feature.py", "y = 2\n")
        r = self.commit()
        self.assertEqual(r.returncode, 1)
        self.assertIn("awaiting its result", r.stderr)

    def test_reviewers_need_committed_unchanged_candidate(self):
        self.started()
        self.need_gitleaks()
        self.engineer("x = 1\n")
        self.assertEqual(self.next()["decision"], "COMMIT")
        self.assertEqual(self.spawn("auditor"), "deny")  # nothing committed yet
        self.assertEqual(self.commit().returncode, 0)
        self.write("feature.py", "y = 2\n")               # uncommitted change after candidate
        self.assertEqual(self.spawn("tester"), "deny")
        self.sh("git checkout -q -- feature.py", cwd=self.wt)
        self.assertEqual(self.spawn("tester"), "allow")

    def test_commit_only_after_engineer(self):
        self.started()
        self.need_gitleaks()
        self.write("feature.py", "pl_wrote_this = 1\n")
        r = self.commit()
        self.assertEqual(r.returncode, 1)
        self.assertIn("next step is BUILD", r.stderr)

    def test_uncounted_helpers_refused_while_open(self):
        self.started()
        self.assertEqual(self.guard("Agent", {"subagent_type": "general-purpose", "prompt": "x"}), "deny")
        self.assertEqual(self.guard("Task", {"subagent_type": "general-purpose", "prompt": "x"}), "deny")
        self.assertEqual(self.guard("SendMessage", {"to": "a1", "message": "continue"}), "deny")
        self.assertEqual(self.guard("Agent", {"subagent_type": "forgev2:auditor"}, agent="engineer"), "deny")

    def test_task_alias_is_counted(self):
        self.started()
        self.assertEqual(self.guard("Task", {"subagent_type": "forgev2:engineer", "prompt": "x"}), "allow")
        self.assertEqual(load(self.ledger)["counts"]["engineer"], 1)

    def test_findings_then_correction_then_deliver(self):
        self.started()
        self.build()
        d = self.review({"tester": "findings"}, {"tester": ["zero-div:blocking"]})
        self.assertEqual(d["decision"], "CORRECT")
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 1)  # refused while findings open
        self.build()
        self.assertEqual(self.review()["decision"], "DELIVER")
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 0)
        self.assertEqual(self.spawn("engineer"), "deny")  # closed

    def test_correction_invalidates_prior_pass(self):
        self.started()
        self.build()
        self.review({"auditor": "findings"}, {"auditor": ["scope-creep:blocking"]})
        self.build()
        d = self.next()
        self.assertEqual(d["decision"], "REVIEW")
        self.assertEqual(d["needs_review"], list(F.REVIEWERS))

    def test_repeated_finding_escalates_and_stops_dispatch(self):
        self.started()
        self.build()
        self.review({"tester": "findings"}, {"tester": ["zero-div:blocking"]})
        self.build()
        d = self.review({"tester": "findings"}, {"tester": ["zero-div:blocking"]})
        self.assertEqual(d["decision"], "ESCALATE")
        self.assertIn("no progress", d["reason"])
        self.assertEqual(self.spawn("engineer"), "deny")  # escalation is binding
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 1)

    def test_correction_without_change_escalates(self):
        """Live run WO-CALC-007: a 'completed' correction that changes nothing is no progress."""
        self.started()
        self.build()
        self.review({"tester": "findings"}, {"tester": ["zero-div:blocking"]})
        self.engineer()                      # reports completed, changes nothing
        r = self.commit()
        self.assertEqual(r.returncode, 1)
        self.assertIn("no progress", r.stderr)
        self.assertEqual(self.next()["decision"], "ESCALATE")
        self.assertEqual(self.spawn("engineer"), "deny")
        self.assertEqual(self.ledger_cmd("close", "DELIVERED").returncode, 1)

    def test_limit_escalates_after_four_rounds(self):
        self.started()
        for i in range(4):
            self.build()
            d = self.review({"auditor": "findings"}, {"auditor": [f"issue-{i}:blocking"]})
        self.assertEqual(d["decision"], "ESCALATE")
        self.assertIn("limit", d["reason"])
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_advisory_and_rejected_do_not_block(self):
        self.started()
        self.build()
        d = self.review(findings={"auditor": ["naming:advisory"], "tester": ["style:rejected"]})
        self.assertEqual(d["decision"], "DELIVER")

    def test_inconclusive_twice_on_same_candidate_escalates(self):
        self.started()
        self.build()
        self.assertEqual(self.review({"tester": "inconclusive"})["decision"], "REVIEW")
        self.assertEqual(self.spawn("auditor"), "deny")   # only the inconclusive reviewer re-runs
        self.assertEqual(self.spawn("tester"), "allow")
        self.ledger_cmd("record", "tester", "inconclusive")
        self.assertEqual(self.next()["decision"], "ESCALATE")

    def test_inconclusive_not_consecutive_does_not_escalate(self):
        self.started()
        self.build()
        self.review({"tester": "inconclusive"})
        self.spawn("tester")
        self.ledger_cmd("record", "tester", "pass")
        self.assertEqual(self.next()["decision"], "DELIVER")

    def test_closed_work_order_is_immutable(self):
        self.started()
        self.engineer(outcome="blocked")
        self.assertEqual(self.next()["decision"], "BLOCKED")
        self.assertEqual(self.ledger_cmd("close", "BLOCKED").returncode, 0)
        self.assertEqual(self.ledger_cmd("close", "ESCALATED").returncode, 1)
        self.assertEqual(self.ledger_cmd("record", "engineer", "completed").returncode, 1)
        self.assertEqual(load(self.ledger)["outcome"], "BLOCKED")

    def test_no_result_accepted_after_close(self):
        self.started()
        self.build()
        self.assertEqual(self.spawn("auditor"), "allow")   # dispatch still pending at close
        self.assertEqual(self.ledger_cmd("close", "ESCALATED").returncode, 0)
        r = self.ledger_cmd("record", "auditor", "pass")
        self.assertEqual(r.returncode, 1)
        self.assertIn("closed", r.stderr)

    def test_corrupt_ledger_fails_cleanly(self):
        self.started()
        with open(self.ledger, "w") as f:
            f.write('{"wo": "WO-1", "coun')
        r = self.ledger_cmd("status")
        self.assertEqual(r.returncode, 1)
        self.assertIn("corrupt", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.spawn("engineer"), "deny")

    def test_record_validation(self):
        self.started()
        self.spawn("engineer")
        self.assertEqual(self.ledger_cmd("record", "engineer", "pass").returncode, 1)  # wrong outcome
        self.assertEqual(self.ledger_cmd("record", "auditor", "pass").returncode, 1)   # not dispatched


class Guard(Base):
    def setUp(self):
        super().setUp()
        self.started()

    def test_engineer_git_writes_denied(self):
        for cmd in ("git commit -am x", "git push origin HEAD", "git reset --hard", "git checkout main",
                    "git stash", "git branch evil", "git tag v1", "git config user.name x",
                    "git -C /tmp commit -m x", "git --git-dir=/x/.git log", "/usr/bin/git commit -m x",
                    "cd src && git add . && git commit -m x", "sh -c 'git commit -m x'",
                    "bash -c \"echo hi; git push\"", "git worktree add ../x", "git remote add x y",
                    "git remote -v set-url --add --push origin https://github.com/evil/x.git",
                    "git remote -v rename origin x", "git -c core.pager='sh -c x' log",
                    "git log --output=/tmp/x", "git diff --ext-diff",
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
                    "git remote -v", "git remote get-url origin",
                    "python3 -m pytest -q", "cat .gitignore", "ls .github", "env FOO=1 python3 x.py",
                    f"gitleaks git --log-opts=HEAD~1..HEAD --redact --no-banner {self.wt}",
                    "echo git commit is PL-only", "grep -rn 'git push' docs"):
            self.assertEqual(self.guard("Bash", {"command": cmd}, "engineer"), "allow", cmd)

    def test_credentials_state_and_pl_tools_denied(self):
        for cmd in ("cat ~/.ssh/id_ed25519", "cat /var/lib/forgev2/pl/token", "printenv", "env",
                    "echo $GH_TOKEN", "cat ~/.git-credentials", "cat /proc/1/environ",
                    "forge-ledger record tester pass", f"cat {self.ledger}",
                    "sed -i s/4/0/ ~/.local/state/forgev2/ledgers/x/WO-1/ledger.json",
                    "cat ~/.claude/.credentials.json", "ls ~/.config/gh"):
            self.assertEqual(self.guard("Bash", {"command": cmd}, "engineer"), "deny", cmd)

    def test_file_tools_confined_to_allowed_directories(self):
        home = self.tmp
        for tool, ti in (("Read", {"file_path": "/etc/shadow"}),
                         ("Read", {"file_path": os.path.join(home, ".config", "gh", "hosts.yml")}),
                         ("Read", {"file_path": self.ledger}),
                         ("Grep", {"pattern": "oauth_token", "path": os.path.join(home, ".config")}),
                         ("Grep", {"pattern": "x", "path": "/"}),
                         ("Glob", {"pattern": "**/.ssh/*", "path": home}),
                         ("Glob", {"pattern": "/etc/*"}),
                         ("Glob", {"pattern": "../../*"})):
            for role in ("engineer", "tester"):
                self.assertEqual(self.guard(tool, ti, role), "deny", (role, tool, ti))
        for tool, ti in (("Read", {"file_path": os.path.join(self.wt, "calc.py")}),
                         ("Read", {"file_path": os.path.join(self.root, "calc.py")}),
                         ("Grep", {"pattern": "def", "path": self.wt}),
                         ("Grep", {"pattern": "def"}),
                         ("Glob", {"pattern": "**/*.py", "path": self.wt})):
            self.assertEqual(self.guard(tool, ti, "auditor"), "allow", (tool, ti))

    def test_specialists_limited_to_known_tools(self):
        for tool in ("WebFetch", "Monitor", "Workflow", "mcp__github__create_pull_request", "NotARealTool"):
            self.assertEqual(self.guard(tool, {"url": "https://example.com"}, "engineer"), "deny", tool)

    def test_engineer_edit_scope(self):
        ok = os.path.join(self.wt, "calc.py")
        self.assertEqual(self.guard("Edit", {"file_path": ok}, "engineer"), "allow")
        for p in (os.path.join(self.root, "calc.py"), "/etc/passwd", os.path.join(self.wt, ".git"),
                  os.path.join(self.wt, "sub", ".git", "config"),
                  os.path.join(self.wt, ".forge", "WO-1", "REPORT.md"), os.path.join(self.wt, "..", "x.py"),
                  self.ledger):
            self.assertEqual(self.guard("Write", {"file_path": p, "content": ""}, "engineer"), "deny", p)

    def test_engineer_symlink_escape_denied(self):
        os.symlink(self.root, os.path.join(self.wt, "escape"))
        p = os.path.join(self.wt, "escape", "calc.py")
        self.assertEqual(self.guard("Edit", {"file_path": p}, "engineer"), "deny")

    def test_reviewers_write_only_scratch(self):
        for role in ("auditor", "tester", "devsecops"):
            self.assertEqual(self.guard("Write", {"file_path": os.path.join(self.wt, "calc.py")}, role), "deny")
            self.assertEqual(self.guard("Bash", {"command": "git commit -m x"}, role), "deny")
        self.assertEqual(self.guard("Write", {"file_path": os.path.join(self.scratch, "t.py")}, "tester"), "allow")

    def test_pl_git_writes_go_through_forge_tools(self):
        for cmd in ("git commit -am x", f"git -C {self.wt} push origin HEAD", "git push --force origin x",
                    "git commit --no-verify -m x"):
            self.assertEqual(self.guard("Bash", {"command": cmd}), "deny", cmd)
        for cmd in ("forge-commit -m 'fix git push bug'", "forge-ledger next", "git log --oneline -3",
                    f"git -C {self.wt} status"):
            self.assertEqual(self.guard("Bash", {"command": cmd}), "allow", cmd)
        self.assertEqual(self.guard("Write", {"file_path": self.ledger, "content": "{}"}), "deny")

    def test_pl_unrestricted_without_work_order(self):
        os.remove(F.session_pointer(SESSION))
        self.assertEqual(self.guard("Bash", {"command": "git commit -m x"}), "allow")

    def test_unknown_role_and_no_ledger_fail_closed(self):
        self.assertEqual(self.guard("Agent", {"subagent_type": "forgev2:intruder"}), "deny")
        self.assertEqual(self.guard("Bash", {"command": "ls"}, "intruder"), "deny")
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
        self.need_gitleaks()
        self.started()

    def test_commit_sets_candidate_and_excludes_records(self):
        self.engineer("x = 1\n")
        os.makedirs(os.path.join(self.wt, ".forge"), exist_ok=True)
        self.write(".forge/stray.txt", "x")
        r = self.commit()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(load(self.ledger)["candidate"], self.head())
        files = self.sh("git show --name-only --format= HEAD", cwd=self.wt).stdout.split()
        self.assertEqual(files, ["feature.py"])

    def test_secret_blocks_commit(self):
        t = token()
        self.engineer(f'TOKEN = "{t}"\n', name="config.py")
        r = self.commit()
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks", r.stderr)
        self.assertNotIn(t, r.stderr + r.stdout)  # redacted
        self.assertEqual(self.head(), self.base)

    def test_repository_cannot_suppress_the_secret_scan(self):
        """Inline allow comments, a repository .gitleaks.toml and .gitleaksignore are not honoured."""
        t = token()
        self.engineer(f'A = "{t}"  # gitleaks:allow\n', name="a.py")
        self.write(".gitleaks.toml", '[allowlist]\npaths = [".*"]\n')
        self.write(".gitleaksignore", f"a.py:github-pat:1\n")
        r = self.commit()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertEqual(self.head(), self.base)

    def test_out_of_band_commit_blocks_commit(self):
        """A commit made outside forge-commit (e.g. a secret committed directly) is never adopted."""
        self.engineer()
        self.write("sneak.py", f'T = "{token()}"\n')
        self.sh("git add -A && git commit -qm sneak", cwd=self.wt)
        self.write("feature.py", "x = 1\n")
        r = self.commit()
        self.assertEqual(r.returncode, 1)
        self.assertIn("outside forge-commit", r.stderr)

    def test_worktree_hooks_not_run_by_pl(self):
        marker = os.path.join(self.tmp, "hook-ran")
        os.makedirs(os.path.join(self.wt, "hooks"))
        self.write("hooks/pre-commit", f"#!/bin/sh\ntouch {marker}\n")
        os.chmod(os.path.join(self.wt, "hooks", "pre-commit"), 0o755)
        self.sh("git config core.hooksPath hooks", cwd=self.root)
        self.engineer("x = 1\n")
        self.assertEqual(self.commit().returncode, 0)
        self.assertFalse(os.path.exists(marker), "a hook from the worktree ran as the PL")

    def test_tampered_worktree_git_pointer_is_ignored(self):
        decoy = os.path.join(self.tmp, "decoy")
        self.sh(f"git init -q {decoy} && git -C {decoy} commit -q --allow-empty -m d")
        decoy_head = self.sh(f"git -C {decoy} rev-parse HEAD").stdout.strip()
        with open(os.path.join(self.wt, ".git"), "w") as f:
            f.write(f"gitdir: {decoy}/.git\n")
        self.engineer("x = 1\n")
        self.assertEqual(self.commit().returncode, 0)
        self.assertEqual(self.sh(f"git -C {decoy} rev-parse HEAD").stdout.strip(), decoy_head)
        real = self.sh("git rev-parse refs/heads/forge/WO-1", cwd=self.root).stdout.strip()
        self.assertEqual(real, load(self.ledger)["candidate"])

    def test_push_requires_closed_work_order(self):
        self.assertIn("close the Work Order", self.run_bin("forge-push").stderr)


class DeliveryEndToEnd(Base):
    def records(self):
        os.makedirs(os.path.join(self.wt, ".forge", "WO-1", "reviews"), exist_ok=True)
        self.write(".forge/WO-1/REPORT.md", "# WO-1 - DELIVERED\n")
        self.write(".forge/WO-1/reviews/r1-auditor.md", "PASS\n")
        r = self.commit("WO-1: delivery record")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_close_records_push_reaches_transport(self):
        self.deliver()
        self.assertTrue(os.path.isfile(os.path.join(self.wt, ".forge", "WO-1", "ledger.json")))
        self.records()
        files = self.sh("git show --name-only --format= HEAD", cwd=self.wt).stdout.split()
        self.assertTrue(files and all(f.startswith(".forge/WO-1/") for f in files), files)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("transport 'https' not allowed", r.stderr)  # every gate passed; stopped before network

    def test_after_close_only_records_commit(self):
        self.deliver()
        self.write("feature.py", "z = 3\n")
        self.assertIn("unreviewed", self.commit().stderr)
        self.sh("git checkout -q -- feature.py", cwd=self.wt)
        self.write(".forge/WO-1/payload.sh", "rm -rf /\n")
        self.assertIn("unreviewed", self.commit().stderr)

    def test_push_refuses_unreviewed_commit_after_delivery(self):
        """Audit finding 2."""
        self.deliver()
        self.records()
        self.write("calc.py", "import os; os.system('id')\n")
        self.sh("git commit -qam sneaky", cwd=self.wt)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unreviewed", r.stderr)

    def test_close_delivered_refuses_head_beyond_candidate(self):
        self.started()
        self.build()
        self.review()
        self.write("calc.py", "evil = 1\n")
        self.sh("git commit -qam sneaky", cwd=self.wt)
        r = self.ledger_cmd("close", "DELIVERED")
        self.assertEqual(r.returncode, 1)
        self.assertIn("not exactly the reviewed candidate", r.stderr)

    def test_push_scans_whole_branch_history(self):
        self.deliver()
        self.records()
        self.write(".forge/WO-1/REPORT.md", f'token {token()}\n')
        self.sh("git commit -qam report", cwd=self.wt)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks", r.stderr)

    def test_push_rechecks_identity(self):
        self.deliver()
        self.records()
        self.sh(f"git remote set-url --push origin {self.tmp}/attacker.git", cwd=self.root)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("push URL", r.stderr)

    def test_push_refuses_non_forge_branch(self):
        self.deliver()
        self.records()
        d = load(self.ledger)
        d["branch"] = "main"
        save(self.ledger, d)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("pushes only forge/<WO>", r.stderr)


if __name__ == "__main__":
    unittest.main()
