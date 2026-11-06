"""Behavior tests using real Git repositories and local stub CLIs, no models."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "cross-model-review/scripts/review.py"
REPORT = """Outcome: SUGGESTIONS

Summary: Reviewed the complete supplied change.

Observations:
- [P1] calc.py:2 — A deliberate fixture defect
  Rationale: Negative input is mishandled.
  Evidence: Read calc.py.
  Suggested correction: Preserve negative inputs.

Tests run: none
Unknowns: none
"""
FAKE = '''import json,os,sys,time,subprocess
from pathlib import Path
args=sys.argv[1:]
tool=Path(sys.argv[0]).name
if os.getenv("ALL_CALL_LOG"):
 Path(os.environ["ALL_CALL_LOG"]).open("a").write(json.dumps([tool,*args])+"\\n")
if os.getenv("FAIL_ANY_CLI"): sys.exit(91)
if args[:2]==["config","status"]:
 print("  plane=defaults source_class=system_file state="+("active" if os.getenv("BAD_POLICY") else "absent")); sys.exit(0)
if args[:2]==["plugins","list"]:
 print(json.dumps({"plugins": ["fixture"] if os.getenv("BAD_PLUGINS") else []})); sys.exit(0)
if "mcp" in args and "list" in args:
 disabled=any("mcp_servers=" in x for x in args)
 print(json.dumps([{"name":"server.with-dots","enabled": bool(os.getenv("BAD_MCP")) or not disabled}])); sys.exit(0)
if "features" in args and "list" in args:
 gate=os.getenv("PROBE_GATE")
 if gate:
  Path(gate+".ready").write_text("Configuration probe reached")
  while not Path(gate).exists(): time.sleep(0.01)
 for x in ("apps","plugins","hooks","multi_agent","computer_use","browser_use","in_app_browser","image_generation"):
  print(x,"stable", "true" if os.getenv("BAD_FEATURE") else "false")
 sys.exit(0)
if "--provider" in args and args[args.index("--provider")+1]=="echo":
 print("echo: configuration probe"); sys.exit(0)
Path(os.environ["CALL_LOG"]).open("a").write(json.dumps([tool,*args])+"\\n")
print("original diagnostic",file=sys.stderr,flush=True)
mode=os.getenv("FAKE_MODE","valid")
if mode=="slow": time.sleep(30)
if mode=="orphan":
 subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
report=os.environ["FAKE_REPORT"]
if mode=="malformed": report="I approve everything."
if mode=="empty": report=""
if tool=="codex":
 Path(args[args.index("--output-last-message")+1]).write_text(report)
 print("native stdout separate from final report")
else: sys.stdout.write(report)
sys.exit(7 if mode=="exit" else 0)
'''


class ReviewRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="review-runner-", dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.repo = self.home / "repo with spaces"
        self.repo.mkdir()
        self.bin = self.home / "bin"
        self.bin.mkdir()
        for tool in ("codex", "claude", "muse"):
            file = self.bin / tool
            file.write_text(f"#!{sys.executable}\n" + FAKE)
            file.chmod(0o700)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
                        GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                        XDG_CONFIG_HOME=str(self.home / "config"),
                        CALL_LOG=str(self.home / "calls.jsonl"), FAKE_REPORT=REPORT,
                        PYTHONDONTWRITEBYTECODE="1")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Review Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / ".gitignore").write_text("artifacts/\nignored.txt\n")
        (self.repo / "calc.py").write_text("def f(n):\n    return n\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture baseline")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.git("checkout", "-qb", "feature")
        self.review = self.home / "review evidence"
        self.brief = self.home / "brief.md"
        self.brief.write_text("Preserve every integer input, including negative values.\n")
        self.checks = self.home / "checks.md"
        self.checks.write_text("No execution in this synthetic case; static inspection only.\n")
        self.auth = self.home / "scope.md"
        self.auth.write_text("Synthetic fixture; caller permits review of the complete change and relevant files read-only.\n")
        self.dispositions = self.home / "dispositions.md"
        self.dispositions.write_text("CMR-001: accepted; corrected negative input handling. Prior failures retained.\n")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], env=self.env,
                              check=True, capture_output=True).stdout

    def command(self, *extra):
        return [sys.executable, "-B", str(RUNNER), "--repo", str(self.repo),
                "--brief", str(self.brief), "--checks", str(self.checks),
                "--authorization", str(self.auth), "--author-model", "fixture-author-v1",
                "--tool", "claude", "--review-dir", str(self.review), *extra]

    def call(self, *extra, env=None):
        result = subprocess.run(self.command(*extra), env={**self.env, **(env or {})},
                                capture_output=True, text=True, timeout=15)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def calls(self):
        file = self.home / "calls.jsonl"
        return [json.loads(x) for x in file.read_text().splitlines()] if file.exists() else []

    def state(self):
        return json.loads((self.review / "review-state.json").read_text())

    def evidence(self):
        return {p.name: p.read_bytes() for p in self.review.iterdir() if p.is_file()}

    def continuation(self, name="decision.json", **changes):
        value = {"version": 1, "after_round": len(self.state()["exchanges"]),
                 "history_sha256": hashlib.sha256((self.review / "review-state.json").read_bytes()).hexdigest(),
                 "allowance": 1, "brief_sha256": hashlib.sha256(self.brief.read_bytes()).hexdigest(),
                 "owner": "Fixture coordinator", "authorization_source": "Synthetic assignment",
                 "basis": "distinct_finding", "rationale": "New boundary case; retain CMR-001 and inspect its fix."}
        value.update(changes)
        file = self.home / name
        file.write_text(json.dumps(value, indent=2) + "\n")
        return file

    def continuation_command(self, file, *extra):
        return [sys.executable, "-B", str(RUNNER), "--review-dir", str(self.review),
                "--repo", str(self.repo), "--brief", str(self.brief), "--continue-with", str(file), *extra]

    def continue_call(self, file, *extra, env=None):
        result = subprocess.run(self.continuation_command(file, *extra),
                                env={**self.env, **(env or {})}, capture_output=True, text=True, timeout=15)
        self.assertNotIn("Traceback", result.stderr, result.stderr)
        return result.returncode, json.loads(result.stdout) if result.stdout else {"error": result.stderr}

    def assert_allowance(self, result, used, limit):
        self.assertEqual(result["allowance_used"], used)
        self.assertEqual(result["allowance_limit"], limit)
        self.assertEqual(result["allowance_remaining"], limit - used)
        self.assertEqual(result["reassessment_required"], used == limit)
        self.assertEqual(result["history_sha256"],
                         hashlib.sha256((self.review / "review-state.json").read_bytes()).hexdigest())

    def test_complete_capture_and_original_reports(self):
        (self.repo / "calc.py").write_text("def f(n):\n    return abs(n)  # staged bug\n")
        self.git("add", "calc.py")
        (self.repo / "calc.py").write_text("def f(n):\n    return n  # working repair\n")
        unusual = 'folder/name "quoted"\nand newline.py'
        (self.repo / unusual).parent.mkdir()
        (self.repo / unusual).write_text("# full untracked source\n")
        self.git("config", "status.showUntrackedFiles", "no")
        code, result = self.call()
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        for text in ("staged bug", "working repair", "full untracked source", "Working tree against index", "Staged change against HEAD"):
            self.assertIn(text, packet)
        self.assertEqual(Path(result["report"]).read_text(), REPORT)
        self.assertEqual(Path(result["stderr"]).read_text(), "original diagnostic\n")
        self.assertEqual(result["outcome"], "SUGGESTIONS")
        self.assertEqual(self.state()["base"], self.base)

    def test_all_adapters_and_model_defaults(self):
        defaults = {"claude":"claude-opus-5-5", "codex":"gpt-6-astra", "muse":"muse-wonder-full-1.0"}
        for tool, model in defaults.items():
            code, result = self.call("--tool", tool, "--dispositions", str(self.dispositions))
            self.assertEqual(code, 0, result)
            self.assertEqual(result["model"], model)
            self.assertEqual(result["effort"], "max")
            self.assertEqual(Path(result["report"]).read_text(), REPORT)
        self.assertEqual(len(self.calls()), 3)
        claude = self.calls()[0]
        for flag in ("--safe-mode", "--restricted", "--strict-mcp-config", "--no-session-persistence"):
            self.assertIn(flag, claude)
        self.assertEqual(claude[claude.index("--tools") + 1], "Read,Glob,Grep")
        self.assertEqual(claude[claude.index("--allowedTools") + 1], "Read,Glob,Grep")
        self.assertEqual(claude[claude.index("--permission-mode") + 1], "dontAsk")
        self.assertEqual(json.loads(claude[claude.index("--mcp-config") + 1]), {"mcpServers":{}})
        codex = self.calls()[1]
        self.assertIn("--ephemeral", codex)
        self.assertIn("read-only", codex)
        self.assertIn('mcp_servers={"server.with-dots"={enabled=false}}', codex)
        muse = self.calls()[2]
        self.assertIn("--disable-write", muse)
        self.assertIn("--disable-shell", muse)
        self.assertIn('run.toolset=["read_file"]', muse)

    def test_committed_change_cancelled_in_index_and_empty_commit_are_preserved(self):
        original = (self.repo / "calc.py").read_text()
        (self.repo / "calc.py").write_text("# committed then staged away\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Committed feature")
        self.git("commit", "--allow-empty", "-qm", "Intentional empty commit")
        (self.repo / "calc.py").write_text(original)
        self.git("add", ".")
        code, result = self.call()
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn("Intentional empty commit", packet)
        self.assertIn("+# committed then staged away", packet)
        self.assertIn("-# committed then staged away", packet)

    def test_unrelated_exclusion_preserves_empty_and_merge_commits(self):
        self.git("commit", "--allow-empty", "-qm", "Intentional empty commit")
        self.git("checkout", "-qb", "topic")
        (self.repo / "public.txt").write_text("Public branch content\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Public branch commit")
        self.git("checkout", "feature")
        self.git("merge", "--no-ff", "-qm", "Merge public history", "topic")
        code, result = self.call("--exclude", "unrelated-private.txt")
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        for subject in ("Intentional empty commit", "Public branch commit", "Merge public history"):
            self.assertIn(subject, packet)

    def test_signed_history_ignores_signature_display_and_preserves_exclusions(self):
        keygen = shutil.which("ssh-keygen")
        if not keygen:
            self.skipTest("Signed-history fixture requires ssh-keygen")
        version = self.git("--version").decode().split()[2]
        if tuple(map(int, version.split(".")[:2])) < (2, 34):
            self.skipTest("SSH commit signing requires Git 2.34 or newer")
        probe = subprocess.run([keygen, "-Y", "sign"], input=b"", capture_output=True,
                               env={**self.env, "LC_ALL": "C"}, timeout=5)
        if b"unknown option" in probe.stderr or b"illegal option" in probe.stderr:
            self.skipTest("Installed ssh-keygen does not support SSH signatures")
        key = self.home / "fixture-signing-key"
        subprocess.run([keygen, "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
                       env=self.env, check=True, capture_output=True, timeout=5)
        signers = self.home / "allowed-signers"
        signers.write_text("fixture@example.invalid " + key.with_suffix(".pub").read_text())
        self.git("config", "gpg.format", "ssh")
        self.git("config", "gpg.ssh.program", keygen)
        self.git("config", "user.signingkey", str(key))
        self.git("config", "gpg.ssh.allowedSignersFile", str(signers))
        (self.repo / "private.txt").write_text("PRIVATE_SIGNED_CONTENT\n")
        self.git("add", "private.txt")
        self.git("commit", "-S", "-qm", "PRIVATE_SIGNED_SUBJECT")
        self.git("verify-commit", "HEAD")
        private_commit = self.git("rev-parse", "--short", "HEAD").decode().strip()
        (self.repo / "calc.py").write_text("# Public signed content\n")
        self.git("add", "calc.py")
        self.git("commit", "-S", "-qm", "Public signed change")
        self.git("verify-commit", "HEAD")
        self.git("config", "log.showSignature", "true")
        # Prove this fixture actually adds presentation text to formatted log output.
        shown = self.git("log", "--format=%H", self.base + "..HEAD")
        self.assertIn(b'Good "git" signature', shown)
        before_status = self.git("status", "--porcelain")
        before_index = (self.repo / ".git/index").read_bytes()
        before_config = (self.repo / ".git/config").read_bytes()
        for name, extra in (("complete", ()), ("unrelated", ("--exclude", "absent.txt")),
                            ("private", ("--exclude", "private.txt"))):
            with self.subTest(scope=name):
                self.review = self.home / ("signed-review-" + name)
                code, result = self.call(*extra)
                self.assertEqual(code, 0, result)
                packet = Path(result["packet"]).read_text()
                history = packet.split("## Committed history\n", 1)[1].split("\n## ", 1)[0]
                self.assertIn("Public signed change", history)
                self.assertIn("Public signed content", packet)
                if name == "private":
                    self.assertNotIn("PRIVATE_SIGNED_", packet)
                    self.assertNotIn(private_commit, history)
                else:
                    self.assertIn("PRIVATE_SIGNED_SUBJECT", history)
                    self.assertIn("PRIVATE_SIGNED_CONTENT", packet)
                self.assertEqual((self.repo / ".git/index").read_bytes(), before_index)
                self.assertEqual((self.repo / ".git/config").read_bytes(), before_config)
        self.assertEqual(self.git("status", "--porcelain"), before_status)
        self.assertEqual(len(self.calls()), 3)

    def test_excluded_only_history_and_merges_do_not_leak_metadata(self):
        private = "private[1].txt"
        (self.repo / private).write_text("PRIVATE_LINEAR_CONTENT\n")
        self.git("add", private)
        self.git("commit", "-qm", "PRIVATE_LINEAR_SUBJECT")
        private_commits = [self.git("rev-parse", "--short", "HEAD").decode().strip()]
        self.git("checkout", "-qb", "private-topic")
        (self.repo / private).write_text("PRIVATE_SIDE_CONTENT\n")
        self.git("add", private)
        self.git("commit", "-qm", "PRIVATE_SIDE_SUBJECT")
        private_commits.append(self.git("rev-parse", "--short", "HEAD").decode().strip())
        self.git("checkout", "feature")
        # The public first-parent change must not make a private side merge public.
        (self.repo / "calc.py").write_text("# Public first-parent content\n")
        self.git("add", "calc.py")
        self.git("commit", "-qm", "Public first-parent commit")
        self.git("merge", "--no-ff", "-qm", "PRIVATE_MERGE_SUBJECT", "private-topic")
        private_commits.append(self.git("rev-parse", "--short", "HEAD").decode().strip())
        (self.repo / "public.txt").write_text("Public mixed commit content\n")
        (self.repo / private).write_text("PRIVATE_MIXED_CONTENT\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Public and private mixed commit")
        code, result = self.call("--exclude", private)
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertNotIn("PRIVATE_", packet)
        for commit in private_commits:
            self.assertNotIn(commit, packet)
        self.assertIn("Public first-parent commit", packet)
        self.assertIn("Public and private mixed commit", packet)
        self.assertIn("Public mixed commit content", packet)

    def test_empty_merge_retains_public_side_history_but_not_excluded_only_side(self):
        for name in ("public", "private"):
            self.git("checkout", "-qb", name + "-topic")
            file = self.repo / (name + ".txt")
            file.write_text(name + " temporary branch content\n")
            self.git("add", ".")
            self.git("commit", "-qm", name + " branch addition")
            self.git("rm", name + ".txt")
            self.git("commit", "-qm", name + " branch removal")
            self.git("checkout", "feature")
            self.git("merge", "--no-ff", "-qm", name + " empty merge", name + "-topic")
        code, result = self.call("--exclude", "private.txt")
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        for suffix in ("branch addition", "branch removal", "empty merge"):
            self.assertIn("public " + suffix, packet)
            self.assertNotIn("private " + suffix, packet)

    def test_text_filename_resembling_binary_numstat_is_not_rejected(self):
        file = self.repo / "literal-\t-\tfile.txt"
        file.write_text("text\n")
        self.git("add", ".")
        self.assertEqual(self.call()[0], 0)

    def test_unmerged_index_is_not_an_incomplete_success(self):
        (self.repo / "calc.py").write_text("def f(n):\n    return 1\n")
        self.git("add", ".")
        self.git("commit", "-qm", "feature edit")
        self.git("checkout", "main")
        (self.repo / "calc.py").write_text("def f(n):\n    return 2\n")
        self.git("add", ".")
        self.git("commit", "-qm", "main edit")
        self.git("checkout", "feature")
        merged = subprocess.run(["git", "-C", str(self.repo), "merge", "main"],
                                env=self.env, capture_output=True)
        self.assertNotEqual(merged.returncode, 0)
        code, result = self.call("--base", self.base)
        self.assertEqual(code, 2, result)
        self.assertIn("Unmerged index", result["error"])
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.call("--base", self.base, "--exclude", "calc.py")[0], 0)

    def test_submodule_ignore_setting_cannot_hide_unsupported_content(self):
        self.git("update-index", "--add", "--cacheinfo", f"160000,{self.base},nested")
        self.git("config", "diff.ignoreSubmodules", "all")
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.call("--exclude", "nested")[0], 0)

    def test_hidden_index_flags_refuse_without_mutation_and_allow_explicit_exclusion(self):
        source = self.repo / "calc.py"
        for flag in ("assume-unchanged", "skip-worktree"):
            with self.subTest(flag=flag):
                self.review = self.home / ("review-" + flag)
                self.git("update-index", "--" + flag, "calc.py")
                source.write_text("# HIDDEN_CHANGED_CONTENT\n")
                (self.repo / "public.txt").write_text("Public content remains reviewable\n")
                before_flags = self.git("ls-files", "-v", "-z")
                before_index = (self.repo / ".git/index").read_bytes()
                code, result = self.call()
                self.assertEqual(code, 2, result)
                self.assertIn(flag, result["error"])
                self.assertFalse(self.review.exists())
                self.assertEqual(self.git("ls-files", "-v", "-z"), before_flags)
                self.assertEqual((self.repo / ".git/index").read_bytes(), before_index)
                code, result = self.call("--exclude", "calc.py")
                self.assertEqual(code, 0, result)
                packet = Path(result["packet"]).read_text()
                self.assertNotIn("HIDDEN_CHANGED_CONTENT", packet)
                self.assertIn("Public content remains reviewable", packet)
                self.assertEqual(self.git("ls-files", "-v", "-z"), before_flags)
                self.assertEqual((self.repo / ".git/index").read_bytes(), before_index)
                self.assertEqual(source.read_text(), "# HIDDEN_CHANGED_CONTENT\n")
                self.git("update-index", "--no-" + flag, "calc.py")
                self.git("checkout", "--", "calc.py")
        self.assertEqual(len(self.calls()), 2)

    def test_documented_invocation_does_not_write_to_installed_skill(self):
        skill = self.home / "installed-skill"
        shutil.copytree(RUNNER.parent.parent, skill)
        command = self.command()
        command[2] = str(skill / "scripts/review.py")
        command.remove("-B")
        env = {k:v for k,v in self.env.items() if k != "PYTHONDONTWRITEBYTECODE"}
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(list(skill.rglob("*.pyc")))

    def test_caller_overrides_not_shell_code(self):
        model = 'caller-model-2$(touch NEVER)'
        code, result = self.call("--model", model, "--effort", "high")
        self.assertEqual(code, 0, result)
        self.assertIn(model, self.calls()[0])
        self.assertEqual(result["effort"], "high")
        self.assertFalse((self.repo / "NEVER").exists())

    def test_same_or_unresolved_model_refuses_before_invocation(self):
        for model in ("claude-opus-5-5", "unknown", "opus"):
            code, result = self.call("--author-model", model)
            self.assertEqual(code, 2, result)
        self.assertEqual(self.calls(), [])

    def test_model_identity_whitespace_and_aliases_refuse_without_artifacts(self):
        for option in ("--author-model", "--model"):
            for i, identity in enumerate(("", " \t\n", "unknown ", "\tAuTo\n", " default ",
                                          " LATEST ", " Opus\t", " sonnet ", " haiku ")):
                with self.subTest(option=option, identity=identity):
                    self.review = self.home / f"identity-{option}-{i}"
                    code, result = self.call(option, identity)
                    self.assertEqual(code, 2, result)
                    self.assertFalse(self.review.exists())
        code, result = self.call("--author-model", " CLAUDE-OPUS-5-5\n")
        self.assertEqual(code, 2, result)
        self.assertIn("separate models", result["error"])
        code, result = self.call("--model", " FIXTURE-AUTHOR-V1\n")
        self.assertEqual(code, 2, result)
        self.assertIn("separate models", result["error"])
        self.assertEqual(self.calls(), [])

    def test_normalized_model_identity_is_used_in_packet_state_and_argv(self):
        code, result = self.call("--model", " reviewer-v1\t", "--author-model", " author-v2\n")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["model"], "reviewer-v1")
        entry = self.state()["exchanges"][0]
        self.assertEqual(entry["model"], "reviewer-v1")
        self.assertEqual(entry["author_model"], "author-v2")
        argv = self.calls()[0]
        self.assertEqual(argv[argv.index("--model") + 1], "reviewer-v1")
        packet = Path(result["packet"]).read_text()
        self.assertIn("Author model: author-v2\nReviewer: claude / reviewer-v1\n", packet)

    def test_missing_or_empty_inputs(self):
        self.checks.unlink()
        self.assertEqual(self.call()[0], 2)
        self.checks.write_text("")
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.calls(), [])
        self.assertFalse(self.review.exists())

    def test_invalid_initial_inputs_leave_no_output_directory_or_parents(self):
        self.review = self.home / "new-output-parent/review"
        for extra in (("--brief", str(self.home / "missing.md")),
                      ("--repo", str(self.home)), ("--base", "missing-ref"),
                      ("--exclude", "../outside"), ("--max-packet-bytes", "40")):
            with self.subTest(extra=extra):
                code, result = self.call(*extra)
                self.assertEqual(code, 2, result)
                self.assertFalse(self.review.parent.exists())
        (self.repo / "binary.bin").write_bytes(b"a\x00b")
        self.assertEqual(self.call()[0], 2)
        self.assertFalse(self.review.parent.exists())
        self.assertEqual(self.calls(), [])

    def test_reconciliation_without_history_leaves_output_untouched(self):
        evidence = self.home / "stop-evidence.md"
        evidence.write_text("No reviewer process was started.\n")
        self.assertEqual(self.call("--reconcile-round", "1", "--reconciliation", str(evidence))[0], 2)
        self.assertFalse(self.review.exists())

    def test_explicit_base_and_complete_committed_history(self):
        (self.repo / "calc.py").write_text("# committed change\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Committed fixture change")
        code, result = self.call("--base", self.base)
        self.assertEqual(code, 0, result)
        self.assertIn("Committed fixture change", Path(result["packet"]).read_text())

    def test_origin_main_default(self):
        self.git("update-ref", "refs/remotes/origin/main", self.base)
        self.assertEqual(self.call()[0], 0)
        self.assertEqual(self.state()["base"], self.base)

    def test_literal_exclusions_apply_to_all_sections(self):
        private = "private[1].txt"
        (self.repo / private).write_text("DO_NOT_TRANSMIT\n")
        self.git("add", private)
        (self.repo / "private1.txt").write_text("INCLUDE_LITERAL_NEIGHBOUR\n")
        code, result = self.call("--exclude", private)
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertNotIn("DO_NOT_TRANSMIT", packet)
        self.assertIn("INCLUDE_LITERAL_NEIGHBOUR", packet)

    def test_untracked_binary_and_large_packet_refuse(self):
        (self.repo / "binary.bin").write_bytes(b"a\x00b")
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.call("--exclude", "binary.bin", "--max-packet-bytes", "40")[0], 2)
        self.assertEqual(self.calls(), [])

    def test_tracked_binary_refuses(self):
        (self.repo / "calc.py").write_bytes(b"\0binary")
        self.assertEqual(self.call()[0], 2)

    def test_symlink_content_is_not_followed(self):
        secret = self.home / "outside"
        secret.write_text("OUTSIDE_PRIVATE_CONTENT")
        (self.repo / "link").symlink_to(secret)
        code, result = self.call()
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn("not followed", packet)
        self.assertNotIn("OUTSIDE_PRIVATE_CONTENT", packet)

    def test_unsafe_output_location_refuses(self):
        self.review = self.repo / "not-ignored"
        before = self.git("status", "--porcelain", "--untracked-files=all")
        self.assertEqual(self.call()[0], 2)
        self.assertFalse(self.review.exists())
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=all"), before)
        self.assertEqual(self.call("--exclude", "not-ignored")[0], 0)

    def test_ignored_output_location(self):
        self.review = self.repo / "artifacts/review"
        self.assertEqual(self.call()[0], 0)

    def test_ignoring_only_json_does_not_cover_review_artifacts(self):
        (self.repo / ".gitignore").write_text("*.json\n")
        self.review = self.repo / "partial-ignore"
        code, result = self.call()
        self.assertEqual(code, 2, result)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.call("--exclude", "partial-ignore")[0], 0)

    def test_exact_artifact_ignore_list_without_directory_rule_refuses(self):
        names = [".review.lock", "review-state.json", ".review-state-probe"]
        for n in range(1, 4):
            names += ["review-packet.md" if n == 1 else f"review-packet-{n}.md",
                      f"review-command-{n}.txt", f"review-round-{n}.md",
                      f"review-round-{n}.stderr.log", f"review-round-{n}.stdout.log",
                      f"review-reconciliation-{n}.md"]
        (self.repo / ".gitignore").write_text("\n".join("exact-ignore/" + n for n in names) + "\n")
        self.review = self.repo / "exact-ignore"
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.calls(), [])

    def test_glob_character_review_directory_cannot_hide_tracked_overlap(self):
        self.review = self.repo / "review[1]"
        self.review.mkdir()
        (self.review / "keep.md").write_text("Tracked source must not share the evidence directory.\n")
        self.git("add", ".")
        code, result = self.call("--exclude", "review[1]")
        self.assertEqual(code, 2, result)
        self.assertIn("overlap tracked files", result["error"])
        self.assertEqual(self.calls(), [])
        self.assertEqual(sorted(p.name for p in self.review.iterdir()), ["keep.md"])

    def test_invalid_input_does_not_add_lock_to_existing_output_directory(self):
        self.review.mkdir()
        marker = self.review / "unrelated.txt"
        marker.write_text("Keep existing content.\n")
        self.checks.unlink()
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(list(self.review.iterdir()), [marker])

    def test_text_forced_nul_is_rejected_before_model_invocation(self):
        (self.repo / ".gitattributes").write_text("*.py diff\n")
        (self.repo / "calc.py").write_bytes(b"# forced text\0with binary data\n")
        self.git("add", ".")
        code, result = self.call()
        self.assertEqual(code, 2, result)
        self.assertIn("NUL", result["error"])
        self.assertEqual(self.calls(), [])

    def test_invalid_exclusion_refuses(self):
        for path in ("../outside", ".", "/absolute"):
            self.assertEqual(self.call("--exclude", path)[0], 2)

    def test_subsequent_packet_contains_raw_findings_and_dispositions(self):
        self.assertEqual(self.call()[0], 0)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn(REPORT, packet)
        self.assertIn("CMR-001: accepted", packet)
        self.assertEqual(result["round"], 2)

    def test_revisit_surfaces_prior_exclusions_and_authorship(self):
        self.assertEqual(self.call("--exclude", "private")[0], 0)
        code, result = self.call("--exclude", "private", "--exclude", "calc.py",
                                 "--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn('Exclusions (literal paths and subtrees): ["calc.py", "private"]', packet)
        self.assertIn('"exclusions": [\n    "private"\n  ]', packet)
        self.assertIn('"author_model": "fixture-author-v1"', packet)
        self.assertIn('"effort": "max"', packet)
        self.assertIn('"tool": "claude"', packet)

    def test_revisit_requires_dispositions(self):
        self.call()
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(len(self.calls()), 1)
        self.dispositions.write_text("")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_empty_report_field_is_invalid(self):
        code, result = self.call(env={"FAKE_REPORT": REPORT.replace("Summary: Reviewed the complete supplied change.", "Summary:")})
        self.assertEqual(code, 1, result)
        self.assertEqual(result["execution"], "invalid_output")

    def test_damaged_history_and_outside_artifact_refuse(self):
        self.call()
        state = self.state()
        for damaged in ([], {"version":1,"exchanges":[]},
                        {**state,"exchanges":[{**state['exchanges'][0],"status":[]}]},
                        {**state,"exchanges":[{**state['exchanges'][0],"files":{"report":"../brief.md"}}]}):
            (self.review / "review-state.json").write_text(json.dumps(damaged))
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_nonfinite_timeout_refuses_before_invocation(self):
        for value in ("nan", "inf", "-1"):
            self.assertEqual(self.call("--timeout", value)[0], 2)
        self.assertEqual(self.calls(), [])

    def test_three_exchange_cap_survives_model_changes(self):
        for model in ("reviewer-one", "reviewer-two", "reviewer-three"):
            self.assertEqual(self.call("--model", model, "--dispositions", str(self.dispositions))[0], 0)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 2, result)
        self.assertIn("exhausted", result["error"])
        self.assertEqual(len(self.calls()), 3)
        self.assert_allowance(result, 3, 3)

    def test_checkpoint_continuation_preserves_history_and_stops_at_new_boundary(self):
        for _ in range(3):
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        before, entries = self.evidence(), self.state()["exchanges"]
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 2, result)
        self.assertEqual(self.evidence(), before)
        grant = self.continuation(allowance=2)
        probes = self.home / "metadata-cli-calls"
        code, result = self.continue_call(grant, env={"FAIL_ANY_CLI": "1", "ALL_CALL_LOG": str(probes)})
        self.assertEqual(code, 0, result)
        self.assertEqual(result["execution"], "continuation_recorded")
        self.assertEqual(len(self.calls()), 3)
        self.assertFalse(probes.exists())
        self.assert_allowance(result, 3, 5)
        self.assertEqual(self.state()["exchanges"], entries)
        for name, data in before.items():
            if name != "review-state.json":
                self.assertEqual((self.review / name).read_bytes(), data)
        self.assertEqual(Path(result["decision"]).read_bytes(), grant.read_bytes())
        self.assertEqual(Path(result["brief"]).read_bytes(), self.brief.read_bytes())
        for round_number in (4, 5):
            code, result = self.call("--dispositions", str(self.dispositions))
            self.assertEqual(code, 0, result)
            self.assertEqual(result["round"], round_number)
            self.assert_allowance(result, round_number, 5)
            packet = Path(result["packet"]).read_text()
            self.assertIn(grant.read_text(), packet)
            self.assertEqual(packet.count(REPORT), round_number - 1)
            self.assertIn("CMR-001: accepted", packet)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        self.assertEqual(len(self.calls()), 5)

    def test_early_revised_brief_retires_unused_allowance_and_retains_prior_scope(self):
        self.assertEqual(self.call()[0], 0)
        initial_hash = self.state()["brief_sha256"]
        initial_packet = (self.review / "review-packet.md").read_bytes()
        self.brief.write_bytes(b"New authorized requirement.\r\nPreserve prior integer behavior.\r\n")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        grant = self.continuation(allowance=2, basis="new_authorized_work")
        code, result = self.continue_call(grant)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 1, 3)
        self.assertEqual(self.state()["brief_sha256"], initial_hash)
        self.assertEqual(Path(result["brief"]).read_bytes(), self.brief.read_bytes())
        for _ in range(2):
            code, result = self.call("--dispositions", str(self.dispositions))
            self.assertEqual(code, 0, result)
            packet = Path(result["packet"]).read_text()
            self.assertIn("New authorized requirement.", packet)
            self.assertIn(REPORT, packet)
            self.assertIn(initial_hash, packet)
            self.assertIn(str(self.review.resolve() / "review-packet.md"), packet)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        self.assertEqual(len(self.calls()), 3)
        self.assertEqual((self.review / "review-packet.md").read_bytes(), initial_packet)

    def test_early_changed_approach_replaces_slots_and_replay_never_regrants(self):
        self.assertEqual(self.call()[0], 0)
        first = self.continuation(allowance=3, basis="changed_approach")
        self.assertEqual(self.continue_call(first)[0], 0)
        before = self.evidence()
        code, result = self.continue_call(first)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["replayed"])
        self.assert_allowance(result, 1, 4)
        self.assertEqual(self.evidence(), before)
        for _ in range(3):
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        before = self.evidence()
        code, result = self.continue_call(first)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 4, 4)
        self.assertEqual(self.evidence(), before)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        second = self.continuation("second.json", allowance=1)
        self.assertEqual(self.continue_call(second)[0], 0)
        before = self.evidence()
        code, result = self.continue_call(first)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 4, 5)
        self.assertEqual(self.evidence(), before)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        self.assertEqual(len(self.calls()), 5)

    def test_same_round_decisions_replace_allowance_and_old_brief_replay_is_inert(self):
        self.call()
        original = self.brief.read_bytes()
        first = self.continuation(allowance=3)
        self.assertEqual(self.continue_call(first)[0], 0)
        self.brief.write_text("Revised current basis\n")
        second = self.continuation("second.json", allowance=1, basis="new_authorized_work")
        code, result = self.continue_call(second)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 1, 2)
        old_brief = self.home / "old-brief.md"
        old_brief.write_bytes(original)
        before = self.evidence()
        code, result = self.continue_call(first, "--brief", str(old_brief))
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 1, 2)
        self.assertEqual(self.evidence(), before)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn(original.decode().strip(), packet)
        self.assertIn("Revised current basis", packet)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_v1_history_stays_v1_until_explicit_promotion_without_rewriting_evidence(self):
        self.call()
        state = self.state()
        state["version"] = 1
        state.pop("continuations", None)
        state["exchanges"][0].pop("exclusions", None)
        (self.review / "review-state.json").write_text(json.dumps(state))
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        self.assertEqual(self.state()["version"], 1)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        before, entries = self.evidence(), self.state()["exchanges"]
        grant = self.continuation()
        self.assertEqual(self.continue_call(grant)[0], 0)
        self.assertEqual(self.state()["version"], 2)
        self.assertEqual(self.state()["exchanges"], entries)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        for name, data in before.items():
            if name != "review-state.json":
                self.assertEqual((self.review / name).read_bytes(), data)
        self.assertEqual(self.state()["exchanges"][:3], entries)

    def test_continuation_rejects_malformed_stale_and_mixed_operations_without_effects(self):
        self.call()
        valid = self.continuation()
        value = json.loads(valid.read_text())
        before = self.evidence()
        for changes in ({"version": True}, {"version": 2}, {"after_round": True}, {"after_round": 0},
                        {"allowance": True}, {"allowance": 0}, {"allowance": 4}, {"allowance": 1.5},
                        {"owner": " "}, {"authorization_source": ""}, {"rationale": []}, {"basis": "retry"},
                        {"history_sha256": "0" * 64}, {"history_sha256": "bad"},
                        {"brief_sha256": "0" * 64}, {"extra": "unknown"}):
            with self.subTest(changes=changes):
                valid.write_text(json.dumps({**value, **changes}))
                self.assertEqual(self.continue_call(valid)[0], 2)
                self.assertEqual(self.evidence(), before)
        for raw in ("", "{", "[]", json.dumps(value)[:-1] + ', "allowance": 2}'):
            valid.write_text(raw)
            self.assertEqual(self.continue_call(valid)[0], 2)
            self.assertEqual(self.evidence(), before)
        original_brief = self.brief.read_bytes()
        self.brief.write_text("\u00a0\n")
        blank_brief = self.continuation("blank-brief.json")
        self.assertEqual(self.continue_call(blank_brief)[0], 2)
        self.assertEqual(self.evidence(), before)
        self.brief.write_bytes(original_brief)
        valid.write_text(json.dumps(value))
        for option, argument in (("--tool", "claude"), ("--model", "reviewer"), ("--effort", "max"),
                                 ("--checks", str(self.checks)), ("--authorization", str(self.auth)),
                                 ("--dispositions", str(self.dispositions)), ("--author-model", "author"),
                                 ("--timeout", "1800"), ("--max-packet-bytes", "2097152"),
                                 ("--reconcile-round", "1"), ("--reconciliation", str(self.checks))):
            with self.subTest(option=option):
                self.assertEqual(self.continue_call(valid, option, argument)[0], 2)
                self.assertEqual(self.evidence(), before)
        self.assertEqual(self.continue_call(valid)[0], 0)
        before = self.evidence()
        valid.write_text(json.dumps({**value, "rationale": "Changed bytes using the stale token"}))
        self.assertEqual(self.continue_call(valid)[0], 2)
        self.assertEqual(self.evidence(), before)
        self.assertEqual(len(self.calls()), 1)

    def test_continuation_never_adopts_missing_or_legacy_history_or_new_repo_base(self):
        self.call()
        grant = self.continuation()
        before = self.evidence()
        for args in (("--repo", str(self.home)), ("--brief", str(self.checks)), ("--base", "missing-ref"),
                     ("--exclude", "../outside")):
            self.assertEqual(self.continue_call(grant, *args)[0], 2)
            self.assertEqual(self.evidence(), before)
        self.git("commit", "--allow-empty", "-qm", "Different base")
        self.assertEqual(self.continue_call(grant, "--base", "HEAD")[0], 2)
        missing = self.home / "missing-parent/history"
        self.assertEqual(self.continue_call(grant, "--review-dir", str(missing))[0], 2)
        self.assertFalse(missing.parent.exists())
        legacy = self.home / "legacy"
        legacy.mkdir()
        (legacy / "review-round-1.md").write_text(REPORT)
        self.assertEqual(self.continue_call(grant, "--review-dir", str(legacy))[0], 2)
        self.assertEqual([p.name for p in legacy.iterdir()], ["review-round-1.md"])

    def test_uncertainty_blocks_continuation_and_replay_until_reconciled(self):
        self.call()
        first = self.continuation(allowance=3)
        self.assertEqual(self.continue_call(first)[0], 0)
        self.assertEqual(self.call("--dispositions", str(self.dispositions), "--timeout", "0.1",
                                   env={"FAKE_MODE": "slow"})[0], 1)
        stale = self.continuation("stale.json", basis="repaired_prerequisite")
        before = self.evidence()
        self.assertEqual(self.continue_call(stale)[0], 2)
        self.assertEqual(self.continue_call(first)[0], 2)
        self.assertEqual(self.evidence(), before)
        stopped = self.home / "stopped.md"
        stopped.write_text("Owned stub group was terminated; no other processes launched.\n")
        code, result = self.call("--reconcile-round", "2", "--reconciliation", str(stopped))
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 2, 4)
        before = self.evidence()
        self.assertEqual(self.continue_call(stale)[0], 2)
        self.assertEqual(self.evidence(), before)
        code, result = self.continue_call(first)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 2, 4)
        fresh = self.continuation("fresh.json", basis="repaired_prerequisite")
        self.assertEqual(self.continue_call(fresh)[0], 0)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_failed_and_invalid_launches_count_preflight_refusals_do_not(self):
        for mode in ("exit", "malformed", "empty"):
            code, result = self.call("--dispositions", str(self.dispositions), env={"FAKE_MODE": mode})
            self.assertEqual(code, 1, result)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        grant = self.continuation()
        self.assertEqual(self.continue_call(grant)[0], 0)
        before = self.evidence()
        self.assertEqual(self.call("--author-model", "unknown")[0], 2)
        self.assertEqual(self.evidence(), before)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 4, 4)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_continuation_evidence_tampering_or_invalid_sequence_is_refused(self):
        self.call()
        grant = self.continuation()
        code, result = self.continue_call(grant)
        self.assertEqual(code, 0, result)
        state_file = self.review / "review-state.json"
        for name in ("decision", "brief"):
            file = Path(result[name])
            original = file.read_bytes()
            file.write_bytes(original + b"tampered")
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
            self.assertEqual(self.continue_call(grant)[0], 2)
            file.unlink()
            self.assertEqual(self.continue_call(grant)[0], 2)
            file.symlink_to(self.brief)
            self.assertEqual(self.continue_call(grant)[0], 2)
            file.unlink()
            file.write_bytes(original)
        state_bytes = state_file.read_bytes()
        recorded = json.loads(state_bytes)
        decision_path = Path(result["decision"])
        decision_bytes = decision_path.read_bytes()
        # Even matching artifact hashes cannot authorize an impossible sequence.
        bad = json.loads(decision_bytes)
        bad["after_round"] = 2
        decision_path.write_text(json.dumps(bad))
        recorded["continuations"][0]["hashes"]["decision"] = hashlib.sha256(decision_path.read_bytes()).hexdigest()
        state_file.write_text(json.dumps(recorded))
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        decision_path.write_bytes(decision_bytes)
        state_file.write_bytes(state_bytes)
        (self.review / "review-round-1.md").write_text("altered original")
        self.assertEqual(self.continue_call(grant)[0], 2)

    def test_complete_orphan_evidence_retry_finishes_once_after_state_write_failure(self):
        self.call()
        grant = self.continuation()
        state_bytes = (self.review / "review-state.json").read_bytes()
        spec = importlib.util.spec_from_file_location("review_for_failure_fixture", RUNNER)
        module = importlib.util.module_from_spec(spec)
        with patch.object(sys, "path", [str(RUNNER.parent), *sys.path]):
            spec.loader.exec_module(module)
        args = module.parser().parse_args(self.continuation_command(grant)[3:])
        with patch.dict(os.environ, self.env, clear=True), \
                patch.object(module, "atomic_json", side_effect=OSError("Synthetic state-write failure")), \
                patch.object(module, "build", side_effect=AssertionError("Metadata must not probe a reviewer")):
            with self.assertRaisesRegex(OSError, "Synthetic state-write failure"):
                module.run(args)
        self.assertEqual((self.review / "review-state.json").read_bytes(), state_bytes)
        orphan_decision = (self.review / "review-continuation-1.json").read_bytes()
        orphan_brief = (self.review / "review-brief-1.md").read_bytes()
        self.assertEqual(orphan_decision, grant.read_bytes())
        self.assertEqual(orphan_brief, self.brief.read_bytes())
        code, result = self.continue_call(grant)
        self.assertEqual(code, 0, result)
        self.assert_allowance(result, 1, 2)
        before = self.evidence()
        self.assertEqual(self.continue_call(grant)[0], 0)
        self.assertEqual(self.evidence(), before)
        self.assertEqual(len(self.state()["continuations"]), 1)
        self.assertEqual(len(self.calls()), 1)

    def test_partial_conflicting_symlinked_and_unexpected_orphans_are_preserved(self):
        self.call()
        grant = self.continuation()
        decision_file = self.review / "review-continuation-1.json"
        brief_file = self.review / "review-brief-1.md"
        decision_file.write_bytes(grant.read_bytes())
        before = self.evidence()
        self.assertEqual(self.continue_call(grant)[0], 2)
        self.assertEqual(self.evidence(), before)
        brief_file.write_text("partial brief")
        before = self.evidence()
        self.assertEqual(self.continue_call(grant)[0], 2)
        self.assertEqual(self.evidence(), before)
        brief_file.unlink()
        brief_file.symlink_to(self.brief)
        self.assertEqual(self.continue_call(grant)[0], 2)
        self.assertTrue(brief_file.is_symlink())
        brief_file.unlink()
        brief_file.write_bytes(self.brief.read_bytes())
        extra = self.review / "review-continuation-9.json"
        extra.write_text("unexpected evidence")
        before = self.evidence()
        self.assertEqual(self.continue_call(grant)[0], 2)
        self.assertEqual(self.evidence(), before)

    def test_continuation_checks_new_artifacts_and_cumulative_round_output_paths(self):
        self.review = self.repo / "artifacts/review"
        for _ in range(3):
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 0)
        grant = self.continuation()
        before = self.evidence()
        (self.repo / ".gitignore").write_text("ignored.txt\n")
        self.assertEqual(self.continue_call(grant)[0], 2)
        self.assertEqual(self.evidence(), before)
        (self.repo / ".gitignore").write_text("artifacts/\nignored.txt\n")
        for name in ("review-continuation-1.json", "review-brief-1.md", "review-round-4.md"):
            file = self.review / name
            file.write_text("Tracked content must not be overwritten\n")
            self.git("add", "-f", str(file))
            before = self.evidence()
            self.assertEqual(self.continue_call(grant, "--exclude", "artifacts/review")[0], 2)
            self.assertEqual(self.evidence(), before)
            self.git("rm", "--cached", str(file))
            file.unlink()
        self.assertEqual(self.continue_call(grant)[0], 0)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["round"], 4)
        self.assertEqual(self.git("status", "--porcelain"), b"")

    def test_concurrent_decisions_cannot_duplicate_or_stack_a_grant(self):
        self.call()
        for count, identical in enumerate((True, False), 1):
            first = self.continuation(f"first-{count}.json")
            second = first if identical else self.continuation(f"second-{count}.json", rationale="Distinct supplied decision")
            processes = [subprocess.Popen(self.continuation_command(file), env=self.env,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                         for file in (first, second)]
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=15)
                self.assertNotIn("Traceback", stderr)
                results.append((process.returncode, json.loads(stdout)))
            self.assertIn(0, [code for code, _ in results])
            if not identical:
                self.assertEqual(sorted(code for code, _ in results), [0, 2])
            self.assertEqual(len(self.state()["continuations"]), count)
            self.assertEqual(len(self.calls()), 1)
            winner = next(result for code, result in results if code == 0)
            self.assert_allowance(winner, 1, 2)

    def test_active_review_lock_blocks_continuation_and_reconciliation(self):
        self.call()
        grant = self.continuation()
        proc = subprocess.Popen(self.command("--dispositions", str(self.dispositions)),
                                env={**self.env, "FAKE_MODE": "slow"},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for _ in range(150):
                if len(self.calls()) == 2 and self.state()["exchanges"][-1]["status"] == "running":
                    break
                time.sleep(0.02)
            self.assertEqual(len(self.calls()), 2)
            lock_inode = (self.review / ".review.lock").stat().st_ino
            before = self.evidence()
            code, result = self.continue_call(grant)
            self.assertEqual(code, 2, result)
            self.assertIn("owns", result["error"])
            self.assertEqual(self.call("--reconcile-round", "2", "--reconciliation", str(self.checks))[0], 2)
            self.assertEqual(self.evidence(), before)
            self.assertEqual((self.review / ".review.lock").stat().st_ino, lock_inode)
            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate(timeout=8)
            self.assertEqual(json.loads(stdout)["execution"], "cancelled", stderr)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

    def test_recovered_v1_missing_packet_stays_missing_after_revised_brief_continuation(self):
        self.call()
        state = self.state()
        state["version"] = 1
        state.pop("continuations")
        state["exchanges"][0].update(status="starting", pid=None, hashes={})
        (self.review / "review-packet.md").unlink()
        (self.review / "review-state.json").write_text(json.dumps(state))
        stale = self.continuation()
        self.assertEqual(self.continue_call(stale)[0], 2)
        stopped = self.home / "stopped.md"
        stopped.write_text("Synthetic interrupted journal; original stub completed and has no remaining process.\n")
        self.assertEqual(self.call("--reconcile-round", "1", "--reconciliation", str(stopped))[0], 0)
        reconciled = self.state()["exchanges"][0]
        self.assertIsNone(reconciled["hashes"]["packet"])
        self.brief.write_text("Revised requirement after interrupted initial capture.\n")
        fresh = self.continuation("fresh.json", basis="new_authorized_work")
        self.assertEqual(self.continue_call(fresh)[0], 0)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        packet = Path(result["packet"]).read_text()
        self.assertIn("Revised requirement after interrupted initial capture.", packet)
        self.assertIn(REPORT, packet)
        self.assertNotIn("Preserve every integer input, including negative values.", packet)
        self.assertFalse((self.review / "review-packet.md").exists())
        self.assertEqual(self.state()["exchanges"][0], reconciled)

    def test_continuation_history_cannot_be_silently_truncated_to_fit_packet_budget(self):
        self.call()
        grant = self.continuation(rationale="Supplied evidence. " * 1500)
        self.assertEqual(self.continue_call(grant)[0], 0)
        before = self.evidence()
        code, result = self.call("--dispositions", str(self.dispositions), "--max-packet-bytes", "15000")
        self.assertEqual(code, 2, result)
        self.assertEqual(self.evidence(), before)
        self.assertEqual(len(self.calls()), 1)

    def test_changed_brief_or_repo_does_not_reset_history(self):
        self.call()
        self.brief.write_text("A different task")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        self.assertEqual(len(self.calls()), 1)

    def test_tampered_report_is_detected(self):
        self.call()
        (self.review / "review-round-1.md").write_text("altered")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_legacy_directory_not_silently_restarted(self):
        self.review.mkdir()
        (self.review / "review-round-1.md").write_text(REPORT)
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.calls(), [])

    def test_invalid_output_is_retained(self):
        code, result = self.call(env={"FAKE_MODE":"malformed"})
        self.assertEqual(code, 1)
        self.assertEqual(result["execution"], "invalid_output")
        self.assertEqual(Path(result["report"]).read_text(), "I approve everything.")
        self.assertIsNone(result["outcome"])

    def test_empty_output_is_not_success(self):
        code, result = self.call(env={"FAKE_MODE":"empty"})
        self.assertEqual(code, 1)
        self.assertEqual(result["execution"], "invalid_output")

    def test_nonzero_exit_retains_report_without_counting_it_completed(self):
        code, result = self.call(env={"FAKE_MODE":"exit"})
        self.assertEqual(code, 1)
        self.assertEqual(result["execution"], "failed")
        self.assertIsNone(result["outcome"])
        self.assertEqual(Path(result["report"]).read_text(), REPORT)
        self.assertEqual(self.state()["exchanges"][0]["returncode"], 7)

    def test_advisory_blocked_is_separate_from_execution(self):
        code, result = self.call(env={"FAKE_REPORT":REPORT.replace("SUGGESTIONS", "BLOCKED", 1)})
        self.assertEqual(code, 0)
        self.assertEqual((result["execution"], result["outcome"]), ("completed", "BLOCKED"))

    def test_timeout_requires_explicit_reconciliation_without_restoring_allowance(self):
        code, result = self.call("--timeout", "0.1", env={"FAKE_MODE":"slow"})
        self.assertEqual(code, 1)
        self.assertEqual(result["execution"], "timeout")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        evidence = self.home / "stopped.md"
        evidence.write_text("The stub process group has exited; no other processes were launched.\n")
        self.assertEqual(self.call("--reconcile-round", "1", "--reconciliation", str(evidence))[0], 0)
        code, result = self.call("--dispositions", str(self.dispositions))
        self.assertEqual(code, 0, result)
        self.assertEqual(result["round"], 2)

    def test_reconciliation_note_retry_after_partial_failure_and_integrity(self):
        self.call("--timeout", "0.1", env={"FAKE_MODE":"slow"})
        evidence = self.home / "stopped.md"
        evidence.write_text("Owned stub group stopped; no separate processes launched.\n")
        note = self.review / "review-reconciliation-1.md"
        # Persisted state after a note write succeeds but the journal update fails.
        note.write_bytes(evidence.read_bytes())
        self.assertEqual(self.state()["exchanges"][0]["status"], "timeout")
        args = ("--reconcile-round", "1", "--reconciliation", str(evidence))
        self.assertEqual(self.call(*args)[0], 0)
        self.assertEqual(self.call(*args)[0], 0)
        self.assertEqual(self.state()["exchanges"][0]["reconciliation_sha256"],
                         hashlib.sha256(evidence.read_bytes()).hexdigest())
        evidence.write_text("Different evidence must not replace the original.\n")
        self.assertEqual(self.call(*args)[0], 2)
        note.write_text("tampered")
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_concurrent_call_and_interruption(self):
        proc = subprocess.Popen(self.command(), env={**self.env, "FAKE_MODE":"slow"},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for _ in range(100):
                if self.calls():
                    break
                time.sleep(0.02)
            self.assertTrue(self.calls())
            lock = self.review / ".review.lock"
            lock_inode = lock.stat().st_ino
            before = {p.name: p.read_bytes() for p in self.review.iterdir()}
            code, result = self.call()
            self.assertEqual(code, 2)
            self.assertIn("owns", result["error"])
            self.assertEqual(self.call("--brief", str(self.home / "missing.md"))[0], 2)
            code, result = self.call()
            self.assertEqual(code, 2)
            self.assertIn("owns", result["error"])
            self.assertEqual(lock.stat().st_ino, lock_inode)
            self.assertEqual({p.name: p.read_bytes() for p in self.review.iterdir()}, before)
            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate(timeout=8)
            self.assertEqual(json.loads(stdout)["execution"], "cancelled", stderr)
            self.assertEqual(len(self.calls()), 1)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

    def test_history_is_rechecked_under_lock_after_concurrent_preflight(self):
        gate = self.home / "release-probe"
        proc = subprocess.Popen(self.command("--tool", "codex"),
                                env={**self.env, "PROBE_GATE": str(gate)},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for _ in range(150):
                if Path(str(gate) + ".ready").exists():
                    break
                time.sleep(0.02)
            self.assertTrue(Path(str(gate) + ".ready").exists())
            self.assertEqual(self.call()[0], 0)
            lock_inode = (self.review / ".review.lock").stat().st_ino
            before = {p.name: p.read_bytes() for p in self.review.iterdir()}
            gate.touch()
            stdout, stderr = proc.communicate(timeout=8)
            self.assertEqual(proc.returncode, 2, stdout + stderr)
            self.assertIn("history changed", json.loads(stdout)["error"])
            self.assertEqual(len(self.calls()), 1)
            self.assertEqual((self.review / ".review.lock").stat().st_ino, lock_inode)
            self.assertEqual({p.name: p.read_bytes() for p in self.review.iterdir()}, before)
        finally:
            gate.touch()
            if proc.poll() is None:
                proc.communicate(timeout=8)

    def test_surviving_reviewer_child_requires_reconciliation(self):
        code, result = self.call(env={"FAKE_MODE":"orphan"})
        self.assertEqual(code, 1, result)
        self.assertEqual(result["execution"], "unknown")
        self.assertEqual(Path(result["report"]).read_text(), REPORT)
        self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)

    def test_crash_reconciliation_freezes_present_and_absent_evidence(self):
        proc = subprocess.Popen(self.command(), env={**self.env, "FAKE_MODE":"slow"},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        native_pid = None
        try:
            for _ in range(150):
                state_file = self.review / "review-state.json"
                if state_file.exists():
                    native_pid = self.state()["exchanges"][0].get("pid")
                if native_pid and self.calls():
                    break
                time.sleep(0.02)
            self.assertTrue(native_pid)
            proc.kill()
            proc.communicate(timeout=5)
            os.killpg(native_pid, signal.SIGTERM)
            for _ in range(150):
                try:
                    os.killpg(native_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.02)
            evidence = self.home / "crash-stopped.md"
            evidence.write_text("Owned stub identity checked; runner killed, native group stopped.\n")
            code, result = self.call("--reconcile-round", "1", "--reconciliation", str(evidence))
            self.assertEqual(code, 0, result)
            hashes = self.state()["exchanges"][0]["hashes"]
            self.assertIsNone(hashes["report"])
            packet = self.review / "review-packet.md"
            original = packet.read_bytes()
            packet.write_bytes(original + b"tampered")
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
            packet.write_bytes(original)
            (self.review / "review-round-1.md").write_text(REPORT)
            self.assertEqual(self.call("--dispositions", str(self.dispositions))[0], 2)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
            if native_pid:
                try:
                    os.killpg(native_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_preflight_rejects_enabled_codex_integrations(self):
        for key in ("BAD_MCP", "BAD_FEATURE"):
            self.assertEqual(self.call("--tool", "codex", env={key:"1"})[0], 2)
        self.assertEqual(self.calls(), [])

    def test_preflight_rejects_unknown_muse_configuration(self):
        for key in ("BAD_POLICY", "BAD_PLUGINS"):
            self.assertEqual(self.call("--tool", "muse", env={key:"1"})[0], 2)
        (self.repo / ".muse").mkdir()
        (self.repo / ".muse/hooks.json").write_text('{"hooks":{}}')
        self.assertEqual(self.call("--tool", "muse")[0], 2)
        self.assertEqual(self.calls(), [])

    def test_preflight_rejects_muse_user_hooks_and_mcp(self):
        settings = Path(self.env["XDG_CONFIG_HOME"]) / "muse/settings.json"
        settings.parent.mkdir(parents=True)
        for config in ({"hooks":{"SessionStart":["fixture"]}}, {"managed_hooks_path":"fixture"},
                       {"mcp_servers":{"fixture":{}}}, {"mcpServers":{"fixture":{}}}, []):
            settings.write_text(json.dumps(config))
            self.assertEqual(self.call("--tool", "muse")[0], 2)
        self.assertEqual(self.calls(), [])


if __name__ == "__main__":
    unittest.main()
