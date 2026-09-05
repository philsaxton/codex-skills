from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "workspace-setup" / "scripts" / "init_workspace.py"


class WorkspaceSetupCliTests(unittest.TestCase):
    def run_script(self, target: Path, *, apply: bool = False) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, os.fspath(SCRIPT), os.fspath(target)]
        if apply:
            command.append("--apply")
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def git(
        self, directory: Path, *arguments: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", os.fspath(directory), *arguments],
            text=True,
            capture_output=True,
            check=check,
        )

    def assert_refused_without_writes(self, target: Path) -> subprocess.CompletedProcess[str]:
        result = self.run_script(target, apply=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_dry_run_reports_fixed_layout_without_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            target = Path(temporary).resolve() / "garage with spaces"

            result = self.run_script(target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists())
            self.assertIn(os.fspath(target), result.stdout)
            for relative_path in (".gitignore", "AGENTS.md", "README.md", "apps/", "artifacts/"):
                self.assertIn(relative_path, result.stdout)
            self.assertIn("dry run", result.stdout.lower())

    def test_apply_creates_thin_unstaged_repository_with_expected_boundaries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            target = Path(temporary).resolve() / "empty garage with spaces"
            target.mkdir()

            result = self.run_script(target, apply=True)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {".git", ".gitignore", "AGENTS.md", "README.md", "apps", "artifacts"},
            )
            self.assertTrue((target / "apps").is_dir())
            self.assertTrue((target / "artifacts").is_dir())
            self.assertEqual(list((target / "apps").iterdir()), [])
            self.assertEqual(list((target / "artifacts").iterdir()), [])
            self.assertFalse((target / ".git" / "hooks").exists())
            self.assertEqual(self.git(target, "diff", "--cached", "--name-only").stdout, "")
            self.assertEqual(self.git(target, "remote").stdout, "")

            app = target / "apps" / "sample app"
            app.mkdir()
            self.git(app, "init", "--quiet", "--template=")
            app_file = app / "main.py"
            app_file.write_text("print('sample')\n", encoding="utf-8")
            artifact_file = target / "artifacts" / "sample report.json"
            artifact_file.write_text("{}\n", encoding="utf-8")

            self.git(target, "add", ".")

            self.assertEqual(
                self.git(target, "diff", "--cached", "--name-only").stdout.splitlines(),
                [".gitignore", "AGENTS.md", "README.md"],
            )
            self.assertEqual(self.git(target, "check-ignore", "-q", os.fspath(app_file)).returncode, 0)
            self.assertEqual(
                self.git(target, "check-ignore", "-q", os.fspath(artifact_file)).returncode,
                0,
            )

    def test_apply_accepts_an_absent_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            target = Path(temporary).resolve() / "new garage"

            result = self.run_script(target, apply=True)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".git").is_dir())

    def test_rerun_refuses_and_preserves_the_workspace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            target = Path(temporary).resolve() / "garage"
            first = self.run_script(target, apply=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = {
                path.name: path.read_bytes()
                for path in target.iterdir()
                if path.is_file()
            }
            status_before = self.git(target, "status", "--porcelain=v1").stdout

            result = self.assert_refused_without_writes(target)

            after = {
                path.name: path.read_bytes()
                for path in target.iterdir()
                if path.is_file()
            }
            self.assertIn("not empty", result.stderr.lower())
            self.assertEqual(after, before)
            self.assertEqual(self.git(target, "status", "--porcelain=v1").stdout, status_before)

    def test_existing_content_is_refused_and_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            target = Path(temporary).resolve() / "occupied garage"
            target.mkdir()
            existing = target / "keep me.txt"
            existing.write_text("user data\n", encoding="utf-8")

            result = self.assert_refused_without_writes(target)

            self.assertIn("not empty", result.stderr.lower())
            self.assertEqual(existing.read_text(encoding="utf-8"), "user data\n")
            self.assertEqual(list(target.iterdir()), [existing])

    def test_ancestor_repository_is_refused_without_touching_its_index(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            repository = Path(temporary).resolve() / "owner repo"
            repository.mkdir()
            self.git(repository, "init", "--quiet", "--template=")
            tracked = repository / "tracked.txt"
            tracked.write_text("tracked\n", encoding="utf-8")
            self.git(repository, "add", "tracked.txt")
            index_before = self.git(repository, "ls-files", "--stage").stdout
            status_before = self.git(repository, "status", "--porcelain=v1").stdout
            target = repository / "nested garage"

            result = self.assert_refused_without_writes(target)

            self.assertIn("git repository", result.stderr.lower())
            self.assertFalse(target.exists())
            self.assertEqual(self.git(repository, "ls-files", "--stage").stdout, index_before)
            self.assertEqual(self.git(repository, "status", "--porcelain=v1").stdout, status_before)

    def test_bare_repository_ancestor_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            bare = Path(temporary).resolve() / "owner.git"
            subprocess.run(
                ["git", "init", "--bare", "--quiet", "--template=", os.fspath(bare)],
                text=True,
                capture_output=True,
                check=True,
            )
            target = bare / "empty target"
            target.mkdir()

            result = self.assert_refused_without_writes(target)

            self.assertIn("git repository", result.stderr.lower())
            self.assertEqual(list(target.iterdir()), [])

    def test_linked_worktree_ancestor_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            temporary_path = Path(temporary).resolve()
            original = temporary_path / "original"
            worktree = temporary_path / "linked worktree"
            original.mkdir()
            self.git(original, "init", "--quiet", "--template=")
            seed = original / "seed.txt"
            seed.write_text("seed\n", encoding="utf-8")
            self.git(original, "add", "seed.txt")
            self.git(
                original,
                "-c",
                "user.name=Workspace Test",
                "-c",
                "user.email=workspace@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "seed",
            )
            self.git(original, "worktree", "add", "--quiet", "--detach", os.fspath(worktree))
            target = worktree / "nested garage"

            result = self.assert_refused_without_writes(target)

            self.assertIn("git repository", result.stderr.lower())
            self.assertFalse(target.exists())

    def test_symlink_target_or_existing_component_is_refused(self) -> None:
        with tempfile.TemporaryDirectory(prefix="workspace setup ") as temporary:
            root = Path(temporary).resolve()
            real_target = root / "real target"
            real_target.mkdir()
            linked_target = root / "linked target"
            linked_target.symlink_to(real_target, target_is_directory=True)

            direct_result = self.assert_refused_without_writes(linked_target)

            self.assertIn("symbolic link", direct_result.stderr.lower())
            self.assertEqual(list(real_target.iterdir()), [])

            real_parent = root / "real parent"
            real_parent.mkdir()
            linked_parent = root / "linked parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            nested_target = linked_parent / "garage"

            component_result = self.assert_refused_without_writes(nested_target)

            self.assertIn("symbolic link", component_result.stderr.lower())
            self.assertFalse((real_parent / "garage").exists())


if __name__ == "__main__":
    unittest.main()
