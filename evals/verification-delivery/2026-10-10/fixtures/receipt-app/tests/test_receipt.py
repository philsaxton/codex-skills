"""Acceptance examples from REQUEST.md, exercised through the actual CLI."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="receipt-test-")
        self.addCleanup(self.scratch.cleanup)
        self.work = Path(self.scratch.name)
        self.output = self.work / "requested-receipt.json"

    def run_cli(self, input_path, env=None):
        return subprocess.run(
            [sys.executable, str(ROOT / "receipt.py"), str(input_path),
             "--output", str(self.output)],
            cwd=self.work, env=env, text=True, capture_output=True, check=False,
        )

    def write_order(self, order):
        path = self.work / "order.json"
        path.write_text(json.dumps(order), encoding="utf-8")
        return path

    def assert_receipt(self, result, expected):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertTrue(self.output.is_file(), "CLI did not create the requested receipt")
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), expected)
        self.assertEqual(json.loads(result.stdout), expected)

    def test_committed_order_receipt(self):
        result = self.run_cli(ROOT / "inputs/order.json")
        self.assert_receipt(result, {
            "order_id": "order-1042", "currency": "USD", "item_count": 4,
            "subtotal_cents": 1000, "tax_cents": 83, "total_cents": 1083,
        })
        self.assertEqual(list(self.work.iterdir()), [self.output])

    def test_second_order_uses_its_quantities_and_prices(self):
        path = self.write_order({
            "order_id": "order-1043",
            "items": [{"quantity": 3, "unit_price_cents": 333}],
        })
        self.assert_receipt(self.run_cli(path), {
            "order_id": "order-1043", "currency": "USD", "item_count": 3,
            "subtotal_cents": 999, "tax_cents": 82, "total_cents": 1081,
        })

    def test_invalid_quantity_leaves_no_receipt(self):
        for quantity in (0, -1, True, "3"):
            with self.subTest(quantity=quantity):
                path = self.write_order({
                    "order_id": "invalid-order",
                    "items": [{"quantity": quantity, "unit_price_cents": 199}],
                })
                result = self.run_cli(path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("quantity", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertFalse(self.output.exists())

    def test_invalid_json_leaves_no_receipt(self):
        path = self.work / "broken.json"
        path.write_text("{", encoding="utf-8")
        result = self.run_cli(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("receipt error:", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.output.exists())

    def test_unknown_rounding_leaves_no_receipt(self):
        environment = dict(os.environ, RECEIPT_ROUNDING="unknown")
        result = self.run_cli(ROOT / "inputs/order.json", env=environment)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RECEIPT_ROUNDING", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.output.exists())

    def test_down_rounding_is_a_separate_supported_mode(self):
        environment = dict(os.environ, RECEIPT_ROUNDING="down")
        self.assert_receipt(self.run_cli(ROOT / "inputs/order.json", env=environment), {
            "order_id": "order-1042", "currency": "USD", "item_count": 4,
            "subtotal_cents": 1000, "tax_cents": 82, "total_cents": 1082,
        })

    def test_invalid_order_fields_leave_no_receipt(self):
        valid_item = {"quantity": 1, "unit_price_cents": 100}
        for order in (
            {"order_id": "", "items": [valid_item]},
            {"order_id": "invalid", "items": []},
            {"order_id": "invalid", "items": [{"quantity": 1, "unit_price_cents": -1}]},
            {"order_id": "invalid", "items": [{"quantity": 1, "unit_price_cents": True}]},
        ):
            with self.subTest(order=order):
                result = self.run_cli(self.write_order(order))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt error:", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
