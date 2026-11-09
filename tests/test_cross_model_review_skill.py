"""Shared review guidance and opt-in checks against the installed native CLIs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "cross-model-review/SKILL.md").read_text()
RESULTS = (ROOT / "cross-model-review/references/results.md").read_text()


class NativeAdapterTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "cross-model-review/scripts"))
        self.addCleanup(sys.path.remove, sys.path[0])
        from adapters import build, environment
        self.build = build
        self.env = environment()
        tmp = tempfile.TemporaryDirectory(dir=os.getenv("CMR_TEST_ARTIFACTS"))
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    @unittest.skipUnless(os.getenv("CMR_VALIDATE_CODEX") == "1" and shutil.which("codex"), "optional Codex inspection")
    def test_codex_disables_configured_server_before_review(self):
        home = self.root / "codex-home"
        home.mkdir()
        self.env["CODEX_HOME"] = str(home)
        (home / "config.toml").write_text(
            '[mcp_servers."cmr.fixture.with-dots"]\ncommand = "/usr/bin/false"\nenabled = true\n')
        argv, _ = self.build("codex", "fixture", "max", self.root, self.root/"packet", self.root/"report", self.env)
        self.assertIn('mcp_servers={"cmr.fixture.with-dots"={enabled=false}}', argv)
        flags = argv[2:argv.index("--ignore-rules")]
        inspected = subprocess.run([argv[0], *flags, "mcp", "list", "--json"], cwd=self.root,
                                   env=self.env, capture_output=True, check=True, timeout=30)
        servers = {row["name"]:row["enabled"] for row in json.loads(inspected.stdout)}
        self.assertIs(servers["cmr.fixture.with-dots"], False)

    @unittest.skipUnless(os.getenv("CMR_VALIDATE_MUSE") == "1" and shutil.which("muse"), "optional local Muse inspection")
    def test_muse_exec_offers_only_assigned_tools(self):
        for access, expected in [("packet", []), ("read-search", ["read_file", "search"])]:
            _, notes = self.build("muse", "muse-wonder-full-1.0", "max", self.root,
                                  self.root/"packet", self.root/"report", self.env,
                                  muse_access=access, verify_muse_tools=True)
            tools = next(n["offered_tools"] for n in notes if n["inspection"] == "muse-exec-tools")
            self.assertCountEqual(tools, expected)


class PairReviewScopeTests(unittest.TestCase):
    COORDINATOR = (ROOT / "coordinator/SKILL.md").read_text()

    def test_skill_requires_an_assigned_separate_model(self):
        self.assertIn("separate reviewer model has already been assigned", SKILL)
        self.assertIn("coordinator", SKILL.lower())
        self.assertIn("separate reviewer model", self.COORDINATOR)

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
