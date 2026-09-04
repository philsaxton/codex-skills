from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = ROOT / "scripts" / "repository_cleanup.py"


def run(
    command: list[str], cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {command}\n{result.stdout}\n{result.stderr}"
        )
    return result


class RepositoryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run(["git", "init", "-b", "main"], self.repo)
        run(["git", "config", "user.name", "Cleanup Test"], self.repo)
        run(
            ["git", "config", "user.email", "cleanup@example.invalid"],
            self.repo,
        )
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "base.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def install_script(self, *, symlink: bool = False) -> Path:
        target = (
            self.root
            / "host"
            / ".agents"
            / "skills"
            / "cleaning-git-repositories"
        )
        (target / "scripts").mkdir(parents=True)
        installed = target / "scripts" / "repository_cleanup.py"
        if symlink:
            installed.symlink_to(SOURCE_SCRIPT)
        else:
            shutil.copy2(SOURCE_SCRIPT, installed)
        return installed

    def test_plan_requires_a_local_integration_branch(self) -> None:
        plan = self.root / "plan.json"
        result = run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "missing",
                "--plan",
                str(plan),
            ],
            self.repo,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integration branch", result.stderr)
        self.assertFalse(plan.exists())

    def test_apply_local_rejects_source_and_symlinked_installations(self) -> None:
        plan = self.root / "plan.json"
        run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--plan",
                str(plan),
            ],
            self.repo,
        )
        source_result = run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "apply-local",
                "--plan",
                str(plan),
            ],
            self.repo,
            check=False,
        )
        symlink_result = run(
            [
                sys.executable,
                str(self.install_script(symlink=True)),
                "apply-local",
                "--plan",
                str(plan),
            ],
            self.repo,
            check=False,
        )
        self.assertIn(
            "protected non-symlinked installation", source_result.stderr
        )
        self.assertIn(
            "protected non-symlinked installation", symlink_result.stderr
        )


if __name__ == "__main__":
    unittest.main()
