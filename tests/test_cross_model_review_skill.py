"""Exercise the packet commands in Git fixtures and optionally inspect Codex.

Set CMR_VALIDATE_CODEX=1 to run the installed CLI's configuration-only checks.
CMR_TEST_ARTIFACTS selects a parent directory for the isolated Git fixtures.
No model, MCP server, or external tool is invoked by the configuration checks.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "cross-model-review/SKILL.md").read_text()
EXAMPLE = (ROOT / "cross-model-review/references/reviewer-model.example").read_text()
GIT_COMMANDS = [
    shlex.split(command)
    for command in re.findall(r"`(git [^`\n]+)`", SKILL)
]


class PacketCaptureTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(
            prefix="cmr-git-", dir=os.environ.get("CMR_TEST_ARTIFACTS")
        )
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-q")
        (self.root / "tracked.txt").write_text("safe baseline\n")
        (self.root / ".gitignore").write_text("ignored.txt\n")
        self.git("add", "tracked.txt", ".gitignore")
        self.git("commit", "-qm", "Fixture baseline")
        self.base = self.git("rev-parse", "HEAD").decode().strip()

    def git(self, *args):
        return subprocess.run(
            ["git", "-c", "core.hooksPath=" + os.devnull,
             "-c", "user.name=Review Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", *args],
            cwd=self.root, env=self.env, check=True, capture_output=True,
        ).stdout

    def capture(self, prefix):
        command = next(command for command in GIT_COMMANDS
                       if command[:len(prefix)] == prefix)
        return self.git(*(self.base if arg == "<BASE>" else arg for arg in command[1:]))

    def test_untracked_inventory_includes_nested_and_unusual_names(self):
        expected = {
            "new-module/nested/implementation.py": "raise RuntimeError('review me')\n",
            'new-module/space "quote"\nand-newline.txt': "unusual path\n",
            "top-level.txt": "top level\n",
        }
        for name, content in expected.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        (self.root / "ignored.txt").write_text("not part of the change\n")
        self.git("config", "status.showUntrackedFiles", "no")
        inventory = self.capture(["git", "ls-files"]).split(b"\0")
        contents = {os.fsdecode(name): (self.root / os.fsdecode(name)).read_text()
                    for name in inventory if name}
        self.assertEqual(contents, expected)

    def test_codex_template_scopes_mcp_isolation_by_config_layer(self):
        self.assertIn("--ignore-user-config", EXAMPLE)
        self.assertIn("--ignore-rules", EXAMPLE)
        self.assertIn("MCP_OVERRIDES", EXAMPLE)
        self.assertIn("config files", EXAMPLE)

    def test_status_expands_new_directories_despite_user_configuration(self):
        (self.root / "new-module").mkdir()
        (self.root / "new-module/implementation.py").write_text("pass\n")
        self.git("config", "status.showUntrackedFiles", "no")
        status = self.capture(["git", "status"]).decode()
        self.assertIn("?? new-module/implementation.py\n", status)

    def test_packet_exposes_staged_change_canceled_in_working_tree(self):
        (self.root / "tracked.txt").write_text("unsafe staged version\n")
        self.git("add", "tracked.txt")
        (self.root / "tracked.txt").write_text("safe baseline\n")
        self.assertEqual(self.git("diff", self.base), b"")
        staged = self.capture(["git", "diff", "--cached"]).decode()
        unstaged_command = next(command for command in GIT_COMMANDS
                                if command == ["git", "diff"])
        unstaged = self.git(*unstaged_command[1:]).decode()
        self.assertIn("+unsafe staged version\n", staged)
        self.assertIn("-unsafe staged version\n", unstaged)
        self.assertIn("+safe baseline\n", unstaged)


@unittest.skipUnless(
    os.environ.get("CMR_VALIDATE_CODEX") == "1" and shutil.which("codex"),
    "set CMR_VALIDATE_CODEX=1 with Codex installed for native configuration checks",
)
class CodexTemplateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(
            prefix="cmr-codex-", dir=os.environ.get("CMR_TEST_ARTIFACTS")
        )
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, capture_output=True)
        (self.root / ".codex").mkdir()
        (self.root / ".codex/config.toml").write_text(
            '[mcp_servers."cmr.fixture.with-dots"]\n'
            'command = "/usr/bin/false"\nenabled = true\n'
            '[features]\napps = true\nplugins = true\nhooks = true\nmulti_agent = true\n'
        )

    def metadata(self, overrides, *operation):
        command = next(line[2:] for line in EXAMPLE.splitlines()
                       if line.startswith("# codex exec "))
        command = command.replace("{root}", shlex.quote(str(self.root)))
        command = command.replace("MCP_OVERRIDES", shlex.join(overrides))
        command = command.replace("MODEL", "cmr-config-probe").replace("EFFORT", "low")
        args = shlex.split(command)
        args = args[2:args.index("<")]
        # These exec-only options do not affect configuration inspection.
        args = [arg for arg in args
                if arg not in {"--ephemeral", "--ignore-rules",
                               "--ignore-user-config", "-"}]
        trust = 'projects={' + json.dumps(str(self.root.resolve())) + '={trust_level="trusted"}}'
        result = subprocess.run(
            [shutil.which("codex"), "-c", trust, *args, *operation],
            cwd=self.root, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, "Codex configuration inspection failed")
        return result.stdout

    def test_effective_mcp_inventory_and_features_are_disabled(self):
        inventory = json.loads(self.metadata([], "mcp", "list", "--json"))
        self.assertTrue(any(row["name"] == "cmr.fixture.with-dots" and row["enabled"]
                            for row in inventory))
        entries = ",".join(json.dumps(row["name"]) + "={enabled=false}" for row in inventory)
        overrides = ["-c", "mcp_servers={" + entries + "}"]
        observed = json.loads(self.metadata(overrides, "mcp", "list", "--json"))
        self.assertEqual({row["name"] for row in observed}, {row["name"] for row in inventory})
        self.assertFalse(any(row["enabled"] for row in observed))
        features = {parts[0]: parts[-1]
                    for line in self.metadata(overrides, "features", "list").splitlines()
                    if (parts := line.split())}
        for name in ("apps", "plugins", "hooks", "multi_agent"):
            self.assertEqual(features.get(name), "false", name)


RESULTS = (ROOT / "cross-model-review/references/results.md").read_text()


class PairReviewScopeTests(unittest.TestCase):
    COORDINATOR = (ROOT / "coordinator/SKILL.md").read_text()

    def test_skill_requires_an_assigned_separate_model(self):
        self.assertIn("separate reviewer model has already been assigned", SKILL)
        self.assertIn("coordinator", SKILL.lower())
        self.assertIn("separate reviewer model", self.COORDINATOR)

    def test_reviewer_model_lives_at_workspace_root_beside_agents(self):
        skill = " ".join(SKILL.split())
        coordinator = " ".join(self.COORDINATOR.split())
        self.assertIn("workspace root", skill)
        self.assertIn("AGENTS.md", skill)
        self.assertNotIn("`.reviewer-model` at the repository root", skill)
        self.assertIn("workspace root", coordinator)

    def test_contract_source_is_not_blocked_by_reviewer_model_file(self):
        skill = " ".join(SKILL.split())
        self.assertIn("do not consult `.reviewer-model`", skill)
        self.assertIn("only when the file supplies the command", skill)
        self.assertIn("whichever source supplied the command", skill)

    def test_reviewer_test_evidence_is_preserved_not_summarised(self):
        for text in (SKILL, RESULTS):
            flat = " ".join(text.split())
            self.assertIn("durable artifact", flat)
            self.assertIn("state tested", flat)
        self.assertIn("including failures", " ".join(RESULTS.split()))

    def test_pair_review_is_advisory_not_an_approval_gate(self):
        self.assertIn("advisory", SKILL.lower())
        self.assertNotIn("only the reviewer closes", SKILL.lower())
        self.assertNotIn("passes cross-model review only when", SKILL.lower())


if __name__ == "__main__":
    unittest.main()
