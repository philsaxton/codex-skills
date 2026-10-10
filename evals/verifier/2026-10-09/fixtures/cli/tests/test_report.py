import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReportBehavior(unittest.TestCase):
    def invoke(self, contents):
        with tempfile.TemporaryDirectory() as folder:
            input_file = Path(folder) / "invoices.csv"
            output_file = Path(folder) / "report.json"
            input_file.write_text(contents, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "report.py"), "--input", str(input_file),
                 "--output", str(output_file)], capture_output=True, text=True,
            )
            report = json.loads(output_file.read_text()) if output_file.exists() else None
            return result, report

    def test_supplied_example_filters_unpaid_rows(self):
        result, report = self.invoke((ROOT / "data/invoices.csv").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report, {"paid_count": 2, "paid_total": "19.75"})

    def test_decimal_arithmetic_and_format(self):
        result, report = self.invoke("invoice_id,status,amount\nA,paid,0.10\nB,paid,0.20\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report, {"paid_count": 2, "paid_total": "0.30"})

    def test_no_paid_rows(self):
        for contents in ("invoice_id,status,amount\n", "invoice_id,status,amount\nA,pending,5.00\n"):
            with self.subTest(contents=contents):
                result, report = self.invoke(contents)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(report, {"paid_count": 0, "paid_total": "0.00"})

    def test_invalid_amount_is_an_error_without_output(self):
        for amount in ("oops", "NaN", "Infinity"):
            with self.subTest(amount=amount):
                result, report = self.invoke(f"invoice_id,status,amount\nA,pending,{amount}\n")
                self.assertEqual(result.returncode, 2)
                self.assertIn("invalid amount", result.stderr.lower())
                self.assertIsNone(report)


if __name__ == "__main__":
    unittest.main()
