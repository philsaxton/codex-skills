"""Connector-shaped fixtures only; these tests never contact GitHub."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_garage_rebuild as git_fixture

SCRIPT = Path(__file__).with_name("garage_workspace.py")


class ConnectorTests(unittest.TestCase):
    git = git_fixture.GarageTests.git

    def setUp(self):
        git_fixture.GarageTests.setUp(self)
        self.git(self.repo, "remote", "set-url", "origin", "https://github.com/example/demo.git")
        self.selection["repositories"][0]["origin"] = "https://github.com/example/demo.git"
        self.bundle_path = self.root / "connector-sources.json"

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
                         "--out", self.snapshot, ok=ok)

    def raw_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args])

    def make_bundle(self):
        snapshots = []
        references = []
        seen = set()
        for branch in self.selection["repositories"][0]["branches"]:
            commit = self.git(self.repo, "rev-parse", branch["name"]).strip()
            references.append({"repository": "example/demo", "ref": branch["remote_ref"],
                               "observed_commit": commit, "observed_at": "2026-10-06T13:00:00Z"})
            if commit in seen:
                continue
            seen.add(commit)
            tree_sha = self.git(self.repo, "rev-parse", commit + "^{tree}").strip()
            trees, blobs = {}, {}
            def walk(tree_id):
                if tree_id in trees:
                    return
                entries = []
                trees[tree_id] = {"sha": tree_id, "truncated": False, "tree": entries}
                for record in self.raw_git("ls-tree", "-z", tree_id).split(b"\0"):
                    if not record:
                        continue
                    meta, name = record.split(b"\t", 1)
                    mode, kind, oid = meta.decode().split(" ")
                    entries.append({"path": name.decode(), "mode": mode, "type": kind, "sha": oid})
                    if kind == "tree":
                        walk(oid)
                    else:
                        data = self.raw_git("cat-file", "blob", oid)
                        blobs[oid] = {"sha": oid, "encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)}
            walk(tree_sha)
            snapshots.append({"repository": "example/demo", "requested_commit": commit,
                              "retrieved_at": "2026-10-06T13:00:00Z",
                              "commit": {"sha": commit, "tree": {"sha": tree_sha}},
                              "trees": list(trees.values()), "blobs": list(blobs.values())})
        return {"version": 1, "provider": "github_connector", "snapshots": snapshots, "references": references}

    def save_bundle(self, bundle=None):
        bundle = self.make_bundle() if bundle is None else bundle
        self.bundle_path.write_text(json.dumps(bundle))
        return bundle

    def bootstrap(self, ok=True, restore_private=False):
        extra = ["--restore-private"] if restore_private else []
        return self.call("bootstrap", "--snapshot", self.snapshot, "--sources", self.bundle_path,
                         "--target", self.target, *extra, ok=ok)

    def verify(self, ok=True):
        return self.call("verify", "--snapshot", self.snapshot, "--target", self.target, ok=ok)

    def test_export_does_not_require_remote_access(self):
        self.export()
        manifest = json.loads((self.snapshot / "manifest.json").read_text())
        self.assertEqual(manifest["mode"], "source_snapshot")
        self.assertEqual(manifest["repositories"][0]["remote_verification"], "pending_connector")

    def test_source_snapshot_has_exact_files_and_no_git(self):
        self.export()
        self.save_bundle()
        result = self.bootstrap()
        self.assertIn("source snapshot", result.stdout)
        self.assertFalse((self.target / "apps/demo/.git").exists())
        self.assertEqual((self.target / "apps/demo/file.txt").read_text(), "draft checkpoint\n")
        self.verify()

    def test_advancing_ref_does_not_replace_recorded_checkpoint(self):
        self.export()
        bundle = self.make_bundle()
        bundle["references"][0]["observed_commit"] = "a" * 40
        self.save_bundle(bundle)
        result = self.bootstrap()
        self.assertIn("moved", result.stdout)
        self.assertEqual((self.target / "apps/demo/file.txt").read_text(), "draft checkpoint\n")

    def test_missing_blob_refused_before_target_creation(self):
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"][0]["blobs"] = []
        self.save_bundle(bundle)
        result = self.bootstrap(ok=False)
        self.assertIn("missing blob", result.stderr)
        self.assertFalse(self.target.exists())

    def test_truncated_tree_refused(self):
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"][0]["trees"][0]["truncated"] = True
        self.save_bundle(bundle)
        result = self.bootstrap(ok=False)
        self.assertIn("truncated", result.stderr)

    def test_blob_hash_mismatch_refused(self):
        self.export()
        bundle = self.make_bundle()
        blob = bundle["snapshots"][0]["blobs"][0]
        blob["content"] = base64.b64encode(b"different content").decode()
        blob["size"] = len(b"different content")
        self.save_bundle(bundle)
        self.assertIn("blob hash", self.bootstrap(ok=False).stderr)

    def test_tree_hash_mismatch_refused(self):
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"][0]["trees"][0]["tree"][0]["path"] = "renamed.txt"
        self.save_bundle(bundle)
        self.assertIn("tree hash", self.bootstrap(ok=False).stderr)

    def test_wrong_commit_binding_refused(self):
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"][0]["commit"]["sha"] = "b" * 40
        self.save_bundle(bundle)
        self.assertIn("commit", self.bootstrap(ok=False).stderr)

    def test_binary_executable_and_contained_symlink_preserved(self):
        (self.repo / "tool").write_bytes(b"\x00\xffbinary\n")
        (self.repo / "tool").chmod(0o755)
        (self.repo / "tool-link").symlink_to("tool")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "binary executable and link")
        self.export()
        self.save_bundle()
        self.bootstrap()
        self.assertEqual((self.target / "apps/demo/tool").read_bytes(), b"\x00\xffbinary\n")
        self.assertTrue((self.target / "apps/demo/tool").stat().st_mode & 0o111)
        self.assertEqual(os.readlink(self.target / "apps/demo/tool-link"), "tool")
        self.verify()

    def test_escaping_app_symlink_refused(self):
        (self.repo / "escape").symlink_to("../../../outside")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "unsafe fixture link")
        self.export()
        self.save_bundle()
        result = self.bootstrap(ok=False)
        self.assertIn("symlink", result.stderr)
        self.assertFalse(self.target.exists())

    def test_all_selected_commits_required(self):
        self.selection["repositories"][0]["branches"].append({"name": "main", "remote_ref": "refs/heads/main"})
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"] = bundle["snapshots"][:1]
        self.save_bundle(bundle)
        self.assertIn("checkpoint inventory", self.bootstrap(ok=False).stderr)

    def test_modified_materialized_source_detected(self):
        self.export()
        self.save_bundle()
        self.bootstrap()
        (self.target / "apps/demo/file.txt").write_text("modified")
        self.assertIn("integrity", self.verify(ok=False).stderr)

    def test_existing_target_refused(self):
        self.export()
        self.save_bundle()
        self.target.mkdir()
        (self.target / "sentinel").write_text("keep")
        self.assertIn("already exists", self.bootstrap(ok=False).stderr)
        self.assertEqual((self.target / "sentinel").read_text(), "keep")

    def test_nested_trees_and_line_wrapped_base64_are_verified(self):
        (self.repo / "a").mkdir()
        (self.repo / "a/sub.txt").write_text("nested data\n" * 15)
        (self.repo / "a.txt").write_text("sorts before directory a")
        (self.repo / "a0.txt").write_text("sorts after directory a")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "nested sorting fixture")
        self.export()
        bundle = self.make_bundle()
        for blob in bundle["snapshots"][0]["blobs"]:
            value = blob["content"]
            blob["content"] = "\n".join(value[i:i + 60] for i in range(0, len(value), 60)) + "\n"
        self.save_bundle(bundle)
        self.bootstrap()
        self.assertEqual((self.target / "apps/demo/a/sub.txt").read_text(), "nested data\n" * 15)
        self.verify()

    def test_missing_nested_tree_refused(self):
        (self.repo / "nested").mkdir()
        (self.repo / "nested/file").write_text("content")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "nested tree")
        self.export()
        bundle = self.make_bundle()
        bundle["snapshots"][0]["trees"] = bundle["snapshots"][0]["trees"][:1]
        self.save_bundle(bundle)
        self.assertIn("missing tree", self.bootstrap(ok=False).stderr)

    def test_extra_blob_refused(self):
        self.export()
        bundle = self.make_bundle()
        data = b"extra object"
        blob_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        bundle["snapshots"][0]["blobs"].append({"sha": blob_sha, "encoding": "base64", "content": base64.b64encode(data).decode(), "size": len(data)})
        self.save_bundle(bundle)
        self.assertIn("extra unused", self.bootstrap(ok=False).stderr)

    def test_added_git_identity_at_workspace_root_is_refused(self):
        self.export()
        self.save_bundle()
        self.bootstrap()
        (self.target / ".git").mkdir()
        self.assertIn("inventory", self.verify(ok=False).stderr)

    def test_symlink_dotdot_is_resolved_in_filesystem_order(self):
        (self.repo / "d").mkdir()
        (self.repo / "other").mkdir()
        (self.repo / "d/keep").write_text("keep directory")
        (self.repo / "other/keep").write_text("keep directory")
        (self.repo / "safe").write_text("must stay in repository")
        (self.repo / "d/link").symlink_to("../other")
        (self.repo / "escape-via-dotdot").symlink_to("d/link/../../safe")
        self.git(self.repo, "add", ".")
        self.git(self.repo, "commit", "-m", "symlink traversal fixture")
        self.export()
        self.save_bundle()
        result = self.bootstrap(ok=False)
        self.assertIn("symlink", result.stderr)
        self.assertFalse(self.target.exists())

    def test_dot_tree_entry_refused_before_target_creation(self):
        self.export()
        bundle = self.make_bundle()
        snapshot = bundle["snapshots"][0]
        tree = snapshot["trees"][0]
        entry = tree["tree"][0]
        entry["path"] = "."
        data = entry["mode"].encode() + b" .\0" + bytes.fromhex(entry["sha"])
        new_tree = hashlib.sha1(b"tree " + str(len(data)).encode() + b"\0" + data).hexdigest()
        tree["sha"] = new_tree
        snapshot["commit"]["tree"]["sha"] = new_tree
        self.save_bundle(bundle)
        result = self.bootstrap(ok=False)
        self.assertIn("path", result.stderr)
        self.assertFalse(self.target.exists())

    def test_stored_bundle_bytes_are_rechecked_before_success(self):
        from argparse import Namespace
        from unittest.mock import patch
        import garage_workspace
        self.export()
        self.save_bundle()
        original = Path.write_bytes
        def corrupt_bundle(path, data):
            return original(path, data + b" " if path.name == garage_workspace.BUNDLE_NAME else data)
        args = Namespace(snapshot=str(self.snapshot), sources=str(self.bundle_path), target=str(self.target))
        with self.assertRaisesRegex(garage_workspace.core.Refusal, "stored source bundle"):
            with patch.object(Path, "write_bytes", corrupt_bundle):
                garage_workspace.bootstrap(args)
        self.assertTrue((self.target / ".incomplete").exists())

    def prepare_private_mapping(self):
        (self.repo / ".gitignore").write_text("source-material/private/\n")
        self.git(self.repo, "add", ".gitignore")
        self.git(self.repo, "commit", "-m", "portable private input ignore")
        private = self.repo / "source-material/private/extracts"
        private.mkdir(parents=True)
        (private / "chapter.txt").write_text("Synthetic private extract\n")
        self.selection["private_include"] = ["apps/demo/source-material/private"]
        self.selection["private_restore"] = [{"source": "apps/demo/source-material/private",
                                                "destination": "apps/demo/source-material/private"}]

    def test_private_ignored_subdirectory_restores_and_verifies(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        restored = self.target / "apps/demo/source-material/private/extracts/chapter.txt"
        self.assertEqual(restored.read_text(), "Synthetic private extract\n")
        self.verify()

    def test_private_mapping_without_opt_in_remains_staged(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap()
        self.assertFalse((self.target / "apps/demo/source-material/private").exists())
        self.assertTrue((self.target / ".garage-private/apps/demo/source-material/private/extracts/chapter.txt").is_file())
        self.verify()

    def test_private_restore_cannot_overwrite_tracked_file(self):
        self.prepare_private_mapping()
        self.selection["private_restore"] = [{"source": "apps/demo/source-material/private/extracts/chapter.txt",
                                                "destination": "apps/demo/file.txt"}]
        self.export()
        self.save_bundle()
        result = self.bootstrap(restore_private=True, ok=False)
        self.assertIn("tracked", result.stderr)
        self.assertFalse(self.target.exists())

    def test_private_restore_requires_tracked_ignore_rule(self):
        self.prepare_private_mapping()
        self.selection["private_restore"][0]["destination"] = "apps/demo/not-ignored"
        self.export()
        self.save_bundle()
        result = self.bootstrap(restore_private=True, ok=False)
        self.assertIn("ignored", result.stderr)
        self.assertFalse(self.target.exists())

    def test_external_global_ignore_cannot_authorize_overlay(self):
        from unittest.mock import patch
        self.prepare_private_mapping()
        self.selection["private_restore"][0]["destination"] = "apps/demo/not-ignored"
        config = self.root / "external-config/git"
        config.mkdir(parents=True)
        (config / "ignore").write_text("not-ignored/\n")
        self.export()
        self.save_bundle()
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(config.parent)}):
            result = self.bootstrap(restore_private=True, ok=False)
        self.assertIn("ignored", result.stderr)
        self.assertFalse(self.target.exists())

    def test_private_restore_cannot_traverse_tracked_symlink(self):
        self.prepare_private_mapping()
        (self.repo / "redirect").symlink_to("source-material")
        (self.repo / "source-material/README.md").write_text("Tracked source notes")
        self.git(self.repo, "add", "redirect", "source-material/README.md")
        self.git(self.repo, "commit", "-m", "tracked link")
        self.selection["private_restore"][0]["destination"] = "apps/demo/redirect/private"
        self.export()
        self.save_bundle()
        result = self.bootstrap(restore_private=True, ok=False)
        self.assertIn("tracked", result.stderr)
        self.assertFalse(self.target.exists())

    def test_private_overlay_tampering_is_detected(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        (self.target / "apps/demo/source-material/private/extracts/chapter.txt").write_text("tampered")
        self.assertIn("integrity", self.verify(ok=False).stderr)

    def test_private_overlay_does_not_allow_unlisted_ignored_files(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        (self.target / "apps/demo/source-material/private/extra.txt").write_text("not inventoried")
        self.assertIn("inventory", self.verify(ok=False).stderr)

    def prepare_nested_ignore_rules(self):
        self.prepare_private_mapping()
        (self.repo / ".gitignore").write_text("")
        (self.repo / "source-material/.gitignore").write_text("private/extracts/*.txt\n!private/extracts/public.txt\n")
        self.git(self.repo, "add", ".gitignore", "source-material/.gitignore")
        self.git(self.repo, "commit", "-m", "nested ignore and negation")

    def test_nested_checkpoint_ignore_rules_authorize_exact_file(self):
        self.prepare_nested_ignore_rules()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        self.verify()

    def test_nested_ignore_negation_refuses_private_destination(self):
        self.prepare_nested_ignore_rules()
        self.selection["private_restore"] = [{"source": "apps/demo/source-material/private/extracts/chapter.txt",
                                                "destination": "apps/demo/source-material/private/extracts/public.txt"}]
        self.export()
        self.save_bundle()
        self.assertIn("ignored", self.bootstrap(restore_private=True, ok=False).stderr)
        self.assertFalse(self.target.exists())

    def test_overlapping_private_mapping_destinations_refused(self):
        self.prepare_private_mapping()
        self.selection["private_restore"].append({"source": "apps/demo/source-material/private/extracts/chapter.txt",
                                                   "destination": "apps/demo/source-material/private/extra.txt"})
        self.assertIn("overlapping", self.export(ok=False).stderr)
        self.assertFalse(self.snapshot.exists())

    def test_private_destination_case_alias_of_tracked_directory_refused(self):
        self.prepare_private_mapping()
        (self.repo / "source-material/README.md").write_text("tracked source notes")
        self.git(self.repo, "add", "source-material/README.md")
        self.git(self.repo, "commit", "-m", "tracked directory")
        self.selection["private_restore"][0]["destination"] = "apps/demo/SOURCE-MATERIAL/private"
        self.export()
        self.save_bundle()
        self.assertIn("collision", self.bootstrap(restore_private=True, ok=False).stderr)
        self.assertFalse(self.target.exists())

    def test_private_symlink_overlay_is_refused(self):
        self.prepare_private_mapping()
        (self.repo / "source-material/private/extracts/link").symlink_to("chapter.txt")
        self.assertIn("symlink private", self.export(ok=False).stderr)
        self.assertFalse(self.snapshot.exists())

    def test_unselected_private_mapping_source_refused(self):
        self.prepare_private_mapping()
        self.selection["private_restore"][0]["source"] = "unselected.pdf"
        self.assertIn("not selected", self.export(ok=False).stderr)
        self.assertFalse(self.snapshot.exists())

    def test_private_receipt_cannot_expand_allowed_overlay(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        path = self.target / ".garage-recovery.json"
        receipt = json.loads(path.read_text())
        receipt["private_overlay"]["files"][0]["path"] = "apps/demo/source-material/private/unapproved.txt"
        path.write_text(json.dumps(receipt))
        self.assertIn("receipt", self.verify(ok=False).stderr)

    def test_tracked_source_tamper_still_fails_with_private_overlay(self):
        self.prepare_private_mapping()
        self.export()
        self.save_bundle()
        self.bootstrap(restore_private=True)
        (self.target / "apps/demo/file.txt").write_text("not the tracked checkpoint")
        self.assertIn("integrity", self.verify(ok=False).stderr)

    def test_older_staging_receipt_without_overlay_field_still_verifies(self):
        self.export()
        self.save_bundle()
        self.bootstrap()
        path = self.target / ".garage-recovery.json"
        receipt = json.loads(path.read_text())
        receipt.pop("private_overlay")
        path.write_text(json.dumps(receipt))
        self.verify()

    def test_304_mib_private_file_streams_through_restore(self):
        from unittest.mock import patch
        from argparse import Namespace
        import garage_workspace
        self.prepare_private_mapping()
        large = self.repo / "source-material/private/large-synthetic.zip"
        with large.open("wb") as file:
            file.write(b"Synthetic sparse archive fixture, not a real ZIP\n")
            file.truncate(304 * 1024 * 1024)
        original = Path.read_bytes
        def forbid_whole_large_read(path):
            if path.name == large.name:
                raise AssertionError("large private file must not use read_bytes")
            return original(path)
        self.plan.write_text(json.dumps(self.selection))
        with patch.object(Path, "read_bytes", forbid_whole_large_read):
            result = garage_workspace.main(["export", "--source", str(self.source), "--selection", str(self.plan), "--out", str(self.snapshot)])
            self.assertEqual(result, 0)
            self.save_bundle()
            garage_workspace.bootstrap(Namespace(snapshot=str(self.snapshot), sources=str(self.bundle_path),
                                                target=str(self.target), restore_private=True))
        self.assertEqual((self.target / "apps/demo/source-material/private/large-synthetic.zip").stat().st_size,
                         304 * 1024 * 1024)
        self.verify()


if __name__ == "__main__":
    unittest.main(verbosity=2)
