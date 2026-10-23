from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "implementation-tracker/scripts/implementation_tracker.py"
FIXTURE = """# Implementation

Keep this introduction and [specification](docs/spec.md).

<!-- implementation-tracker:v1 -->
| ID | Title | Status | Checkpoint | Dependencies | Evidence |
| --- | --- | --- | --- | --- | --- |
| S0.1 | Define request | ready | Contract accepted | S0.2 | [Review](docs/review.md) |
| S0.2 | Benchmark | planned | Examples reviewed | | |
| VO-026 | Export | in_progress | Output matches contract | | |
| ACKS-MD-0199 | Present result | in_progress | Public output verified | | |
<!-- /implementation-tracker -->

## History

Earlier S0.1 was planned. Preserve that observation.
"""


class ImplementationTrackerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tracker test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.file = self.root / "IMPLEMENTATION.md"
        self.file.write_text(FIXTURE, encoding="utf-8")

    def invoke(self, *args, code=0, cwd=None, human=False):
        command = [sys.executable, "-B", str(SCRIPT)]
        if not human:
            command.append("--json")
        result = subprocess.run(command + list(args), cwd=cwd or self.root,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if human:
            return result.stdout
        payload = result.stdout if code == 0 else result.stderr
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            self.fail("CLI did not return the expected JSON response: " + payload)

    def revision(self):
        return "sha256:" + hashlib.sha256(self.file.read_bytes()).hexdigest()

    def update(self, item="S0.1", *fields, code=0, revision=None):
        return self.invoke("update", item, "--expected-revision",
                           revision or self.revision(), *fields, code=code)

    def test_list_filters_recorded_ready_without_promoting_dependencies(self):
        before = self.file.read_bytes()
        result = self.invoke("list", "--status", "ready")
        self.assertEqual([row["id"] for row in result["slices"]], ["S0.1"])
        self.assertEqual(result["slices"][0]["dependencies"], ["S0.2"])
        self.assertEqual(result["revision"], self.revision())
        self.assertEqual(result["file"], str(self.file))
        self.assertEqual(self.file.read_bytes(), before)
        self.assertEqual(list(self.root.iterdir()), [self.file])

    def test_inspect_returns_complete_record_and_multiple_active_slices(self):
        row = self.invoke("inspect", "S0.1")["slice"]
        self.assertEqual(row, {"id": "S0.1", "title": "Define request", "status": "ready",
                               "checkpoint": "Contract accepted", "dependencies": ["S0.2"],
                               "evidence": "[Review](docs/review.md)", "type": "slice",
                               "priority": "", "owner": "", "blocker": "", "parent": ""})
        active = self.invoke("list", "--status", "in_progress")["slices"]
        self.assertEqual([row["id"] for row in active], ["VO-026", "ACKS-MD-0199"])

    def test_update_preserves_other_rows_prose_and_direct_edit(self):
        self.file.write_text(FIXTURE.replace("Benchmark", "Human's benchmark"), encoding="utf-8")
        before = self.file.read_text(encoding="utf-8")
        result = self.update("S0.1", "--status", "review")
        self.assertTrue(result["changed"])
        self.assertEqual(self.file.read_text(encoding="utf-8"), before.replace("| ready |", "| review |"))
        self.assertEqual(self.invoke("inspect", "S0.2")["slice"]["title"], "Human's benchmark")
        self.assertEqual(result["revision"], self.revision())

    def test_stale_update_preserves_newer_manual_changes(self):
        revision = self.revision()
        self.file.write_text(FIXTURE + "\nManual note.\n", encoding="utf-8")
        before = self.file.read_bytes()
        error = self.update("S0.1", "--status", "done", revision=revision, code=3)["error"]
        self.assertEqual(error["code"], "stale_revision")
        self.assertEqual(error["actual_revision"], self.revision())
        self.assertEqual(error["expected_revision"], revision)
        self.assertEqual(self.file.read_bytes(), before)

    def test_noop_does_not_reformat_table(self):
        self.file.write_text(FIXTURE.replace("| S0.1 |", "|  S0.1   |"), encoding="utf-8")
        before = self.file.read_bytes()
        result = self.update("S0.1", "--status", "ready")
        self.assertFalse(result["changed"])
        self.assertEqual(self.file.read_bytes(), before)

    def test_insert_at_position_preserves_identifiers_and_records_fields(self):
        result = self.invoke("insert", "S099", "--title", "New boundary", "--checkpoint", "[Contract](c.md)",
                             "--before", "S0.2", "--owner", "another agent", "--priority", "P1",
                             "--dependencies", "S0.1,VO-026", "--expected-revision", self.revision())
        self.assertEqual(result["slice"]["status"], "planned")
        self.assertEqual(result["slice"]["dependencies"], ["S0.1", "VO-026"])
        self.assertEqual(result["slice"]["owner"], "another agent")
        rows = self.invoke("list")["slices"]
        self.assertEqual([row["id"] for row in rows], ["S0.1", "S099", "S0.2", "VO-026", "ACKS-MD-0199"])
        self.assertEqual(rows[0]["status"], "ready")
        self.assertEqual(rows[2]["owner"], "")

    def test_update_can_add_and_clear_optional_columns_without_deciding_state(self):
        self.update("S0.1", "--owner", "reviewer", "--blocker", "[Decision](d.md)", "--priority", "P0")
        row = self.update("S0.1", "--owner", "", "--dependencies", "", "--priority", "")["slice"]
        self.assertEqual(row["owner"], "")
        self.assertEqual(row["dependencies"], [])
        self.assertEqual(row["priority"], "")
        self.assertEqual(row["blocker"], "[Decision](d.md)")
        self.assertEqual(row["status"], "ready")

    def test_epics_are_explicit_and_parent_does_not_inherit_dependencies(self):
        self.invoke("insert", "E1", "--title", "Milestone", "--checkpoint", "Reviewed outcome",
                    "--type", "epic", "--dependencies", "S0.2", "--expected-revision", self.revision())
        self.update("VO-026", "--parent", "E1")
        row = self.invoke("inspect", "VO-026")["slice"]
        self.assertEqual(row["dependencies"], [])
        self.assertEqual(row["parent"], "E1")
        self.assertEqual(len(self.invoke("list")["slices"]), 4)
        self.assertEqual([r["id"] for r in self.invoke("list", "--type", "epic")["slices"]], ["E1"])

    def test_markdown_pipes_backslashes_unicode_and_crlf_round_trip(self):
        self.file.write_bytes(FIXTURE.replace("\n", "\r\n").encode())
        value = "Résumé `a|b` at C:\\work\\evidence; [review](docs/r.md)"
        self.update("S0.1", "--checkpoint", value)
        self.assertEqual(self.invoke("inspect", "S0.1")["slice"]["checkpoint"], value)
        data = self.file.read_bytes()
        self.assertIn(b"a\\|b", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))

    def test_fenced_example_is_not_a_second_tracker(self):
        self.file.write_text("```markdown\n" + FIXTURE + "```\n\n" + FIXTURE, encoding="utf-8")
        self.assertEqual(self.invoke("validate")["count"], 4)

    def test_inline_backtick_code_before_fenced_example_keeps_live_tracker(self):
        prefix = "```git status```\n\n~~~markdown\n" + FIXTURE + "~~~\n\n"
        self.file.write_text(prefix + FIXTURE, encoding="utf-8")
        self.assertEqual(self.invoke("validate")["count"], 4)
        self.update("S0.1", "--status", "review")
        self.assertEqual(self.file.read_text(encoding="utf-8"),
                         prefix + FIXTURE.replace("| ready |", "| review |"))

    def test_unicode_separators_in_cell_text_remain_readable_after_update(self):
        value = "Quoted text: alpha\u2028beta\u2029gamma\u0085delta"
        self.update("S0.1", "--checkpoint", value)
        self.assertEqual(self.invoke("inspect", "S0.1")["slice"]["checkpoint"], value)

    def test_invalid_documents_fail_without_rewriting(self):
        cases = {
            "duplicate id": FIXTURE.replace("| S0.2 |", "| S0.1 |"),
            "missing reference": FIXTURE.replace("| S0.2 | [Review]", "| MISSING | [Review]"),
            "invalid status": FIXTURE.replace("| planned |", "| approved |"),
            "missing checkpoint": FIXTURE.replace("| Examples reviewed |", "| |"),
            "unknown column": FIXTURE.replace("| Evidence |", "| Approval |"),
            "duplicate column": FIXTURE.replace("| Evidence |", "| Title |"),
            "ragged row": FIXTURE.replace("| Examples reviewed | | |", "| Examples reviewed | |"),
            "duplicate block": FIXTURE + FIXTURE,
            "missing closing marker": FIXTURE.replace("<!-- /implementation-tracker -->", ""),
            "unsupported version": FIXTURE.replace("tracker:v1", "tracker:v2"),
            "legacy layout": "# Implementation\n| Slice | Status |\n|---|---|\n| S1 | active |\n",
        }
        for name, content in cases.items():
            with self.subTest(name=name):
                self.file.write_text(content, encoding="utf-8")
                before = self.file.read_bytes()
                self.invoke("validate", code=2)
                self.update("S0.1", "--status", "done", code=2)
                self.assertEqual(self.file.read_bytes(), before)

    def test_invalid_reference_graphs_do_not_publish(self):
        for field, value in (("--dependencies", "S0.1"), ("--dependencies", "S0.2,S0.2"),
                             ("--parent", "MISSING"), ("--parent", "S0.1")):
            with self.subTest(field=field, value=value):
                before = self.file.read_bytes()
                self.update("S0.1", field, value, code=2)
                self.assertEqual(self.file.read_bytes(), before)
        self.update("S0.2", "--dependencies", "S0.1", code=2)
        self.update("S0.1", "--parent", "S0.2")
        before = self.file.read_bytes()
        self.update("S0.2", "--parent", "S0.1", code=2)
        self.assertEqual(self.file.read_bytes(), before)

    def test_invalid_mutations_preserve_document(self):
        for fields in (("--title", ""), ("--checkpoint", "first\nsecond"), ("--priority", "P9"),
                       ("--status", "Ready"), ("--status", "garbage"), ("--type", "issue")):
            with self.subTest(fields=fields):
                before = self.file.read_bytes()
                self.update("S0.1", *fields, code=2)
                self.assertEqual(self.file.read_bytes(), before)
        self.update("S0.1", code=2)
        self.update("MISSING", "--status", "done", code=2)
        self.invoke("update", "S0.1", "--status", "done", code=2)
        self.invoke("insert", "S0.1", "--title", "Duplicate", "--checkpoint", "Check",
                    "--expected-revision", self.revision(), code=2)

    def test_override_works_from_elsewhere_without_discovering_another_file(self):
        other = self.root / "elsewhere"
        other.mkdir()
        self.invoke("list", cwd=other, code=1)
        result = self.invoke("list", "--file", str(self.file), cwd=other)
        self.assertEqual(len(result["slices"]), 4)
        self.assertEqual(list(other.iterdir()), [])

    def test_init_creates_valid_empty_tracker_and_never_overwrites(self):
        destination = self.root / "new document.md"
        result = self.invoke("--file", str(destination), "init")
        self.assertTrue(result["changed"])
        self.assertEqual(self.invoke("--file", str(destination), "list")["slices"], [])
        before = destination.read_bytes()
        self.invoke("--file", str(destination), "init", code=2)
        self.assertEqual(destination.read_bytes(), before)

    def test_lock_conflict_preserves_existing_lock_and_tracker(self):
        lock = self.root / ".IMPLEMENTATION.md.lock"
        lock.write_text('{"pid": 12345, "host": "another-writer"}\n')
        before = self.file.read_bytes()
        self.update("S0.1", "--status", "done", code=4)
        self.assertEqual(self.file.read_bytes(), before)
        self.assertIn("another-writer", lock.read_text())
        self.assertEqual(self.invoke("inspect", "S0.1")["slice"]["status"], "ready")

    def test_two_writers_cannot_publish_from_the_same_revision(self):
        revision = self.revision()
        processes = [subprocess.Popen([sys.executable, "-B", str(SCRIPT), "--json", "update", item,
                                      "--status", "done", "--expected-revision", revision],
                                     cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for item in ("S0.1", "S0.2")]
        for process in processes:
            process.communicate(timeout=10)
        self.assertEqual(sum(p.returncode == 0 for p in processes), 1)
        self.assertTrue(all(p.returncode in (0, 3, 4) for p in processes))
        done = self.invoke("list", "--status", "done")["slices"]
        self.assertEqual(len(done), 1)
        self.assertEqual(list(self.root.iterdir()), [self.file])

    def test_file_modes_preserved_and_symlink_alias_uses_target_lock(self):
        self.file.chmod(0o640)
        alias = self.root / "alias.md"
        alias.symlink_to(self.file)
        self.invoke("--file", str(alias), "update", "S0.1", "--status", "done",
                    "--expected-revision", self.revision())
        self.assertTrue(alias.is_symlink())
        self.assertEqual(self.file.stat().st_mode & 0o777, 0o640)
        (self.root / ".IMPLEMENTATION.md.lock").write_text("occupied")
        self.invoke("--file", str(alias), "update", "S0.1", "--status", "ready",
                    "--expected-revision", self.revision(), code=4)

    def test_hardlinked_write_is_refused_without_diverging_names(self):
        alias = self.root / "linked.md"
        os.link(self.file, alias)
        before = self.file.read_bytes()
        self.update("S0.1", "--status", "done", code=2)
        self.assertEqual(alias.read_bytes(), before)
        self.assertEqual(self.file.read_bytes(), before)

    def test_human_output_includes_identity_state_and_revision(self):
        output = self.invoke("list", "--status", "ready", human=True)
        self.assertIn("S0.1", output)
        self.assertIn("ready", output)
        self.assertNotIn("VO-026", output)
        self.assertIn(self.revision(), output)


if __name__ == "__main__":
    unittest.main()
