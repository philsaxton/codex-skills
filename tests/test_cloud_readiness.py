"""Synthetic, offline readiness cases. No user projects or runtime registration.

Each assertion detects a concrete change: trusting labels instead of bytes,
conflating optional inputs with builds, bypassing host/history/report gates, or
executing profile data. Fixtures compute Git objects independently of the helper.
"""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "workspace-setup/scripts/check_cloud_readiness.py"
DEPENDENCY = os.environ.get("GARAGE_RECOVERY_DEPENDENCY", str(ROOT / "workspace-setup/scripts/recovery"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_oid(kind, data):
    return hashlib.sha1(kind.encode() + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return sha(raw)


def requirements(**changes):
    return {"skills": [], "tools": [], "inputs": [], "git": [], "files": [], "report_parents": [], **changes}


def inventory(root):
    return {p.relative_to(root).as_posix(): (p.lstat().st_mode, p.read_bytes() if p.is_file() and not p.is_symlink() else None)
            for p in root.rglob("*")}


class CloudReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cloud-readiness-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.app = self.root / "apps/sample"
        self.app.mkdir(parents=True)
        (self.root / "evidence").mkdir()
        (self.root / "reports").mkdir()
        (self.root / "private").mkdir()
        (self.root / "AGENTS.md").write_bytes(b"Synthetic governance\n")
        (self.root / "recipe.md").write_bytes(b"Synthetic recipe; review before execution.\n")
        (self.root / "control.json").write_bytes(b"{}\n")
        (self.app / "main.txt").write_bytes(b"Synthetic source\n")
        blob = git_oid("blob", (self.app / "main.txt").read_bytes())
        tree = git_oid("tree", b"100644 main.txt\0" + bytes.fromhex(blob))
        self.bundle = {
            "version": 1, "provider": "github_connector",
            "snapshots": [{"repository": "example/synthetic", "requested_commit": "a" * 40,
                           "retrieved_at": "2026-10-07T00:00:00Z",
                           "commit": {"sha": "a" * 40, "tree": {"sha": tree}},
                           "trees": [{"sha": tree, "truncated": False, "tree": [
                               {"path": "main.txt", "mode": "100644", "type": "blob", "sha": blob}]}],
                           "blobs": [{"sha": blob, "encoding": "base64", "size": 17,
                                      "content": base64.b64encode(b"Synthetic source\n").decode()}]}],
            "references": [{"repository": "example/synthetic", "ref": "refs/heads/reviewed-work",
                            "observed_commit": "a" * 40, "observed_at": "2026-10-07T00:00:00Z"}]}
        bundle_hash = write_json(self.root / "evidence/source.json", self.bundle)
        self.profile = {
            "version": 1, "id": "scope-like",
            "governance": [{"path": "AGENTS.md", "sha256": sha(b"Synthetic governance\n")}],
            "applications": [{"id": "sample", "path": "apps/sample", "repository": "example/synthetic",
                              "ref": "refs/heads/reviewed-work", "commit": "a" * 40, "tree": tree,
                              "bundle": {"path": "evidence/source.json", "sha256": bundle_hash}}],
            "skills": [{"id": "review-skill", "sha256": sha(b"Synthetic skill\n"), "resources": [
                {"path": "SKILL.md", "sha256": sha(b"Synthetic skill\n")},
                {"path": "references/review.md", "sha256": sha(b"Synthetic resource\n")}]}],
            "tools": [{"id": "python", "version": "3.12.0"}], "inputs": [], "private_manifest": None,
            "recipes": [{"id": "build", "path": "recipe.md", "sha256": sha(b"Synthetic recipe; review before execution.\n"),
                         "commands": ["python3 -m unittest"]}],
            "development": requirements(skills=["review-skill"], tools=["python"]),
            "groups": [{"id": "build", "optional": False, "recipe": "build", "requires": requirements()}]}
        self.observations = {}
        self.save()

    def save(self, *, fresh_host=True):
        digest = write_json(self.root / "workspace-setup.json", self.profile)
        if fresh_host:
            now = datetime.now(timezone.utc)
            self.observations = {
                "version": 1, "profile_sha256": digest, "workspace": str(self.root), "context": "synthetic-session",
                "observed_at": (now - timedelta(seconds=5)).isoformat(),
                "expires_at": (now + timedelta(minutes=10)).isoformat(),
                "skills": [{**s, "registered": True, "resources": [{**r, "readable": True} for r in s["resources"]]}
                           for s in self.profile["skills"]],
                "tools": [{**t, "available": True} for t in self.profile["tools"]]}
        write_json(self.root / "host.json", self.observations)

    def run_check(self, *, host=True, dependency=None, cwd=None, script=SCRIPT, block_original=False):
        command = [sys.executable, str(script), "--workspace", str(self.root), "--context", "synthetic-session"]
        if dependency is not False:
            command += ["--dependency-dir", dependency or DEPENDENCY]
        if host:
            command += ["--host-observations", str(self.root / "host.json")]
        if block_original:
            # Deny access, not merely omit the old path. The relocated helper
            # must need only its bundled copies even if the original exists.
            guard = """import os, runpy, sys
blocked = os.path.abspath(sys.argv.pop(1))
script = sys.argv.pop(1)
def deny_original(event, args):
    if event in {'open', 'os.listdir', 'os.scandir'} and args and isinstance(args[0], (str, bytes)):
        path = os.path.abspath(os.fsdecode(args[0]))
        if path == blocked or path.startswith(blocked + os.sep):
            raise RuntimeError('Original recovery directory is unavailable')
sys.addaudithook(deny_original)
sys.argv[0] = script
runpy.run_path(script, run_name='__main__')
"""
            command = [sys.executable, "-c", guard, DEPENDENCY, str(script), *command[2:]]
        result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, check=False)
        self.assertTrue(result.stdout.startswith("{"), "Expected a bounded JSON readiness report: " + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertLess(len(result.stdout), 1024 * 1024)
        return result.returncode, json.loads(result.stdout)

    def assert_state(self, section, status):
        self.assertEqual(section["status"], status, section)

    def test_scope_like_source_and_supplied_prerequisites_are_ready_but_no_tests_ran(self):
        code, report = self.run_check()
        self.assertEqual(code, 0)
        self.assert_state(report["source"], "ready")
        self.assert_state(report["development"], "ready")
        self.assert_state(report["groups"]["build"], "ready")
        self.assertEqual(report["host_trust"], "supplied_observations_not_independently_authenticated")
        self.assertEqual(report["tests"], "not_run")
        self.assertEqual(report["acceptance"], "not_assessed")
        self.assertFalse((self.app / ".git").exists())

    def make_private(self):
        self.profile["id"] = "acks-like"
        self.profile["inputs"] = ["source-extract"]
        (self.root / "private/source.txt").write_bytes(b"Synthetic private input\n")
        manifest = {"version": 1, "profile_id": "acks-like", "inputs": [
            {"id": "source-extract", "path": "private/source.txt", "sha256": sha(b"Synthetic private input\n"), "size": 24}]}
        digest = write_json(self.root / "private/manifest.json", manifest)
        (self.root / "private/manifest.sha256").write_text(digest + "\n")
        self.profile["private_manifest"] = {"path": "private/manifest.json", "sha256": digest,
                                            "sha256_file": "private/manifest.sha256"}
        self.profile["groups"].append({"id": "audit", "optional": True, "recipe": "build",
                                       "requires": requirements(inputs=["source-extract"])})
        self.save()

    def test_acks_like_optional_missing_private_input_leaves_build_ready(self):
        self.make_private()
        (self.root / "private/source.txt").unlink()
        code, report = self.run_check()
        self.assertEqual(code, 0)
        self.assert_state(report["groups"]["build"], "ready")
        self.assert_state(report["groups"]["audit"], "blocked")
        self.assertEqual(report["groups"]["audit"]["checks"][-1]["state"], "missing")

    def test_private_hash_companion_is_required_only_for_consumers(self):
        self.make_private()
        (self.root / "private/manifest.sha256").unlink()
        _, report = self.run_check()
        self.assert_state(report["groups"]["build"], "ready")
        self.assert_state(report["groups"]["audit"], "blocked")
        self.assertIn("missing", [c["state"] for c in report["groups"]["audit"]["checks"]])

    def test_selected_private_bytes_and_manifest_hashes_must_match(self):
        self.make_private()
        _, good = self.run_check()
        self.assert_state(good["groups"]["audit"], "ready")
        (self.root / "private/source.txt").write_bytes(b"wrong")
        _, bad = self.run_check()
        self.assertIn("mismatch", [c["state"] for c in bad["groups"]["audit"]["checks"]])
        (self.root / "private/manifest.sha256").write_text("b" * 64 + "\n")
        _, bad = self.run_check()
        self.assert_state(bad["groups"]["audit"], "blocked")

    def test_unselected_private_files_are_not_read_or_echoed(self):
        self.make_private()
        os.mkfifo(self.root / "private/unrelated")
        _, report = self.run_check()
        self.assert_state(report["groups"]["audit"], "ready")
        self.assertNotIn("private/source.txt", json.dumps(report))

    def test_caw_like_source_snapshot_cannot_supply_report_history(self):
        self.profile["id"] = "caw-like"
        self.profile["groups"].append({"id": "report", "optional": False, "recipe": "build", "requires": requirements(
            git=[{"app": "sample", "head": True, "commits": ["b" * 40], "complete_history": True}],
            files=[{"path": "control.json", "sha256": sha(b"{}\n")}], report_parents=["reports"])})
        self.save()
        code, report = self.run_check()
        self.assertEqual(code, 1)
        self.assert_state(report["source"], "ready")
        self.assert_state(report["groups"]["build"], "ready")
        self.assert_state(report["groups"]["report"], "blocked")
        self.assertIn("unavailable", [c["state"] for c in report["groups"]["report"]["checks"]])

    def test_local_skill_files_do_not_imply_host_registration(self):
        skill = self.root / ".agents/skills/review-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_bytes(b"Synthetic skill\n")
        _, report = self.run_check(host=False)
        self.assert_state(report["source"], "ready")
        self.assert_state(report["development"], "blocked")

    def test_missing_unregistered_mismatched_unreadable_skill_evidence_blocks(self):
        original = json.loads(json.dumps(self.observations))
        for mutation in ("missing", "unregistered", "mismatch", "resource-missing", "unreadable", "resource-mismatch"):
            with self.subTest(mutation=mutation):
                self.observations = json.loads(json.dumps(original))
                item = self.observations["skills"][0]
                if mutation == "missing": self.observations["skills"] = []
                if mutation == "unregistered": item["registered"] = False
                if mutation == "mismatch": item["sha256"] = "b" * 64
                if mutation == "resource-missing": item["resources"].pop()
                if mutation == "unreadable": item["resources"][1]["readable"] = False
                if mutation == "resource-mismatch": item["resources"][1]["sha256"] = "b" * 64
                self.save(fresh_host=False)
                _, report = self.run_check()
                self.assert_state(report["development"], "blocked")

    def test_host_binding_freshness_and_timestamp_validation(self):
        original = json.loads(json.dumps(self.observations))
        cases = {"workspace": str(self.root.parent), "profile_sha256": "b" * 64,
                 "context": "other-session", "expires_at": "2000-01-01T00:00:00Z",
                 "observed_at": "2099-01-01T00:00:00Z"}
        for key, value in cases.items():
            with self.subTest(field=key):
                self.observations = {**original, key: value}
                self.save(fresh_host=False)
                _, report = self.run_check()
                self.assert_state(report["development"], "blocked")
        self.observations = {**original, "observed_at": "secret-malformed-time"}
        self.save(fresh_host=False)
        _, report = self.run_check()
        self.assert_state(report["development"], "blocked")
        self.assertNotIn("secret-malformed-time", json.dumps(report))

    def test_unknown_or_wrong_tool_observation_cannot_pass(self):
        self.observations["tools"][0]["version"] = "0.0"
        self.save(fresh_host=False)
        _, report = self.run_check()
        self.assert_state(report["development"], "blocked")

    def test_source_bytes_governance_and_bundle_identity_are_independent_checks(self):
        for path in ("apps/sample/main.txt", "AGENTS.md", "evidence/source.json"):
            with self.subTest(path=path):
                file = self.root / path
                original = file.read_bytes()
                file.write_bytes(b"wrong bytes\n")
                _, report = self.run_check()
                self.assert_state(report["source"], "blocked")
                self.assertIn("mismatch", [c["state"] for c in report["source"]["checks"]])
                file.write_bytes(original)

    def test_requested_tree_and_source_objects_are_verified_not_labels(self):
        self.profile["applications"][0]["tree"] = "b" * 40
        self.save()
        _, report = self.run_check()
        self.assert_state(report["source"], "blocked")
        self.profile["applications"][0]["tree"] = self.bundle["snapshots"][0]["commit"]["tree"]["sha"]
        self.bundle["snapshots"][0]["blobs"][0]["content"] = base64.b64encode(b"Corrupted source\n").decode()
        self.profile["applications"][0]["bundle"]["sha256"] = write_json(self.root / "evidence/source.json", self.bundle)
        self.save()
        _, report = self.run_check()
        self.assert_state(report["source"], "blocked")

    def test_advanced_remote_ref_does_not_replace_selected_checkpoint(self):
        self.bundle["references"][0]["observed_commit"] = "b" * 40
        self.profile["applications"][0]["bundle"]["sha256"] = write_json(self.root / "evidence/source.json", self.bundle)
        self.save()
        _, report = self.run_check()
        self.assert_state(report["source"], "ready")
        self.assertTrue(report["source"]["checks"][-1]["ref_moved"])

    def test_report_parent_missing_file_symlink_and_access_uncertainty(self):
        self.profile["groups"][0]["requires"]["report_parents"] = ["reports"]
        self.save()
        _, good = self.run_check()
        self.assert_state(good["groups"]["build"], "unverified")
        self.assertEqual(good["groups"]["build"]["checks"][-1]["state"], "unverified")
        self.assertTrue(good["groups"]["build"]["checks"][-1]["directory_exists"])
        (self.root / "reports").rmdir()
        _, missing = self.run_check()
        self.assert_state(missing["groups"]["build"], "blocked")
        (self.root / "reports").write_text("file")
        _, wrong = self.run_check()
        self.assert_state(wrong["groups"]["build"], "blocked")
        (self.root / "reports").unlink()
        (self.root / "reports").symlink_to(self.root / "evidence", target_is_directory=True)
        _, unsafe = self.run_check()
        self.assert_state(unsafe["groups"]["build"], "blocked")

    def test_missing_report_control_blocks_before_tests(self):
        self.profile["groups"][0]["requires"]["files"] = [{"path": "control.json", "sha256": sha(b"{}\n")}]
        self.save()
        (self.root / "control.json").unlink()
        _, report = self.run_check()
        self.assert_state(report["groups"]["build"], "blocked")
        self.assertEqual(report["tests"], "not_run")

    def test_closed_schema_rejects_unknown_fields_hashes_traversal_and_bad_types(self):
        original = json.loads(json.dumps(self.profile))
        for mutation in ("field", "hash", "traversal", "absolute", "boolean", "reference", "duplicate", "dot-ref", "lock-ref"):
            with self.subTest(mutation=mutation):
                self.profile = json.loads(json.dumps(original))
                if mutation == "field": self.profile["secret-unknown-field"] = "private-value"
                if mutation == "hash": self.profile["governance"][0]["sha256"] = "private-value"
                if mutation == "traversal": self.profile["governance"][0]["path"] = "../outside"
                if mutation == "absolute": self.profile["applications"][0]["path"] = str(self.app)
                if mutation == "boolean": self.profile["version"] = True
                if mutation == "reference": self.profile["groups"][0]["requires"]["inputs"] = ["undeclared"]
                if mutation == "duplicate": self.profile["groups"].append(self.profile["groups"][0])
                if mutation == "dot-ref": self.profile["applications"][0]["ref"] = "refs/heads/.invalid/name"
                if mutation == "lock-ref": self.profile["applications"][0]["ref"] = "refs/heads/name.lock/child"
                self.save()
                code, report = self.run_check()
                self.assertEqual(code, 2)
                self.assertEqual(report["error"]["state"], "malformed")
                self.assertNotIn("private-value", json.dumps(report))
                self.assertNotIn("secret-unknown-field", json.dumps(report))

    def test_duplicate_json_keys_are_malformed(self):
        (self.root / "workspace-setup.json").write_text('{"version":1,"version":1}')
        code, report = self.run_check()
        self.assertEqual(code, 2)
        self.assertEqual(report["error"]["state"], "malformed")

    def test_symlink_and_special_inputs_are_refused_without_blocking(self):
        original = (self.root / "AGENTS.md").read_bytes()
        for kind in ("symlink", "fifo", "hardlink"):
            with self.subTest(kind=kind):
                (self.root / "AGENTS.md").unlink()
                if kind == "symlink": (self.root / "AGENTS.md").symlink_to(self.root / "recipe.md")
                if kind == "fifo": os.mkfifo(self.root / "AGENTS.md")
                if kind == "hardlink": os.link(self.root / "recipe.md", self.root / "AGENTS.md")
                _, report = self.run_check()
                self.assert_state(report["source"], "blocked")
                (self.root / "AGENTS.md").unlink()
                (self.root / "AGENTS.md").write_bytes(original)

    def test_dependency_missing_mismatch_and_ambient_module_substitution(self):
        empty = self.root / "dependency"
        empty.mkdir()
        code, report = self.run_check(dependency=str(empty))
        self.assertEqual(code, 2)
        self.assertEqual(report["error"]["state"], "missing")
        for name in ("garage_rebuild.py", "garage_workspace.py"):
            shutil.copyfile(Path(DEPENDENCY) / name, empty / name)
        with (empty / "garage_workspace.py").open("a") as stream: stream.write("\n# modified\n")
        code, report = self.run_check(dependency=str(empty))
        self.assertEqual(code, 2)
        self.assertEqual(report["error"]["state"], "mismatch")
        (self.root / "garage_rebuild.py").write_text("raise RuntimeError('ambient substitution')")
        code, _ = self.run_check(cwd=self.root)
        self.assertEqual(code, 0)

    def test_no_inspected_files_change_and_profile_commands_never_execute(self):
        self.profile["recipes"][0]["commands"] = ["touch MUST-NOT-EXIST", "$(touch MUST-NOT-EXIST)"]
        self.save()
        before = inventory(self.root)
        dependency_before = inventory(Path(DEPENDENCY))
        self.run_check()
        self.assertEqual(before, inventory(self.root))
        self.assertEqual(dependency_before, inventory(Path(DEPENDENCY)))
        self.assertFalse((self.root / "MUST-NOT-EXIST").exists())

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.app), *args], check=True, text=True, capture_output=True).stdout.strip()

    def make_history(self):
        self.git("init", "--quiet", "--template=")
        self.git("add", "main.txt")
        self.git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", "commit", "--quiet", "-m", "Synthetic")
        commit = self.git("rev-parse", "HEAD")
        self.bundle["snapshots"][0]["requested_commit"] = commit
        self.bundle["snapshots"][0]["commit"]["sha"] = commit
        self.bundle["references"][0]["observed_commit"] = commit
        self.profile["applications"][0]["commit"] = commit
        self.profile["applications"][0]["bundle"]["sha256"] = write_json(self.root / "evidence/source.json", self.bundle)
        self.profile["groups"][0]["requires"]["git"] = [{"app": "sample", "head": True, "commits": [commit], "complete_history": True}]
        self.save()
        return commit

    def test_genuine_git_head_objects_and_complete_history_are_checked(self):
        self.make_history()
        before = inventory(self.app / ".git")
        code, report = self.run_check()
        self.assertEqual(code, 0, report)
        self.assert_state(report["groups"]["build"], "ready")
        self.assertEqual(before, inventory(self.app / ".git"))
        self.profile["groups"][0]["requires"]["git"][0]["commits"] = ["b" * 40]
        self.save()
        _, report = self.run_check()
        self.assert_state(report["groups"]["build"], "blocked")

    def test_shallow_promisor_replacement_and_include_git_state_are_unavailable(self):
        commit = self.make_history()
        config = self.app / ".git/config"
        original = config.read_bytes()
        for relative, data in (("shallow", (commit + "\n").encode()),
                               ("objects/info/alternates", b"/unrelated/private/path\n"),
                               ("objects/pack/test.promisor", b"")):
            with self.subTest(path=relative):
                file = self.app / ".git" / relative
                file.parent.mkdir(exist_ok=True, parents=True)
                file.write_bytes(data)
                _, report = self.run_check()
                self.assert_state(report["groups"]["build"], "blocked")
                file.unlink()
        config.write_bytes(original + b"\n[include]\n path = /unrelated/private/path\n")
        _, report = self.run_check()
        self.assert_state(report["groups"]["build"], "blocked")

    def test_profile_relative_paths_do_not_depend_on_cwd(self):
        code, report = self.run_check(cwd="/")
        self.assertEqual(code, 0)
        self.assert_state(report["source"], "ready")

    def test_genuine_commit_tree_must_match_supplied_source_identity(self):
        self.make_history()
        (self.app / "extra.txt").write_text("Different commit tree\n")
        self.git("add", "extra.txt")
        self.git("-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", "commit", "--quiet", "-m", "Different tree")
        commit = self.git("rev-parse", "HEAD")
        self.profile["applications"][0]["commit"] = commit
        self.bundle["snapshots"][0]["requested_commit"] = commit
        self.bundle["snapshots"][0]["commit"]["sha"] = commit
        self.bundle["references"][0]["observed_commit"] = commit
        self.profile["applications"][0]["bundle"]["sha256"] = write_json(self.root / "evidence/source.json", self.bundle)
        self.save()
        _, report = self.run_check()
        self.assert_state(report["groups"]["build"], "blocked")
        self.assertIn("mismatch", [c["state"] for c in report["groups"]["build"]["checks"]])

    def test_malformed_private_and_dependency_messages_never_leak_contents(self):
        self.make_private()
        (self.root / "private/source.txt").write_bytes(b"-----BEGIN PRIVATE KEY-----\nPRIVATE-SENTINEL\n")
        _, report = self.run_check()
        self.assert_state(report["groups"]["audit"], "blocked")
        self.assertNotIn("PRIVATE-SENTINEL", json.dumps(report))
        self.assertNotIn("private/source.txt", json.dumps(report))

    def test_profile_and_observation_symlinks_are_not_followed(self):
        for name, section_name in (("host.json", "development"), ("workspace-setup.json", "error")):
            with self.subTest(name=name):
                path = self.root / name
                backup = self.root / (name + ".copy")
                path.rename(backup)
                path.symlink_to(backup)
                _, report = self.run_check()
                if section_name == "error":
                    self.assertEqual(report["error"]["state"], "unsafe")
                else:
                    self.assert_state(report[section_name], "blocked")
                path.unlink()
                backup.rename(path)

    def test_three_published_examples_drive_the_synthetic_patterns(self):
        examples = ROOT / "workspace-setup/references/cloud-examples"
        for name in ("scope-like", "acks-like", "caw-like"):
            with self.subTest(example=name):
                path = examples / (name + ".json")
                self.assertTrue(path.is_file(), "The sanitized example must exist")
                if name == "acks-like":
                    self.make_private()
                self.profile = json.loads(path.read_bytes())
                self.save()
                if name == "acks-like":
                    (self.root / "private/source.txt").unlink()
                code, report = self.run_check()
                self.assert_state(report["source"], "ready")
                self.assert_state(report["groups"]["build"], "ready")
                if name == "acks-like": self.assert_state(report["groups"]["audit"], "blocked")
                if name == "caw-like": self.assert_state(report["groups"]["report"], "blocked")

    def test_declarative_schema_artifact_has_closed_shapes_for_all_inputs(self):
        path = ROOT / "workspace-setup/references/cloud-readiness.schema.json"
        self.assertTrue(path.is_file(), "The machine-readable input schema must exist")
        schema = json.loads(path.read_bytes())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        for name in ("profile", "host", "privateManifest", "requirements"):
            self.assertFalse(schema["$defs"][name]["additionalProperties"])

    def test_large_cross_product_is_refused_before_unbounded_reporting(self):
        self.profile["tools"] = [{"id": "tool-" + str(i), "version": "1"} for i in range(128)]
        self.profile["development"] = requirements()
        self.profile["groups"] = [{"id": "group-" + str(i), "optional": False, "recipe": "build",
                                   "requires": requirements(tools=[t["id"] for t in self.profile["tools"]])}
                                  for i in range(128)]
        self.save()
        code, report = self.run_check()
        self.assertEqual(code, 2)
        self.assertEqual(report["error"]["state"], "malformed")

    def test_default_bundled_dependency_is_available_without_directory_argument(self):
        code, report = self.run_check(dependency=False)
        self.assertEqual(code, 0, report)
        self.assert_state(report["source"], "ready")

    def test_relocated_skill_uses_default_with_original_access_denied(self):
        moved = self.root / "relocated-skill"
        shutil.copytree(ROOT / "workspace-setup", moved)
        before = inventory(moved)
        code, report = self.run_check(dependency=False, cwd="/", script=moved / "scripts/check_cloud_readiness.py", block_original=True)
        self.assertEqual(code, 0, report)
        self.assertEqual(before, inventory(moved))

    def test_bundled_recovery_harness_loads_original_and_regression_tests(self):
        result = subprocess.run([sys.executable, str(ROOT / "tests/run_recovery_tests.py"), "--list"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        names = result.stdout.splitlines()
        self.assertEqual(len(names), 89)
        self.assertEqual(len(set(names)), 89)
        self.assertEqual(sum(not name.startswith("test_source_expansion.") for name in names), 79)


if __name__ == "__main__":
    unittest.main()
