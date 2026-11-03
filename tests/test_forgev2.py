"""ForgeV2 plugin tests: identity gate, ledger and loop rules, dispatch, sandbox settings, guard, commit/push gates.

Run: python3 -m unittest discover -s tests -v
Prerequisite: an approved gitleaks build at /usr/local/bin or /usr/bin (see INSTALL.md);
without it every commit-path test fails with an explicit message, by design.
Uses throwaway repositories under a temp dir; pushes are stopped at the transport
(GIT_ALLOW_PROTOCOL=file), so nothing reaches a real remote. Specialists are
replaced by a fake `claude` (FORGE_CLAUDE); tests/host/sandbox-boundary.sh runs
real sandboxed specialists against the host.
"""
import json
import os
import random
import shutil
import socket
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


FAKE_CLAUDE = r'''#!/usr/bin/python3
# Test stand-in for a specialist `claude -p` run: argv as built by forge-dispatch, prompt on stdin.
import json, os, subprocess, sys
role = os.environ["FORGE_ROLE"]
wt = json.loads(sys.argv[sys.argv.index("--settings") + 1])["sandbox"]["filesystem"]["denyWrite"][0][:-len("/.git")]
d = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "fake")
open(os.path.join(d, role + ".prompt"), "wb").write(sys.stdin.buffer.read())
json.dump({"argv": sys.argv[1:], "env": dict(os.environ)}, open(os.path.join(d, role + ".argv.json"), "w"))
def get(ext, default):
    p = os.path.join(d, role + ext)
    return open(p).read() if os.path.exists(p) else default
if os.path.exists(os.path.join(d, role + ".sh")):
    subprocess.run(["/bin/sh", os.path.join(d, role + ".sh"), wt], check=True)
code = int(get(".exit", "0"))
default = "STATUS: completed" if role == "engineer" else "VERDICT: PASS"
print(json.dumps({"type": "result", "is_error": get(".error", "") == "1", "result": get(".txt", default),
                  "num_turns": 1}))
sys.exit(code)
'''
REPORT_LINE = {"pass": "VERDICT: PASS", "findings": "VERDICT: FINDINGS", "inconclusive": "VERDICT: INCONCLUSIVE"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="forgev2-test-")
        os.chmod(self.tmp, 0o700)
        self.fake = os.path.join(self.tmp, "fake")
        os.makedirs(self.fake)
        with open(os.path.join(self.tmp, "fake-claude"), "w") as f:
            f.write(FAKE_CLAUDE)
        os.chmod(os.path.join(self.tmp, "fake-claude"), 0o755)
        self.env = dict(os.environ, HOME=self.tmp, FORGE_STATE_DIR=os.path.join(self.tmp, "state"),
                        FORGE_CLAUDE=os.path.join(self.tmp, "fake-claude"), FAKE_DIR=self.fake,
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
        return self.run_bin("forge-start", "--wo", "WO-1", "--repo", repo,
                            "--host", socket.gethostname(), "--root", self.root,
                            "--worktrees", os.path.join(self.tmp, "src", "worktrees"), *extra, env=env)

    def started(self):
        r = self.start("--known-commit", self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        info = json.loads(r.stdout)
        self.wt, self.ledger, self.scratch = info["worktree"], info["ledger"], info["scratch"]
        self.records = info["records"]
        return info

    def guard(self, tool, tool_input, cwd=None):
        ev = {"session_id": SESSION, "tool_name": tool, "tool_input": tool_input, "hook_event_name": "PreToolUse",
              "cwd": cwd or self.root}
        r = subprocess.run([sys.executable, "-I", GUARD], input=json.dumps(ev), env=self.env,
                           capture_output=True, text=True)
        self.assertIn(r.returncode, (0, 2), r.stderr)
        if r.returncode == 2:
            return "deny"
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        return out.get("hookSpecificOutput", {}).get("permissionDecision", "allow")

    def fake_report(self, role, text=None, exit_code=None, script=None):
        for ext, val in ((".txt", text), (".exit", exit_code), (".sh", script)):
            p = os.path.join(self.fake, role + ext)
            if val is None:
                if os.path.exists(p):
                    os.remove(p)
            else:
                with open(p, "w") as f:
                    f.write(str(val))

    def dispatch(self, *roles):
        args = []
        for role in roles:
            pf = os.path.join(self.tmp, f"prompt-{role}.md")
            with open(pf, "w") as f:
                f.write(f"Brief for {role}\n")
            args.append(f"{role}={pf}")
        return self.run_bin("forge-dispatch", *args)

    def spawn(self, role, report=None):
        """allow = dispatched and returned; void = dispatched, no usable result; deny = refused."""
        if report is not None or role == "engineer":
            self.fake_report(role, report)
        r = self.dispatch(role)
        if r.returncode == 0:
            return "allow"
        return "void" if "NO RESULT" in r.stdout else "deny"

    def ledger_cmd(self, *args):
        return self.run_bin("forge-ledger", *args)

    def head(self):
        return self.sh("git rev-parse HEAD", cwd=self.wt).stdout.strip()

    def write(self, name, text, mode="a"):
        with open(os.path.join(self.wt, name), mode) as f:
            f.write(text)

    def engineer(self, text=None, name="feature.py", outcome="completed"):
        self.assertEqual(self.spawn("engineer", f"STATUS: {outcome}"), "allow")
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
            self.fake_report(role, REPORT_LINE[results.get(role, "pass")])
        r = self.dispatch(*F.REVIEWERS)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for role in F.REVIEWERS:
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
        self.assertFalse(os.path.realpath(self.records).startswith(os.path.realpath(self.wt) + os.sep))
        self.assertEqual(os.listdir(os.path.join(self.wt, ".forge")), [])
        self.assertFalse(os.path.realpath(self.scratch).startswith(os.path.realpath(self.env["FORGE_STATE_DIR"])))
        self.assertEqual(os.stat(self.env["FORGE_STATE_DIR"]).st_mode & 0o777, 0o700)
        for top, dirs, _ in os.walk(self.env["FORGE_STATE_DIR"]):
            for x in dirs:
                self.assertEqual(os.stat(os.path.join(top, x)).st_mode & 0o777, 0o700, os.path.join(top, x))

    def test_state_directory_readable_by_others_refused(self):
        os.makedirs(self.env["FORGE_STATE_DIR"], mode=0o700)
        os.chmod(self.env["FORGE_STATE_DIR"], 0o755)
        r = self.start()
        self.assertEqual(r.returncode, 1)
        self.assertIn("must be owned by this account with mode 0700", r.stderr)
        self.assertEqual(self.sh("git branch --list 'forge/*'", cwd=self.root).stdout.strip(), "")

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

    def test_missing_explicit_host_or_worktree_refused_before_git_change(self):
        for fields in (("--root", self.root, "--worktrees", os.path.join(self.tmp, "src", "worktrees")),
                       ("--host", socket.gethostname(), "--root", self.root)):
            r = self.run_bin("forge-start", "--wo", "WO-1", "--repo", OWNER_REPO, *fields)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("required", r.stderr)
        self.assertEqual(self.sh("git branch --list 'forge/*'", cwd=self.root).stdout.strip(), "")

    def test_wrong_execution_host_blocks_before_changes(self):
        r = self.start("--host", "a-different-build-host.invalid")
        self.assertEqual(r.returncode, 1)
        self.assertIn("remote execution is not configured", r.stderr)
        self.assertIn("remote execution is not configured", self.start("--host", "203.0.113.111").stderr)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "src", "worktrees")))

    def test_target_path_boundary(self):
        canonical_worktrees = os.path.join(self.tmp, "src", "worktrees")
        non_sibling = os.path.join(self.tmp, "elsewhere", "worktrees")
        self.assertIn("distinct siblings", self.start("--worktrees", non_sibling).stderr)
        self.assertIn("distinct siblings", self.start("--worktrees", self.root).stderr)
        self.assertIn("canonical path", self.start("--root", self.root + "/../calc").stderr)
        os.symlink(self.root, os.path.join(self.tmp, "alias"))
        self.assertIn("canonical path", self.start("--root", os.path.join(self.tmp, "alias")).stderr)
        # An explicit protected root cannot be disguised by choosing a child as the checkout.
        from unittest.mock import patch
        with patch.object(F, "PROTECTED_INSTALLS", (os.path.join(self.tmp, "src"),)):
            with self.assertRaisesRegex(F.ForgeError, "protected Foundry/ForgeV2 installation"):
                F.validate_project_target(socket.gethostname(), self.root, canonical_worktrees)
        self.assertEqual(self.sh("git branch --list 'forge/*'", cwd=self.root).stdout.strip(), "")

    def test_missing_git_identity_refused_before_any_change(self):
        env = {k: v for k, v in self.env.items() if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
        with open(os.path.join(self.tmp, ".gitconfig"), "w") as f:
            f.write("[user]\n\tuseConfigOnly = true\n")
        r = self.start(env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no Git author identity", r.stderr)
        self.assertEqual(self.sh("git branch --list 'forge/*'", cwd=self.root).stdout.strip(), "")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "src", "worktrees")))
        with open(os.path.join(self.tmp, ".gitconfig"), "a") as f:
            f.write("\tname = t\n\temail = t@invalid.example\n")
        self.assertEqual(self.start(env=env).returncode, 0)

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
        r = self.start("--root", os.path.join(self.root, "sub"),
                       "--worktrees", os.path.join(self.root, "worktrees"))
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

    def test_in_process_subagents_refused_while_open(self):
        self.started()
        for st in ("general-purpose", "forgev2:engineer", "forgev2:auditor"):
            self.assertEqual(self.guard("Agent", {"subagent_type": st, "prompt": "x"}), "deny", st)
            self.assertEqual(self.guard("Task", {"subagent_type": st, "prompt": "x"}), "deny", st)
        self.assertEqual(self.guard("SendMessage", {"to": "a1", "message": "continue"}), "deny")
        self.assertEqual(load(self.ledger)["counts"]["engineer"], 0)

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
        self.spawn("tester", "VERDICT: PASS")
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
    """The PL's own tool calls while a Work Order is bound."""
    def setUp(self):
        super().setUp()
        self.started()

    def test_pl_git_writes_go_through_forge_tools(self):
        for cmd in ("git commit -am x", f"git -C {self.wt} push origin HEAD", "git push --force origin x",
                    "git commit --no-verify -m x", "sh -c 'git commit -m x'", "git remote -v set-url origin x",
                    "git -c core.hooksPath=/tmp commit -m x", "GIT_DIR=/x git update-ref refs/heads/x HEAD"):
            self.assertEqual(self.guard("Bash", {"command": cmd}), "deny", cmd)
        for cmd in ("forge-commit -m 'fix git push bug'", "forge-ledger next", "git log --oneline -3",
                    f"git -C {self.wt} status", f"git -C {self.wt} diff", "forge-dispatch engineer=/x/p.md"):
            self.assertEqual(self.guard("Bash", {"command": cmd}), "allow", cmd)

    def test_ledger_and_dispatch_outputs_not_editable_by_pl(self):
        disp = os.path.join(os.path.dirname(self.ledger), "dispatch", "0-engineer.json")
        for p in (self.ledger, disp):
            self.assertEqual(self.guard("Write", {"file_path": p, "content": "{}"}), "deny", p)
        self.assertEqual(self.guard("Bash", {"command": f"sed -i s/4/9/ {self.ledger}"}), "deny")
        self.assertEqual(self.guard("Write", {"file_path": os.path.join(self.records, "REPORT.md"),
                                              "content": "x"}), "allow")

    def test_pl_does_not_write_the_shared_area(self):
        for p in (os.path.join(self.wt, "calc.py"), os.path.join(self.wt, ".forge", "WO-1", "REPORT.md"),
                  os.path.join(self.scratch, "x")):
            self.assertEqual(self.guard("Write", {"file_path": p, "content": "x"}), "deny", p)
            self.assertEqual(self.guard("Edit", {"file_path": p}), "deny", p)
        self.assertEqual(self.guard("Read", {"file_path": os.path.join(self.wt, "calc.py")}), "allow")

    def test_pl_file_tools_cannot_modify_engine_or_foundry(self):
        for p in ("/srv/forgev2/plugin/README.md", "/srv/foundry/README.md",
                  os.path.join(PLUGIN, "roles", "engineer.md")):
            self.assertEqual(self.guard("Write", {"file_path": p, "content": "x"}), "deny", p)
            self.assertEqual(self.guard("Edit", {"file_path": p}), "deny", p)

    def test_pl_does_not_follow_links_planted_in_the_worktree(self):
        secret = os.path.join(self.tmp, "pl-secret")
        with open(secret, "w") as f:
            f.write("x")
        os.symlink(secret, os.path.join(self.wt, "notes.md"))
        self.assertEqual(self.guard("Read", {"file_path": os.path.join(self.wt, "notes.md")}), "deny")
        self.assertEqual(self.guard("Read", {"file_path": secret}), "allow")  # outside the shared area

    def test_specialists_only_via_forge_dispatch(self):
        for cmd in ("claude -p 'fix the bug'", "/usr/local/bin/claude -p x", "cd /x && claude --tools Bash -p y",
                    "bwrap --bind / / sh", "echo x | sudo -u forgev2-agent id"):
            self.assertEqual(self.guard("Bash", {"command": cmd}), "deny", cmd)

    def test_subagents_allowed_again_after_close(self):
        self.engineer(outcome="blocked")
        self.assertEqual(self.ledger_cmd("close", "BLOCKED").returncode, 0)
        self.assertEqual(self.guard("Agent", {"subagent_type": "general-purpose", "prompt": "x"}), "allow")

    def test_pl_unrestricted_without_work_order(self):
        os.remove(F.session_pointer(SESSION))
        self.assertEqual(self.guard("Bash", {"command": "git commit -m x"}), "allow")
        self.assertEqual(self.guard("Agent", {"subagent_type": "general-purpose", "prompt": "x"}), "allow")

    def test_malformed_input_blocks(self):
        r = subprocess.run([sys.executable, "-I", GUARD], input="not json", env=self.env,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


class Dispatch(Base):
    def setUp(self):
        super().setUp()
        self.started()

    def test_dispatch_runs_specialist_with_prompt_and_keeps_output(self):
        self.fake_report("engineer", "did it\nSTATUS: completed")
        r = self.dispatch("engineer")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("did it", r.stdout)
        with open(os.path.join(self.fake, "engineer.prompt")) as f:
            self.assertEqual(f.read(), "Brief for engineer\n")
        d = load(self.ledger)
        ev = [e for e in d["events"] if e["type"] == "dispatched"][-1]
        self.assertEqual((ev["role"], ev["reported"], ev["exit"]), ("engineer", "completed", 0))
        out = load(os.path.join(os.path.dirname(self.ledger), ev["output"]))
        self.assertEqual(out["prompt"], "Brief for engineer\n")
        self.assertIn("did it", out["result"])
        spawn = [e for e in d["events"] if e["type"] == "spawn"][-1]
        self.assertEqual(spawn["via"], "forge-dispatch")
        self.assertIn("claude", spawn)  # a non-standard Claude binary is visible in the record
        argv = load(os.path.join(self.fake, "engineer.argv.json"))["argv"]
        settings = json.loads(argv[argv.index("--settings") + 1])
        self.assertTrue(settings["sandbox"]["enabled"] and settings["sandbox"]["failIfUnavailable"])

    def test_failed_run_is_recorded_void(self):
        self.fake_report("engineer", "STATUS: completed", exit_code=3)
        r = self.dispatch("engineer")
        self.assertEqual(r.returncode, 1)
        self.assertIn("NO RESULT", r.stdout)
        d = load(self.ledger)
        self.assertEqual([e["outcome"] for e in d["events"] if e["type"] == "result"], ["void"])
        self.fake_report("engineer", "STATUS: completed")
        self.assertEqual(self.dispatch("engineer").returncode, 0)  # the void freed the slot
        self.assertEqual(load(self.ledger)["counts"]["engineer"], 2)

    def test_error_result_and_garbage_output_are_void(self):
        with open(os.path.join(self.fake, "engineer.error"), "w") as f:
            f.write("1")
        self.assertEqual(self.spawn("engineer", "STATUS: completed"), "void")
        os.remove(os.path.join(self.fake, "engineer.error"))
        self.fake_report("engineer", "x", script="echo not-json; exit 0")
        r = self.dispatch("engineer")
        self.assertIn("NO RESULT", r.stdout)

    def test_pass_and_completed_need_the_specialists_own_report(self):
        self.assertEqual(self.spawn("engineer", "STATUS: blocked - cannot reach the database"), "allow")
        r = self.ledger_cmd("record", "engineer", "completed")
        self.assertEqual(r.returncode, 1)
        self.assertIn("reported blocked", r.stderr)
        self.assertEqual(self.ledger_cmd("record", "engineer", "blocked").returncode, 0)

    def test_reviewer_pass_needs_reported_pass(self):
        self.build()
        self.fake_report("auditor", "VERDICT: FINDINGS\nFINDING x blocking: ...")
        self.fake_report("tester", "I think it is fine")              # no status line
        self.fake_report("devsecops", "VERDICT: PASS\n...\nVERDICT: FINDINGS")  # ambiguous
        self.assertEqual(self.dispatch(*F.REVIEWERS).returncode, 0)
        for role in F.REVIEWERS:
            self.assertEqual(self.ledger_cmd("record", role, "pass").returncode, 1, role)
        self.assertEqual(self.ledger_cmd("record", "auditor", "findings", "--finding", "x:blocking").returncode, 0)
        self.assertEqual(self.ledger_cmd("record", "tester", "inconclusive").returncode, 0)

    def test_result_cannot_be_recorded_before_dispatch_returns(self):
        with F.locked_ledger(self.ledger) as d:
            F.spawn(d, "engineer")         # counted, still running
        r = self.ledger_cmd("record", "engineer", "completed")
        self.assertEqual(r.returncode, 1)
        self.assertIn("has not returned", r.stderr)
        self.assertEqual(self.ledger_cmd("record", "engineer", "void").returncode, 0)

    def test_multiple_dispatch_is_all_or_nothing(self):
        self.build()
        self.assertEqual(self.review({"tester": "inconclusive"})["decision"], "REVIEW")
        before = load(self.ledger)["counts"]
        r = self.dispatch("tester", "auditor")     # auditor is not needed again
        self.assertEqual(r.returncode, 1)
        self.assertEqual(load(self.ledger)["counts"], before)
        self.assertIn("never alongside", self.dispatch("tester", "engineer").stderr)
        self.assertIn("given twice", self.dispatch("tester", "tester").stderr)

    def test_reviewer_that_changes_the_worktree_is_void(self):
        self.build()
        self.fake_report("tester", "VERDICT: PASS", script='echo "x = 2" >> "$1/feature.py"')
        r = self.dispatch(*F.REVIEWERS)
        self.assertEqual(r.returncode, 1)
        self.assertIn("no longer matches the candidate", r.stdout)
        results = [e for e in load(self.ledger)["events"] if e["type"] == "result" and e["role"] != "engineer"]
        self.assertEqual({e["outcome"] for e in results}, {"void"})

    def test_bad_prompt_or_role_is_refused_uncounted(self):
        empty = os.path.join(self.tmp, "empty.md")
        open(empty, "w").close()
        for args in ([f"engineer={empty}"], [f"engineer={self.tmp}/missing.md"], [f"intruder={empty}"],
                     ["engineer"], []):
            r = self.run_bin("forge-dispatch", *args)
            self.assertEqual(r.returncode, 1, args)
            self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(load(self.ledger)["counts"]["engineer"], 0)

    def test_dispatch_rechecks_repository_identity(self):
        self.sh("git remote set-url origin https://github.com/evil/calc.git", cwd=self.root)
        self.assertEqual(self.spawn("engineer"), "deny")
        self.assertEqual(load(self.ledger)["counts"]["engineer"], 0)


class Sandbox(Base):
    """The command and settings every specialist run gets (the real sandbox: tests/host/sandbox-boundary.sh)."""
    def setUp(self):
        super().setUp()
        self.started()
        self.d = load(self.ledger)
        self.home = tempfile.mkdtemp(prefix="forgev2-engineer-")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        super().tearDown()

    def build(self, role):
        argv, env, cwd = F.specialist_command(self.d, role, self.home)
        self.assertEqual(cwd, self.scratch)  # never start inside the repository
        return argv, env, json.loads(argv[argv.index("--settings") + 1])

    def test_sandbox_is_mandatory_and_offline(self):
        for role in F.ROLES:
            argv, env, st = self.build(role)
            sb = st["sandbox"]
            self.assertEqual((sb["enabled"], sb["failIfUnavailable"], sb["allowUnsandboxedCommands"]),
                             (True, True, False), role)
            self.assertEqual(sb["excludedCommands"], [])
            self.assertFalse(sb["enableWeakerNestedSandbox"] or sb["allowNestedUserNamespaces"])
            self.assertEqual(sb["network"], {"allowedDomains": [], "strictAllowlist": True})
            self.assertTrue(st["disableAllHooks"])
            for flag in ("--safe-mode", "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"):
                self.assertIn(flag, argv)
            self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
            self.assertEqual(argv[argv.index("--permission-mode") + 1], "dontAsk")
            self.assertNotIn("--dangerously-skip-permissions", argv)
            self.assertNotIn("--allowedTools", argv)  # nothing allowed beyond the scoped rules

    def test_private_paths_unreadable_by_commands_and_file_tools(self):
        for role in F.ROLES:
            _, _, st = self.build(role)
            deny_read = st["sandbox"]["filesystem"]["denyRead"]
            for p in (os.path.expanduser("~root") if os.geteuid() == 0 else os.path.expanduser("~"),
                      self.env["FORGE_STATE_DIR"], F.claude_config_dir()):
                p = os.path.realpath(p)
                self.assertIn(p, deny_read, role)
                self.assertIn(f"Read(/{p}/**)", st["permissions"]["deny"], role)

    def test_writes_limited_by_role(self):
        _, _, eng = self.build("engineer")
        self.assertEqual(eng["sandbox"]["filesystem"]["allowWrite"], [self.wt, self.scratch, self.home])
        self.assertEqual(eng["sandbox"]["filesystem"]["denyWrite"],
                         [os.path.join(self.wt, ".git"), os.path.join(self.wt, ".forge"),
                          self.d["git_dir"], self.d["common_dir"]])
        self.assertIn(f"Edit(/{self.d['common_dir']}/**)", eng["permissions"]["deny"])
        self.assertIn(f"Edit(/{self.wt}/**)", eng["permissions"]["allow"])
        for p in (".git", ".forge"):
            self.assertIn(f"Edit(/{os.path.join(self.wt, p)}/**)", eng["permissions"]["deny"])
        for role in F.REVIEWERS:
            _, _, rv = self.build(role)
            self.assertNotIn(self.wt, rv["sandbox"]["filesystem"]["allowWrite"], role)
            self.assertFalse([a for a in rv["permissions"]["allow"] if self.wt in a], role)
        for role in F.ROLES:
            _, _, st = self.build(role)
            self.assertFalse({"Edit", "Write"} & set(st["permissions"]["allow"]), role)  # never unscoped

    def test_environment_is_fixed_and_fresh(self):
        os.environ["GH_TOKEN"] = "x"
        try:
            argv, env, _ = self.build("tester")
        finally:
            os.environ.pop("GH_TOKEN")
        self.assertEqual(env["HOME"], self.home)
        self.assertEqual(env["PATH"], "/usr/local/bin:/usr/bin:/bin")
        self.assertFalse({"GH_TOKEN", "SSH_AUTH_SOCK", "ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN",
                          "FORGE_STATE_DIR", "CLAUDE_CODE_SESSION_ID"} & set(env))
        self.assertEqual(argv[argv.index("--tools") + 1], "Read,Grep,Glob,Bash,Write")

    def test_project_inside_private_area_refused(self):
        self.assertRaises(F.ForgeError, F.specialist_command, self.d, "engineer",
                          os.path.join(self.env["FORGE_STATE_DIR"], "home"))
        inside = os.path.join(self.env["FORGE_STATE_DIR"], "proj", "calc")
        self.sh(f"git clone -q {self.root} {inside} && git -C {inside} remote set-url origin "
                f"https://github.com/{OWNER_REPO}.git")
        r = self.run_bin("forge-start", "--wo", "WO-2", "--repo", OWNER_REPO,
                         "--host", socket.gethostname(), "--root", inside,
                         "--worktrees", os.path.join(os.path.dirname(inside), "worktrees"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("specialists cannot read", r.stderr)

    def test_missing_sandbox_dependency_refused(self):
        deps = F.SANDBOX_DEPS
        try:
            F.SANDBOX_DEPS = ("/nonexistent/bwrap",)
            self.assertRaisesRegex(F.ForgeError, "only inside the sandbox", F.check_runtime)
        finally:
            F.SANDBOX_DEPS = deps

    def test_roles_parse_with_limited_tools(self):
        for role in F.ROLES:
            tools, body = F.load_role(role)
            self.assertTrue(set(tools) <= F.SPECIALIST_TOOLS)
            self.assertEqual("Edit" in tools, role == "engineer")
            self.assertIn("ForgeV2", body)


class Records(Base):
    def setUp(self):
        super().setUp()
        self.need_gitleaks()
        self.deliver()

    def report(self, text="# WO-1 - DELIVERED\n"):
        with open(os.path.join(self.records, "REPORT.md"), "w") as f:
            f.write(text)

    def test_records_published_from_pl_directory(self):
        self.report()
        with open(os.path.join(self.records, "prompts", "r1-auditor.md"), "w") as f:
            f.write("assess independently\n")
        r = self.commit("WO-1: delivery record")
        self.assertEqual(r.returncode, 0, r.stderr)
        files = sorted(self.sh("git show --name-only --format= HEAD", cwd=self.wt).stdout.split())
        self.assertIn(".forge/WO-1/ledger.json", files)
        self.assertIn(".forge/WO-1/REPORT.md", files)
        self.assertIn(".forge/WO-1/prompts/r1-auditor.md", files)
        self.assertEqual(len([f for f in files if f.startswith(".forge/WO-1/dispatch/")]), 4)
        self.assertTrue(F.record_paths_ok(load(self.ledger), files))
        published = load(os.path.join(self.wt, ".forge", "WO-1", "ledger.json"))
        self.assertEqual(published["outcome"], "DELIVERED")

    def test_report_required(self):
        self.assertIn("REPORT.md first", self.commit("WO-1: delivery record").stderr)

    def test_unexpected_record_file_refused(self):
        self.report()
        with open(os.path.join(self.records, "run.sh"), "w") as f:
            f.write("x")
        self.assertIn("unexpected file", self.commit("WO-1: delivery record").stderr)

    def test_planted_symlink_in_record_path_is_not_followed(self):
        """A worktree writer can rename .forge and plant a link to a PL file (the sandbox also forbids it)."""
        self.report()
        target = os.path.join(self.tmp, "pl-file")
        with open(target, "w") as f:
            f.write("precious\n")
        forge = os.path.join(self.wt, ".forge")
        os.rename(forge, forge + "-moved")
        os.makedirs(forge)
        os.symlink(self.tmp, os.path.join(forge, "WO-1"))
        r = self.commit("WO-1: delivery record")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("Traceback", r.stderr)
        with open(target) as f:
            self.assertEqual(f.read(), "precious\n")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "ledger.json")))

    def test_publish_never_writes_through_a_link(self):
        """Second layer, below forge-commit's status check: publish_records itself refuses links."""
        self.report()
        forge = os.path.join(self.wt, ".forge")
        victim = os.path.join(self.tmp, "victim")
        os.makedirs(victim, mode=0o700)
        for planted in (os.path.join(forge, "WO-1"), forge):
            if os.path.islink(forge):
                os.remove(forge)
            elif os.path.isdir(forge):
                shutil.rmtree(forge)
            if planted != forge:
                os.makedirs(forge)
            os.symlink(victim, planted)
            self.assertRaisesRegex(F.ForgeError, "replaced in the worktree",
                                   F.publish_records, load(self.ledger), self.ledger)
            self.assertEqual(os.listdir(victim), [], planted)

    def test_record_directory_owned_by_another_account_refused(self):
        self.report()
        forge = os.path.join(self.wt, ".forge")
        if os.geteuid() != 0:
            self.skipTest("needs root to create a foreign-owned directory")
        os.rename(forge, forge + "-moved")
        os.makedirs(os.path.join(forge, "WO-1"))
        os.chown(forge, 65534, 65534)
        r = self.commit("WO-1: delivery record")
        self.assertEqual(r.returncode, 1)
        self.assertIn("replaced in the worktree", r.stderr)


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
    def commit_records(self):
        with open(os.path.join(self.records, "REPORT.md"), "w") as f:
            f.write("# WO-1 - DELIVERED\n")
        r = self.commit("WO-1: delivery record")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_close_records_push_reaches_transport(self):
        self.deliver()
        self.assertFalse(os.path.exists(os.path.join(self.wt, ".forge", "WO-1", "ledger.json")))
        self.commit_records()
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
        os.makedirs(os.path.join(self.wt, ".forge", "WO-1"))
        self.write(".forge/WO-1/payload.sh", "rm -rf /\n")
        self.assertIn("unreviewed", self.commit().stderr)

    def test_push_refuses_unreviewed_commit_after_delivery(self):
        """Audit finding 2."""
        self.deliver()
        self.commit_records()
        self.write("calc.py", "import os; os.system('id')\n")
        self.sh("git commit -qam sneaky", cwd=self.wt)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unreviewed", r.stderr)

    def test_push_refuses_rename_that_hides_a_deletion(self):
        """Release audit: rename detection must not hide a deleted reviewed file."""
        self.deliver()
        self.commit_records()
        self.sh("mkdir -p .forge/WO-1/prompts && git mv calc.py .forge/WO-1/prompts/moved.md", cwd=self.wt)
        self.sh("git commit -qm hide", cwd=self.wt)
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
        self.commit_records()
        self.write(".forge/WO-1/REPORT.md", f'token {token()}\n')
        self.sh("git commit -qam report", cwd=self.wt)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("gitleaks", r.stderr)

    def test_push_rechecks_identity(self):
        self.deliver()
        self.commit_records()
        self.sh(f"git remote set-url --push origin {self.tmp}/attacker.git", cwd=self.root)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("push URL", r.stderr)

    def test_push_refuses_non_forge_branch(self):
        self.deliver()
        self.commit_records()
        d = load(self.ledger)
        d["branch"] = "main"
        save(self.ledger, d)
        r = self.run_bin("forge-push")
        self.assertEqual(r.returncode, 1)
        self.assertIn("pushes only forge/<WO>", r.stderr)


if __name__ == "__main__":
    unittest.main()
