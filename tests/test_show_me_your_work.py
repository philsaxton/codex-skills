"""Exercise decision-log appends without invoking models or external services."""
from pathlib import Path
import csv
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "show-me-your-work/scripts/log.sh"
HEADER = ["ts", "run", "phase", "decision", "why", "evidence", "result"]


class DecisionLogTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(prefix="decision-log-")
        self.addCleanup(self.fixture.cleanup)
        self.log = Path(self.fixture.name) / "task with spaces" / "trail.tsv"

    def append(self, *cells, check=True, env=None):
        return subprocess.run(
            ["bash", str(HELPER), str(self.log), *cells],
            capture_output=True, text=True, check=check, env=env,
        )

    def rows(self):
        with self.log.open(newline="") as source:
            return list(csv.reader(source, delimiter="\t", strict=True))

    def test_create_append_and_correction_preserve_history(self):
        self.append("run-a", "verify", "Ran suite", "Check behavior", "receipt.txt", "failed")
        original = self.log.read_bytes()
        self.append("run-b", "correction", "Correct run-a line 2", "Wrong fixture",
                    "new-receipt.txt", "inconclusive")
        self.assertTrue(self.log.read_bytes().startswith(original))
        rows = self.rows()
        self.assertEqual(rows[0], HEADER)
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(len(row) == 7 for row in rows))
        self.assertRegex(rows[1][0], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(rows[1][1:], ["run-a", "verify", "Ran suite", "Check behavior",
                                       "receipt.txt", "failed"])
        self.assertEqual(rows[2][1], "run-b")
        self.assertEqual(rows[2][-1], "inconclusive")

    def test_separators_and_shell_text_remain_cell_data(self):
        marker = Path(self.fixture.name) / "must-not-exist"
        decision = f'Kept "quotes"; $(touch {marker})'
        self.append("run-a", "phase\twith\nlines\r", decision,
                    "reason\twith\nlines", "path with spaces", "")
        row = self.rows()[1]
        self.assertEqual(len(row), 7)
        self.assertEqual(row[2], "phase with lines ")
        self.assertEqual(row[3], decision)
        self.assertEqual(row[4], "reason with lines")
        self.assertEqual(row[-1], "")
        self.assertFalse(marker.exists())

    def test_formula_prefixes_including_after_whitespace_are_escaped(self):
        cells = ["=1+1", "+SUM(A1)", "-1", "@command", " \t=1+1", "\n+1"]
        self.append(*cells)
        self.assertEqual(self.rows()[1][1:], ["'=1+1", "'+SUM(A1)", "'-1",
                                             "'@command", "'  =1+1", "' +1"])

    def test_quotes_round_trip_without_consuming_columns_or_later_entries(self):
        cells = ['"unmatched', 'embedded "quote"', 'trailing"',
                 '""', '"=1+1"', 'a "quoted" result']
        self.append(*cells)
        self.append("run-b", "handoff", "Next checkpoint", "Continue",
                    "receipt.txt", "open")
        rows = self.rows()
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(len(row) == 7 for row in rows))
        self.assertEqual(rows[1][1:], cells)
        self.assertEqual(rows[2][1:], ["run-b", "handoff", "Next checkpoint",
                                      "Continue", "receipt.txt", "open"])
        self.assertEqual(len(self.log.read_text().splitlines()), 3)

    def test_formula_guards_survive_quote_decoding(self):
        cells = ['=SUM(1,"2")', ' +SUM("1")', '-"1"', '@"command"',
                 '"=1+1"', '"+1']
        self.append(*cells)
        self.assertEqual(self.rows()[1][1:], ["'" + cell for cell in cells[:4]]
                         + cells[4:])

    def test_viewer_line_separators_stay_in_one_physical_row(self):
        separators = "\t\n\r\v\f\x1c\x1d\x1e\u0085\u2028\u2029"
        self.append("run-a", "verify", "a" + separators + "b", "why", "receipt", "open")
        self.assertEqual(self.rows()[1][3], "a           b")
        self.assertEqual(len(self.log.read_text().splitlines()), 2)

    def test_non_utf8_argument_is_not_silently_dropped(self):
        self.append(b"run-\xff", "verify", "Kept evidence", "why", "receipt", "open")
        self.assertIn(b"\trun-\xff\tverify\t", self.log.read_bytes())

    def test_timestamp_failure_does_not_change_or_create_log(self):
        commands = Path(self.fixture.name) / "commands"
        commands.mkdir()
        date = commands / "date"
        date.write_text("#!/bin/sh\nexit 7\n")
        date.chmod(0o755)
        env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ["PATH"])
        result = self.append("a", "b", "c", "d", "e", "f", check=False, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())
        self.append("run-a", "verify", "Original entry", "why", "receipt", "open")
        original = self.log.read_bytes()
        result = self.append("a", "b", "c", "d", "e", "f", check=False, env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.log.read_bytes(), original)

    def test_incompatible_log_is_rejected_without_changes(self):
        self.log.parent.mkdir(parents=True)
        original = b"ts\tphase\tdecision\nold\trow\tkept\n"
        self.log.write_bytes(original)
        result = self.append("a", "b", "c", "d", "e", "f", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.log.read_bytes(), original)

    def test_incomplete_final_line_is_rejected_without_changes(self):
        self.log.parent.mkdir(parents=True)
        original = ("\t".join(HEADER) + "\ninterrupted row").encode()
        self.log.write_bytes(original)
        result = self.append("a", "b", "c", "d", "e", "f", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.log.read_bytes(), original)

    def test_wrong_argument_count_does_not_create_log(self):
        result = self.append("run-a", "phase", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
