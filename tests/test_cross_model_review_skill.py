"""Contract checks for the cross-model-review skill's packet completeness.

The skill is Markdown, so its durable regression surface is the exact Git
capture prescriptions and reviewer lockdown template it instructs. These
checks fail if a future edit drops them.
"""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "cross-model-review/SKILL.md").read_text()
EXAMPLE = (ROOT / "cross-model-review/references/reviewer-model.example").read_text()


class CrossModelReviewSkillTests(unittest.TestCase):
    def test_packet_enumerates_every_untracked_file(self):
        self.assertIn("--untracked-files=all", SKILL)
        self.assertIn("git ls-files --others --exclude-standard", SKILL)

    def test_packet_captures_staged_and_unstaged_separately(self):
        self.assertIn("git diff --cached <BASE>", SKILL)
        self.assertIn("git diff` (working tree against the index", SKILL)

    def test_codex_template_disables_write_capable_integrations(self):
        for flag in ("--ignore-user-config", "--disable apps",
                     "--disable plugins", "--disable hooks",
                     "--disable multi_agent"):
            self.assertIn(flag, EXAMPLE)


if __name__ == "__main__":
    unittest.main()
