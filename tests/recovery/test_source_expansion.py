"""Offline source-inventory limits; Git object identities are built independently."""
import base64
import copy
import hashlib
import json
import unittest

import garage_rebuild as core
import garage_workspace as source


def git_oid(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


class SourceExpansionTests(unittest.TestCase):
    def setUp(self):
        self.trees = []
        self.blobs = []
        self.file = self.blob(b"synthetic\n")

    def blob(self, data):
        oid = git_oid("blob", data)
        self.blobs.append({"sha": oid, "encoding": "base64", "content": base64.b64encode(data).decode(),
                           "size": len(data)})
        return oid

    def entry(self, name, oid=None, mode="100644"):
        return {"path": name, "sha": oid or self.file, "mode": mode,
                "type": "tree" if mode == "040000" else "blob"}

    def tree(self, entries):
        ordered = sorted(entries, key=lambda e: e["path"].encode() + (b"/" if e["type"] == "tree" else b""))
        wire = b"".join(str(int(e["mode"])).encode() + b" " + e["path"].encode() + b"\0" +
                        bytes.fromhex(e["sha"]) for e in ordered)
        oid = git_oid("tree", wire)
        self.trees.append({"sha": oid, "truncated": False, "tree": entries})
        return oid

    def snapshot(self, tree):
        return {"repository": "example/synthetic", "requested_commit": "a" * 40,
                "retrieved_at": "2026-10-07T00:00:00Z",
                "commit": {"sha": "a" * 40, "tree": {"sha": tree}},
                "trees": self.trees, "blobs": self.blobs}

    def flat_snapshot(self, count):
        return self.snapshot(self.tree([self.entry("file-" + str(i)) for i in range(count)]))

    def bundle(self, snapshot):
        second = copy.deepcopy(snapshot)
        second["requested_commit"] = second["commit"]["sha"] = "b" * 40
        snapshots = [snapshot, second]
        branches = [{"commit": item["requested_commit"], "remote_ref": "refs/heads/checkpoint-" + str(i)}
                    for i, item in enumerate(snapshots)]
        manifest = {"repositories": [{"github_repository": "example/synthetic", "branches": branches}]}
        bundle = {"version": 1, "provider": "github_connector", "snapshots": snapshots,
                  "references": [{"repository": "example/synthetic", "ref": b["remote_ref"],
                                  "observed_commit": b["commit"], "observed_at": "2026-10-07T00:00:00Z"}
                                 for b in branches]}
        return bundle, manifest

    def test_shared_subtrees_below_limit_preserve_every_path(self):
        leaf = self.tree([self.entry("file")])
        root = self.tree([self.entry("left", leaf, "040000"), self.entry("right", leaf, "040000")])
        result = source.validate_source_objects(self.snapshot(root))
        self.assertEqual([e["path"] for e in result["entries"]], ["left", "left/file", "right", "right/file"])
        self.assertEqual(result["bytes"], {"left/file": b"synthetic\n", "right/file": b"synthetic\n"})

    def test_exact_expanded_entry_limit_is_allowed(self):
        result = source.validate_source_objects(self.flat_snapshot(10_000))
        self.assertEqual(len(result["entries"]), 10_000)
        self.assertEqual(len(result["bytes"]), 10_000)

    def test_one_over_expanded_entry_limit_is_refused(self):
        with self.assertRaisesRegex(core.Refusal, "expanded source entry limit"):
            source.validate_source_objects(self.flat_snapshot(10_001))

    def test_compact_shared_tree_dag_is_refused(self):
        tree = self.tree([self.entry("file")])
        for _ in range(15):
            tree = self.tree([self.entry("left", tree, "040000"), self.entry("right", tree, "040000")])
        snapshot = self.snapshot(tree)
        self.assertLess(len(json.dumps(snapshot)), 10_000)
        with self.assertRaisesRegex(core.Refusal, "expanded source entry limit"):
            source.validate_source_objects(snapshot)

    def test_directories_and_symlinks_consume_the_same_budget(self):
        empty = self.tree([])
        link = self.blob(b"file")
        entries = [self.entry("file")]
        entries += [self.entry("dir-" + str(i), empty, "040000") for i in range(4_999)]
        entries += [self.entry("link-" + str(i), link, "120000") for i in range(5_000)]
        snapshot = self.snapshot(self.tree(entries))
        self.assertEqual(len(source.validate_source_objects(snapshot)["entries"]), 10_000)
        self.trees.pop()
        snapshot = self.snapshot(self.tree(entries + [self.entry("one-more-link", link, "120000")]))
        with self.assertRaisesRegex(core.Refusal, "expanded source entry limit"):
            source.validate_source_objects(snapshot)

    def test_bundle_combined_entry_limit_is_allowed(self):
        sources, _ = source.validate_bundle(*self.bundle(self.flat_snapshot(5_000)))
        self.assertEqual(sum(len(item["entries"]) for item in sources.values()), 10_000)

    def test_bundle_repeated_paths_cannot_reset_the_entry_budget(self):
        with self.assertRaisesRegex(core.Refusal, "expanded source entry limit"):
            source.validate_bundle(*self.bundle(self.flat_snapshot(5_001)))

    def test_budget_is_checked_before_resolving_the_next_tree(self):
        entries = [self.entry("file-" + str(i)) for i in range(10_000)]
        entries.append(self.entry("unvisited", "c" * 40, "040000"))
        # The unreachable missing tree distinguishes a traversal guard from a
        # check performed only after the complete inventory has been built.
        with self.assertRaisesRegex(core.Refusal, "expanded source entry limit"):
            source.validate_source_objects(self.snapshot(self.tree(entries)))

    def test_virtual_case_colliding_files_are_refused_on_every_filesystem(self):
        tree = self.tree([self.entry("Notes"), self.entry("notes")])
        with self.assertRaisesRegex(core.Refusal, "collision"):
            source.validate_source_objects(self.snapshot(tree))

    def test_virtual_case_colliding_ancestors_are_refused_on_every_filesystem(self):
        leaf = self.tree([self.entry("file")])
        root = self.tree([self.entry("Foo", leaf, "040000"), self.entry("foo", leaf, "040000")])
        with self.assertRaisesRegex(core.Refusal, "collision"):
            source.validate_source_objects(self.snapshot(root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
