from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_HELPER = ROOT / "workspace-scratch/scripts/workspace_scratch.py"
spec = importlib.util.spec_from_file_location("scratch_helper", SOURCE_HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class WorkspaceScratchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="garage scratch ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.garage = self.base / "garage with spaces"
        self.garage.mkdir()
        for name in ("tmp", "artifacts", "apps", ".worktrees"):
            (self.garage / name).mkdir()
        self.script = SOURCE_HELPER

    def run_helper(self, *args, success=True, script=None, workspace=None, env=None):
        p = subprocess.run([sys.executable, str(script or self.script), "--workspace", str(workspace or self.garage), *args],
                           cwd=self.base, env=env, capture_output=True, text=True)
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

    def test_run_routes_temporary_output_preserving_cwd_streams_and_arguments(self):
        task = self.create()
        marker = (task / helper.MARKER).read_bytes()
        code = """import json, os, sys, tempfile
from pathlib import Path
f = tempfile.NamedTemporaryFile(delete=False)
f.write(sys.stdin.buffer.read())
f.close()
print(json.dumps({'temp': f.name, 'cwd': os.getcwd(), 'args': sys.argv[1:],
                  'env': {k: os.environ[k] for k in ('TMPDIR', 'TMP', 'TEMP', 'SCRATCH_TEST_VALUE')}}))
print('child stderr', file=sys.stderr)
"""
        literal = ["two words", "$(touch should-not-exist)", ";", "--apply", "--workspace", "--"]
        env = {**os.environ, "SCRATCH_TEST_VALUE": "inherited",
               "TMPDIR": str(self.base), "TMP": str(self.base), "TEMP": str(self.base)}
        p = subprocess.run([sys.executable, str(self.script), "--workspace", str(self.garage),
                            "run", "task-a", "--", sys.executable, "-c", code, *literal],
                           cwd=self.base, env=env, input="child stdin", capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(Path(data["temp"]).parent, task)
        self.assertEqual(Path(data["temp"]).read_text(), "child stdin")
        self.assertEqual(Path(data["cwd"]), self.base)
        self.assertEqual(data["args"], literal)
        self.assertEqual(data["env"], {"TMPDIR": str(task), "TMP": str(task),
                                      "TEMP": str(task), "SCRATCH_TEST_VALUE": "inherited"})
        self.assertEqual(p.stderr, "child stderr\n")
        self.assertFalse((self.base / "should-not-exist").exists())
        self.assertEqual(env["TMPDIR"], str(self.base))
        self.assertEqual((task / helper.MARKER).read_bytes(), marker)

    def test_run_preserves_exit_status_and_active_task_on_failure(self):
        task = self.create()
        marker = (task / helper.MARKER).read_bytes()
        for code, expected in (("raise SystemExit(23)", 23),
                               ("import os, signal; os.kill(os.getpid(), signal.SIGTERM)", -signal.SIGTERM)):
            with self.subTest(code=code):
                p = self.run_helper("run", "task-a", "--", sys.executable, "-c", code, success=False)
                self.assertEqual(p.returncode, expected)
                self.assertEqual((task / helper.MARKER).read_bytes(), marker)
        self.run_helper("run", "task-a", "--", str(self.base / "missing-executable"), success=False)
        self.assertEqual((task / helper.MARKER).read_bytes(), marker)
        p = self.run_helper("run", "task-a", "--", "/bin/sh", "-c",
                            "kill -PIPE $$; exit 99", success=False)
        self.assertEqual(p.returncode, -signal.SIGPIPE)

    def test_run_requires_active_marked_task_and_does_not_launch_on_refusal(self):
        task = self.create()
        self.complete()
        (self.garage / "tmp/unmarked").mkdir()
        (self.garage / "tmp/alias").symlink_to(task, target_is_directory=True)
        code = "from pathlib import Path; Path('launched').touch()"
        for name in ("task-a", "missing", "unmarked", "alias", "../artifacts"):
            with self.subTest(task=name):
                self.run_helper("run", name, "--", sys.executable, "-c", code, success=False)
        self.assertFalse((self.base / "launched").exists())
        self.assertFalse((self.garage / "tmp/missing").exists())
        self.assertEqual(json.loads((task / helper.MARKER).read_text())["state"], "complete")

    def test_command_separator_and_apply_are_validated_before_mutation(self):
        for args in (("run", "task-a"), ("run", "task-a", "--"),
                     ("run", "task-a", sys.executable),
                     ("create", "task-a", "--", sys.executable),
                     ("create", "task-a", "--"),
                     ("run", "task-a", "--apply", "--", sys.executable),
                     ("inspect", "task-a", "--apply")):
            with self.subTest(args=args):
                self.run_helper(*args, success=False)
        self.assertEqual(list((self.garage / "tmp").iterdir()), [])

    def test_inspection_and_preview_show_complete_inventory_without_mutation(self):
        task = self.create()
        (task / "empty dir").mkdir()
        nested = task / "nested"
        nested.mkdir()
        unusual = 'quote"\n\t\x1b[31m.txt'
        (nested / unusual).write_bytes(b"private content")
        (task / ".hidden").write_bytes(b"\x00\x01")

        def check_inventory(action, state):
            before = {str(p.relative_to(task)): p.read_bytes()
                      for p in task.rglob("*") if p.is_file()}
            p = self.run_helper(action, "task-a")
            rows = [line.split("\t") for line in p.stdout.splitlines()
                    if line.startswith(("file\t", "dir\t"))]
            observed = {json.loads(path): (kind, size) for kind, size, path in rows}
            expected = {path: ("file", str(len(data))) for path, data in before.items()}
            expected.update({"empty dir": ("dir", "-"), "nested": ("dir", "-")})
            self.assertEqual(observed, expected)
            self.assertIn(f"State: {state}\n", p.stdout)
            self.assertIn(f"Total: 3 files, 2 directories, {sum(map(len, before.values()))} bytes\n", p.stdout)
            self.assertNotIn("private content", p.stdout)
            self.assertNotIn("\x1b", p.stdout)
            self.assertEqual(before, {str(p.relative_to(task)): p.read_bytes()
                                      for p in task.rglob("*") if p.is_file()})

        check_inventory("inspect", "active")
        self.run_helper("clean", "task-a", success=False)
        self.complete()
        check_inventory("inspect", "complete")
        check_inventory("clean", "complete")
        self.run_helper("clean", "task-a", "--apply")
        self.assertFalse(task.exists())

    def test_run_uses_inherited_path_to_find_executable(self):
        task = self.create()
        bin_dir = self.base / "bin with spaces"
        bin_dir.mkdir()
        executable = bin_dir / "scratch-fixture"
        executable.write_text('#!/bin/sh\nprintf "%s\\n" "$TMPDIR" "$TMP" "$TEMP" "$PWD" "$1"\n'
                              'printf "fixture stderr\\n" >&2\nexit 19\n')
        executable.chmod(0o700)
        env = {**os.environ, "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", "")}
        p = self.run_helper("run", "task-a", "--", "scratch-fixture", "two words", env=env, success=False)
        self.assertEqual(p.returncode, 19)
        self.assertEqual(p.stdout.splitlines(), [str(task)] * 3 + [str(self.base), "two words"])
        self.assertEqual(p.stderr, "fixture stderr\n")

    def test_run_allows_existing_artifacts_while_inspection_and_cleanup_refuse_them(self):
        task = self.create()
        nested = task / "nested"
        nested.mkdir()
        name = 'link\n\x1b[31m'
        (nested / name).symlink_to(self.base, target_is_directory=True)
        p = self.run_helper("inspect", "task-a", success=False)
        self.assertIn("symlink", p.stderr)
        self.assertIn(json.dumps("nested/" + name), p.stderr)
        self.assertNotIn("\x1b", p.stderr)
        self.run_helper("run", "task-a", "--", sys.executable, "-c",
                        "from pathlib import Path; Path('launched').touch()")
        self.assertTrue((self.base / "launched").is_file())
        self.run_helper("complete", "task-a", success=False)
        (nested / name).unlink()
        self.complete()
        (nested / name).symlink_to(self.base, target_is_directory=True)
        for action in (("inspect", "task-a"), ("clean", "task-a"), ("clean", "task-a", "--apply")):
            p = self.run_helper(*action, success=False)
            self.assertIn(json.dumps("nested/" + name), p.stderr)
            self.assertTrue((nested / name).is_symlink())
        self.assertTrue((self.base / "launched").is_file())

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

    def test_explicit_workspace_required_and_unsafe_roots_refused(self):
        p = subprocess.run([sys.executable, str(self.script), "create", "task-a"],
                           cwd=self.garage, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        for workspace in (".", "/", str(self.garage / ".." / self.garage.name),
                          str(self.base / "missing")):
            with self.subTest(workspace=workspace):
                self.run_helper("create", "task-a", workspace=workspace, success=False)
        alias = self.base / "alias"
        alias.symlink_to(self.garage, target_is_directory=True)
        self.run_helper("create", "task-a", workspace=alias, success=False)
        self.assertFalse((self.garage / "tmp/task-a").exists())

    def test_external_installation_and_multiple_workspaces_are_independent(self):
        alias = self.base / "installed-helper.py"
        alias.symlink_to(self.script)
        other = self.base / "other workspace"
        (other / "tmp").mkdir(parents=True)
        self.run_helper("create", "same-task", script=alias)
        self.run_helper("create", "same-task", workspace=other)
        self.run_helper("complete", "same-task", workspace=other)
        self.run_helper("clean", "same-task", "--apply", workspace=other)
        self.assertTrue((self.garage / "tmp/same-task").is_dir())
        self.assertFalse((other / "tmp/same-task").exists())
        self.assertFalse((self.garage / "support").exists())

    def test_existing_version_one_marker_remains_usable(self):
        task = self.garage / "tmp/legacy-task"
        task.mkdir()
        (task / helper.MARKER).write_text(json.dumps(
            {"version": 1, "task": "legacy-task", "state": "active"}))
        (task / "output.txt").write_text("disposable")
        self.run_helper("complete", "legacy-task")
        self.run_helper("clean", "legacy-task", "--apply")
        self.assertFalse(task.exists())

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
        git(self.garage, "init", "--quiet", "--template=")
        (self.garage / ".gitignore").write_text("/apps/\n/artifacts/\n/tmp/\n/.worktrees/\n")
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
                         {".gitignore"})


if __name__ == "__main__":
    unittest.main()
