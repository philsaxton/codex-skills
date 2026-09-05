from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "workspace-setup/scripts/init_workspace.py"
SOURCE_HELPER = ROOT / "workspace-setup/scripts/workspace_scratch.py"
spec = importlib.util.spec_from_file_location("scratch_helper", SOURCE_HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class WorkspaceScratchTests(unittest.TestCase):
    def setUp(self):
        # Scaffold refusal tests require a location outside any ancestor Git repo.
        self.temporary = tempfile.TemporaryDirectory(prefix="garage scratch ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.garage = self.base / "garage with spaces"
        subprocess.run([sys.executable, str(SCAFFOLD), str(self.garage), "--apply"],
                       check=True, capture_output=True)
        self.script = self.garage / "support/workspace_scratch.py"

    def run_helper(self, *args, success=True, script=None):
        p = subprocess.run([sys.executable, str(script or self.script), *args],
                           cwd=self.base, capture_output=True, text=True)
        if success:
            self.assertEqual(p.returncode, 0, p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout)
        return p

    def create(self, name="task-a"):
        p = self.run_helper("create", name)
        path = self.garage / "tmp" / name
        self.assertEqual(p.stdout.strip(), str(path))
        return path

    def complete(self, name="task-a"):
        self.run_helper("complete", name)

    def test_lifecycle_routes_real_temporary_output_and_preserves_other_tasks(self):
        task = self.create()
        other = self.create("task-b")
        nested = task / "nested"
        nested.mkdir()
        (nested / "scratch.txt").write_text("disposable")
        env = {**os.environ, "TMPDIR": str(task), "TMP": str(task), "TEMP": str(task)}
        p = subprocess.run([sys.executable, "-c",
                            "import tempfile; f=tempfile.NamedTemporaryFile(delete=False); print(f.name); f.close()"],
                           env=env, text=True, capture_output=True, check=True)
        self.assertEqual(Path(p.stdout.strip()).parent, task)
        report = self.garage / "artifacts/retain.txt"
        report.write_text("retained evidence")
        self.run_helper("clean", "task-a", "--apply", success=False)
        self.complete()
        before = {str(p.relative_to(task)): p.read_bytes() for p in task.rglob("*") if p.is_file()}
        self.run_helper("clean", "task-a")
        self.assertEqual(before, {str(p.relative_to(task)): p.read_bytes() for p in task.rglob("*") if p.is_file()})
        self.run_helper("clean", "task-a", "--apply")
        self.assertFalse(task.exists())
        self.assertTrue(other.is_dir())
        self.assertEqual(report.read_text(), "retained evidence")
        self.run_helper("clean", "task-a", "--apply", success=False)

    def test_occupied_unmarked_and_path_arguments_refused(self):
        task = self.create()
        marker = (task / helper.MARKER).read_bytes()
        self.run_helper("create", "task-a", success=False)
        self.assertEqual((task / helper.MARKER).read_bytes(), marker)
        unmarked = self.garage / "tmp/legacy"
        unmarked.mkdir()
        (unmarked / "keep").write_text("keep")
        self.run_helper("complete", "legacy", success=False)
        self.run_helper("clean", "legacy", "--apply", success=False)
        for name in ("..", "../apps", "/", str(task), "a/b", ".worktrees"):
            with self.subTest(name=name):
                self.run_helper("clean", name, "--apply", success=False)
        self.assertEqual((unmarked / "keep").read_text(), "keep")

    def test_repository_worktree_and_bare_content_refused(self):
        task = self.create()
        self.complete()
        for entries in ((".git",), (".worktrees",), ("HEAD", "objects", "refs")):
            with self.subTest(entries=entries):
                for name in entries:
                    (task / name).mkdir()
                self.run_helper("clean", "task-a", "--apply", success=False)
                self.assertTrue((task / helper.MARKER).exists())
                for name in entries:
                    (task / name).rmdir()

    def test_symlink_target_and_descendant_leave_external_data_intact(self):
        task = self.create()
        self.complete()
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "keep").write_text("external")
        (task / "link").symlink_to(outside, target_is_directory=True)
        self.run_helper("clean", "task-a", "--apply", success=False)
        (task / "link").unlink()
        (self.garage / "tmp/link-task").symlink_to(outside, target_is_directory=True)
        self.run_helper("clean", "link-task", "--apply", success=False)
        self.assertEqual((outside / "keep").read_text(), "external")
        moved = self.garage / "real-tmp"
        (self.garage / "tmp").rename(moved)
        (self.garage / "tmp").symlink_to(moved, target_is_directory=True)
        self.run_helper("clean", "task-a", "--apply", success=False)
        self.assertTrue((moved / "task-a").is_dir())

    def test_hard_links_and_special_files_refused(self):
        task = self.create()
        self.complete()
        outside = self.base / "keep"
        outside.write_text("external")
        os.link(outside, task / "linked")
        self.run_helper("clean", "task-a", "--apply", success=False)
        (task / "linked").unlink()
        os.mkfifo(task / "fifo")
        self.run_helper("clean", "task-a", "--apply", success=False)
        self.assertEqual(outside.read_text(), "external")

    def test_uninstalled_or_symlinked_helper_refused(self):
        self.run_helper("create", "task-a", script=SOURCE_HELPER, success=False)
        alias = self.base / "alias"
        alias.symlink_to(self.garage, target_is_directory=True)
        self.run_helper("create", "task-a", script=alias / "support/workspace_scratch.py", success=False)
        self.assertFalse((self.garage / "tmp/task-a").exists())

    def test_changed_and_replaced_paths_after_inventory_are_not_followed(self):
        task = self.create()
        child = task / "child"
        child.mkdir()
        (child / "keep").write_text("original")
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "keep").write_text("external")
        with helper.open_absolute_directory(task) as fd:
            entries = helper.inventory(fd, os.fstat(fd).st_dev)
            child.rename(task / "retained")
            child.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(helper.Refusal):
                helper.remove_inventory(fd, entries)
        self.assertEqual((outside / "keep").read_text(), "external")
        self.assertEqual((task / "retained/keep").read_text(), "original")

    def test_changed_file_and_new_entries_are_preserved(self):
        task = self.create()
        file = task / "data"
        file.write_text("old")
        with helper.open_absolute_directory(task) as fd:
            entries = helper.inventory(fd, os.fstat(fd).st_dev)
            file.write_text("new data")
            with self.assertRaises(helper.Refusal):
                helper.remove_inventory(fd, entries)
        self.assertEqual(file.read_text(), "new data")
        with helper.open_absolute_directory(task) as fd:
            entries = helper.inventory(fd, os.fstat(fd).st_dev)
            (task / "late").write_text("new arrival")
            with self.assertRaises(helper.Refusal):
                helper.remove_inventory(fd, entries)
        self.assertEqual((task / "late").read_text(), "new arrival")
        self.assertTrue((task / helper.MARKER).is_file())
        with self.assertRaises(OSError):
            task.rmdir()

    def test_repository_at_scratch_root_refused(self):
        (self.garage / "tmp/.git").mkdir()
        self.run_helper("create", "task-a", success=False)
        self.assertFalse((self.garage / "tmp/task-a").exists())

    def test_real_worktrees_use_separate_app_namespaces_and_git_owners(self):
        def git(repo, *args):
            return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()
        for app_name in ("reporter", "consumer"):
            app = self.garage / "apps" / app_name
            app.mkdir()
            git(app, "init", "--quiet", "--template=")
            (app / "code.txt").write_text(app_name)
            git(app, "add", "code.txt")
            git(app, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "--quiet", "-m", "fixture")
            worktree = self.garage / ".worktrees" / app_name / "task-a"
            worktree.parent.mkdir()
            git(app, "worktree", "add", "--quiet", "--detach", str(worktree))
            self.assertEqual(git(worktree, "rev-parse", "--show-toplevel"), str(worktree))
            common = git(worktree, "rev-parse", "--git-common-dir")
            self.assertEqual((worktree / common).resolve(), app / ".git")
            self.assertEqual((worktree / "code.txt").read_text(), app_name)
            git(self.garage, "check-ignore", "-q", str(worktree / "code.txt"))
            (worktree / "code.txt").write_text("dirty work")
            self.run_helper("clean", f"../.worktrees/{app_name}/task-a", "--apply", success=False)
            self.assertEqual((worktree / "code.txt").read_text(), "dirty work")
        git(self.garage, "add", ".")
        self.assertEqual(set(git(self.garage, "ls-files").splitlines()),
                         {".gitignore", "AGENTS.md", "README.md", "support/workspace_scratch.py"})


if __name__ == "__main__":
    unittest.main()
