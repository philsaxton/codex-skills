"""Behavior tests; all Git repositories and files are synthetic."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("garage_rebuild.py")


class GarageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="garage-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "AGENTS.md").write_text("Shared guidance\n")
        (self.source / "vendors/demo").mkdir(parents=True)
        (self.source / "vendors/demo/SKILL.md").write_text("Skill instructions\n")
        (self.source / ".agents/skills").mkdir(parents=True)
        (self.source / ".agents/skills/demo").symlink_to("../../vendors/demo")
        (self.source / "scripts").mkdir()
        (self.source / "scripts/setup.sh").write_text("#!/bin/sh\nexit 0\n")
        (self.source / "scripts/setup.sh").chmod(0o755)
        self.remote = self.root / "remote.git"
        self.git(self.root, "init", "--bare", str(self.remote))
        self.repo = self.source / "apps/demo"
        self.repo.mkdir(parents=True)
        self.git(self.repo, "init", "-b", "main")
        self.git(self.repo, "config", "user.name", "Fixture")
        self.git(self.repo, "config", "user.email", "fixture@example.invalid")
        (self.repo / "file.txt").write_text("base\n")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "base")
        self.git(self.repo, "remote", "add", "origin", str(self.remote))
        self.git(self.repo, "push", "-u", "origin", "main")
        self.git(self.repo, "checkout", "-b", "draft-work")
        (self.repo / "file.txt").write_text("draft checkpoint\n")
        self.git(self.repo, "commit", "-am", "draft checkpoint")
        self.git(self.repo, "push", "-u", "origin", "draft-work")
        self.sha = self.git(self.repo, "rev-parse", "HEAD").strip()
        self.selection = {
            "version": 1,
            "include": ["AGENTS.md", ".agents", "vendors", "scripts"],
            "exclude": [],
            "private_include": [],
            "repositories": [{"path": "apps/demo", "origin": str(self.remote),
                              "base_branch": "main", "checkout": "draft-work",
                              "branches": [{"name": "draft-work", "remote_ref": "refs/heads/draft-work",
                                            "pull_request": {"url": "https://github.com/example/demo/pull/1",
                                                             "state": "draft", "head_ref": "draft-work"}}],
                              "ignored_exclusions": []}],
            "notes": {"toolchain": "Python 3 and Git; fixture only"}}
        self.plan = self.root / "selection.json"
        self.snapshot = self.root / "snapshot"
        self.target = self.root / "rebuilt"

    def git(self, cwd, *args):
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                   GIT_TERMINAL_PROMPT="0")
        result = subprocess.run(["git", "-C", str(cwd), *args], env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def call(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def export(self, ok=True):
        self.plan.write_text(json.dumps(self.selection))
        return self.call("export", "--source", self.source, "--selection", self.plan,
                         "--out", self.snapshot, "--allow-local-origins", ok=ok)

    def bootstrap(self, ok=True):
        return self.call("bootstrap", "--snapshot", self.snapshot, "--target", self.target,
                         "--allow-local-origins", ok=ok)

    def rewrite_manifest(self, mutate):
        path = self.snapshot / "manifest.json"
        manifest = json.loads(path.read_text())
        mutate(manifest)
        path.write_text(json.dumps(manifest))
        (self.snapshot / "manifest.sha256").write_text(hashlib.sha256(path.read_bytes()).hexdigest() + "\n")

    def test_round_trip_restores_selected_draft_checkpoint(self):
        self.export()
        self.assertEqual(list((self.snapshot / "garage/apps").iterdir()), [])
        self.assertFalse((self.snapshot / "garage/apps/demo").exists())
        manifest = json.loads((self.snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["repositories"][0]["branches"][0]["commit"], self.sha)
        self.assertEqual(manifest["repositories"][0]["branches"][0]["pull_request"]["state"], "draft")
        self.bootstrap()
        self.assertEqual(self.git(self.target / "apps/demo", "rev-parse", "HEAD").strip(), self.sha)
        self.assertEqual((self.target / ".agents/skills/demo/SKILL.md").read_text(), "Skill instructions\n")
        self.assertTrue((self.target / "scripts/setup.sh").stat().st_mode & 0o111)
        self.call("verify", "--snapshot", self.snapshot, "--target", self.target, "--allow-local-origins")

    def test_advanced_remote_keeps_checkpoint_on_recovery_branch(self):
        self.export()
        (self.repo / "file.txt").write_text("newer remote content\n")
        self.git(self.repo, "commit", "-am", "advance")
        self.git(self.repo, "push", "origin", "draft-work")
        result = self.bootstrap()
        self.assertIn("moved", result.stdout)
        repo = self.target / "apps/demo"
        self.assertEqual(self.git(repo, "rev-parse", "HEAD").strip(), self.sha)
        self.assertEqual(self.git(repo, "branch", "--show-current").strip(), "recovery/draft-work")

    def test_unavailable_commit_refuses_restore(self):
        self.export()
        self.rewrite_manifest(lambda m: m["repositories"][0]["branches"][0].update(commit="1" * 40))
        result = self.bootstrap(ok=False)
        self.assertIn("unavailable checkpoint", result.stderr)
        self.assertTrue((self.target / ".incomplete").exists())

    def test_existing_target_is_untouched(self):
        self.export()
        self.target.mkdir()
        (self.target / "sentinel").write_text("keep")
        result = self.bootstrap(ok=False)
        self.assertIn("already exists", result.stderr)
        self.assertEqual((self.target / "sentinel").read_text(), "keep")
        self.assertEqual(len(list(self.target.iterdir())), 1)

    def test_existing_snapshot_is_untouched(self):
        self.export()
        before = (self.snapshot / "manifest.json").read_bytes()
        result = self.export(ok=False)
        self.assertIn("already exists", result.stderr)
        self.assertEqual((self.snapshot / "manifest.json").read_bytes(), before)

    def test_known_secret_names_are_excluded_and_reported(self):
        (self.source / "scripts/.env").write_text("PASSWORD=hidden")
        self.export()
        self.assertFalse((self.snapshot / "garage/scripts/.env").exists())
        self.assertIn("scripts/.env", (self.snapshot / "manifest.json").read_text())

    def test_private_key_content_refused(self):
        (self.source / "scripts/notes.txt").write_text("-----BEGIN OPENSSH PRIVATE KEY-----\nsecret")
        result = self.export(ok=False)
        self.assertIn("secret", result.stderr)

    def test_pdf_requires_private_selection(self):
        (self.source / "scripts/book.pdf").write_bytes(b"%PDF-1.7\nfixture")
        result = self.export(ok=False)
        self.assertIn("private_include", result.stderr)

    def test_private_pdf_stays_separate_and_hash_verified(self):
        (self.source / "book.pdf").write_bytes(b"%PDF-1.7\nfixture")
        self.selection["private_include"] = ["book.pdf"]
        self.export()
        self.bootstrap()
        self.assertFalse((self.target / "book.pdf").exists())
        self.assertEqual((self.target / ".garage-private/book.pdf").read_bytes(), b"%PDF-1.7\nfixture")
        self.call("verify", "--snapshot", self.snapshot, "--target", self.target, "--allow-local-origins")

    def test_escaping_symlink_refused(self):
        (self.source / "scripts/escape").symlink_to("../../outside")
        result = self.export(ok=False)
        self.assertIn("symlink", result.stderr)

    def test_unselected_symlink_target_refused(self):
        (self.source / "unselected.txt").write_text("outside selection")
        (self.source / "scripts/link").symlink_to("../unselected.txt")
        result = self.export(ok=False)
        self.assertIn("symlink", result.stderr)

    def test_dirty_application_refused(self):
        (self.repo / "file.txt").write_text("not committed")
        result = self.export(ok=False)
        self.assertIn("dirty", result.stderr)
        self.assertIn("apps/demo", result.stderr)

    def test_untracked_application_refused(self):
        (self.repo / "evidence.txt").write_text("unique evidence")
        result = self.export(ok=False)
        self.assertIn("dirty", result.stderr)

    def test_local_only_commit_refused(self):
        (self.repo / "file.txt").write_text("local only")
        self.git(self.repo, "commit", "-am", "unpublished")
        result = self.export(ok=False)
        self.assertIn("remote checkpoint differs", result.stderr)

    def test_ignored_inputs_require_explicit_handling(self):
        (self.repo / ".gitignore").write_text("build/\n")
        self.git(self.repo, "add", ".gitignore")
        self.git(self.repo, "commit", "-m", "ignore build")
        self.git(self.repo, "push", "origin", "draft-work")
        (self.repo / "build").mkdir()
        (self.repo / "build/generated.txt").write_text("rebuildable")
        result = self.export(ok=False)
        self.assertIn("unhandled ignored", result.stderr)

    def test_payload_corruption_detected(self):
        self.export()
        (self.snapshot / "garage/AGENTS.md").write_text("corrupted")
        result = self.bootstrap(ok=False)
        self.assertIn("integrity", result.stderr)
        self.assertFalse(self.target.exists())

    def test_extra_payload_detected(self):
        self.export()
        (self.snapshot / "garage/extra.txt").write_text("extra")
        result = self.call("verify", "--snapshot", self.snapshot, "--allow-local-origins", ok=False)
        self.assertIn("inventory", result.stderr)

    def test_manifest_checksum_detected(self):
        self.export()
        with (self.snapshot / "manifest.json").open("a") as file:
            file.write(" ")
        result = self.call("verify", "--snapshot", self.snapshot, ok=False)
        self.assertIn("manifest integrity", result.stderr)

    def test_manifest_path_traversal_refused_even_with_new_hash(self):
        self.export()
        self.rewrite_manifest(lambda m: m["files"][0].update(path="../../escape"))
        result = self.bootstrap(ok=False)
        self.assertIn("path", result.stderr)
        self.assertFalse((self.root / "escape").exists())

    def test_origin_credentials_refused(self):
        self.selection["repositories"][0]["origin"] = "https://token@example.invalid/repo.git"
        result = self.export(ok=False)
        self.assertIn("origin", result.stderr)
        self.assertNotIn("token@", result.stderr)

    def test_case_collision_refused(self):
        (self.source / "scripts/Notes").write_text("one")
        (self.source / "scripts/notes").write_text("two")
        result = self.export(ok=False)
        self.assertIn("collision", result.stderr)

    def test_reserved_garage_paths_refused(self):
        self.selection["include"].append("apps")
        result = self.export(ok=False)
        self.assertIn("reserved", result.stderr)

    def test_access_time_change_is_not_a_source_mutation(self):
        os.utime(self.source / "AGENTS.md", (1, 1))
        self.export()

    def test_assume_unchanged_cannot_hide_source_edits(self):
        self.git(self.repo, "update-index", "--assume-unchanged", "file.txt")
        (self.repo / "file.txt").write_text("unique hidden work")
        result = self.export(ok=False)
        self.assertIn("index flags", result.stderr)

    def test_skip_worktree_cannot_hide_target_edits(self):
        self.export()
        self.bootstrap()
        repo = self.target / "apps/demo"
        self.git(repo, "update-index", "--skip-worktree", "file.txt")
        (repo / "file.txt").write_text("hidden change")
        result = self.call("verify", "--snapshot", self.snapshot, "--target", self.target,
                           "--allow-local-origins", ok=False)
        self.assertIn("index flags", result.stderr)

    def test_case_insensitive_reserved_path_refused(self):
        (self.source / ".GARAGE-RECOVERY.JSON").write_text("must not be overwritten")
        self.selection["include"].append(".GARAGE-RECOVERY.JSON")
        result = self.export(ok=False)
        self.assertIn("reserved", result.stderr)

    def test_truncated_receipt_cannot_skip_branch_verification(self):
        self.selection["repositories"][0]["branches"].append({"name": "main", "remote_ref": "refs/heads/main"})
        self.export()
        self.bootstrap()
        self.git(self.target / "apps/demo", "branch", "-D", "main")
        receipt_path = self.target / ".garage-recovery.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["repositories"][0]["branches"] = []
        receipt_path.write_text(json.dumps(receipt))
        result = self.call("verify", "--snapshot", self.snapshot, "--target", self.target,
                           "--allow-local-origins", ok=False)
        self.assertIn("receipt branch", result.stderr)

    def test_worktree_config_is_rejected_before_filters_execute(self):
        self.git(self.repo, "config", "extensions.worktreeConfig", "true")
        (self.repo / ".git/config.worktree").write_text("[filter \"probe\"]\n    clean = touch SHOULD_NOT_RUN; cat\n")
        (self.repo / ".gitattributes").write_text("file.txt filter=probe\n")
        result = self.export(ok=False)
        self.assertIn("worktree", result.stderr)
        self.assertFalse((self.repo / "SHOULD_NOT_RUN").exists())

    def test_target_filter_config_is_rejected(self):
        self.export()
        self.bootstrap()
        repo = self.target / "apps/demo"
        self.git(repo, "config", "filter.probe.clean", "touch SHOULD_NOT_RUN; cat")
        result = self.call("verify", "--snapshot", self.snapshot, "--target", self.target,
                           "--allow-local-origins", ok=False)
        self.assertIn("configuration", result.stderr)
        self.assertFalse((repo / "SHOULD_NOT_RUN").exists())

    def test_implicit_ancestor_case_collision_refused(self):
        (self.source / "Foo").mkdir()
        (self.source / "foo").mkdir()
        (self.source / "Foo/bar").write_text("first")
        (self.source / "foo/baz").write_text("second")
        self.selection["include"] += ["Foo/bar", "foo/baz"]
        result = self.export(ok=False)
        self.assertIn("collision", result.stderr)

    def test_pdf_magic_requires_private_selection(self):
        (self.source / "scripts/manual.dat").write_bytes(b"%PDF-1.7\nfixture")
        result = self.export(ok=False)
        self.assertIn("private_include", result.stderr)

    def test_external_receipt_symlink_refused(self):
        self.export()
        self.bootstrap()
        receipt = self.target / ".garage-recovery.json"
        outside = self.root / "outside-receipt.json"
        outside.write_bytes(receipt.read_bytes())
        receipt.unlink()
        receipt.symlink_to(outside)
        result = self.call("verify", "--snapshot", self.snapshot, "--target", self.target,
                           "--allow-local-origins", ok=False)
        self.assertIn("receipt", result.stderr)

    def test_git_plaintext_credential_store_is_excluded(self):
        (self.source / ".git-credentials").write_text("https://user:fixture-password@example.invalid\n")
        self.selection["include"].append(".git-credentials")
        self.export()
        self.assertFalse((self.snapshot / "garage/.git-credentials").exists())

    def test_embedded_url_credentials_are_refused(self):
        (self.source / "scripts/notes.txt").write_text("https://user:fixture-password@example.invalid\n")
        result = self.export(ok=False)
        self.assertIn("secret", result.stderr)
        self.assertNotIn("fixture-password", result.stderr)

    def test_active_git_operation_is_not_a_clean_checkpoint(self):
        (self.repo / ".git/MERGE_HEAD").write_text(self.sha + "\n")
        result = self.export(ok=False)
        self.assertIn("in-progress", result.stderr)

    def test_submodule_is_refused_before_nested_filter_execution(self):
        self.git(self.repo, "-c", "protocol.file.allow=always", "submodule", "add", "-b", "main", str(self.remote), "child")
        child = self.repo / "child"
        self.git(child, "config", "user.name", "Fixture")
        self.git(child, "config", "user.email", "fixture@example.invalid")
        (child / ".gitattributes").write_text("file.txt filter=probe\n")
        self.git(child, "add", ".gitattributes")
        self.git(child, "commit", "-m", "nested attributes fixture")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "nested submodule fixture")
        self.git(child, "config", "filter.probe.clean", "touch SHOULD_NOT_RUN; cat")
        (child / "file.txt").write_text("edit\n")
        result = self.export(ok=False)
        self.assertFalse((child / "SHOULD_NOT_RUN").exists())
        self.assertIn("submodules", result.stderr)

    def test_full_git_mode_refuses_private_restore_mappings(self):
        self.selection["private_restore"] = [{"source": "private/input.zip", "destination": "apps/demo/private/input.zip"}]
        result = self.export(ok=False)
        self.assertIn("require garage_workspace.py", result.stderr)
        self.assertFalse(self.snapshot.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
