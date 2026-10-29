"""Behavior tests using real Git repositories and local stub CLIs, no models."""
import hashlib
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
if args[:2]==["config","status"]:
 print("  plane=defaults source_class=system_file state="+("active" if os.getenv("BAD_POLICY") else "absent")); sys.exit(0)
if args[:2]==["plugins","list"]:
 print(json.dumps({"plugins": ["fixture"] if os.getenv("BAD_PLUGINS") else []})); sys.exit(0)
if "mcp" in args and "list" in args:
 disabled=any("mcp_servers=" in x for x in args)
 print(json.dumps([{"name":"server.with-dots","enabled": bool(os.getenv("BAD_MCP")) or not disabled}])); sys.exit(0)
if "features" in args and "list" in args:
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

    def test_missing_or_empty_inputs(self):
        self.checks.unlink()
        self.assertEqual(self.call()[0], 2)
        self.checks.write_text("")
        self.assertEqual(self.call()[0], 2)
        self.assertEqual(self.calls(), [])

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
        self.assertEqual(self.call()[0], 2)
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
            code, result = self.call()
            self.assertEqual(code, 2)
            self.assertIn("owns", result["error"])
            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate(timeout=8)
            self.assertEqual(json.loads(stdout)["execution"], "cancelled", stderr)
            self.assertEqual(len(self.calls()), 1)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

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
