from pathlib import Path
import tempfile
import unittest
from store import EventStore


class StoreBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "events.sqlite"
        self.store = EventStore(self.path)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def test_commit_survives_reopen(self):
        self.assertTrue(self.store.record("alpha", 17))
        self.store.close()
        self.store = EventStore(self.path)
        self.assertEqual(self.store.entries(), [("alpha", 17)])

    def test_duplicate_preserves_original_amount(self):
        self.assertTrue(self.store.record("alpha", 17))
        self.assertFalse(self.store.record("alpha", 99))
        self.assertEqual(self.store.entries(), [("alpha", 17)])

    def test_entries_sorted_by_exact_id(self):
        self.store.record("z", 5)
        self.store.record("a", 8)
        self.store.record(" a ", 3)
        self.assertEqual(self.store.entries(), [(" a ", 3), ("a", 8), ("z", 5)])

    def test_invalid_ids_leave_existing_rows_unchanged(self):
        self.store.record("saved", 5)
        for event_id in ("", "  ", None, 7):
            with self.subTest(event_id=event_id):
                with self.assertRaises(ValueError):
                    self.store.record(event_id, 3)
                self.assertEqual(self.store.entries(), [("saved", 5)])

    def test_amount_validation_and_boundaries(self):
        self.assertTrue(self.store.record("minimum", 1))
        self.assertTrue(self.store.record("maximum", 2**63 - 1))
        expected = [("maximum", 9223372036854775807), ("minimum", 1)]
        for amount in (0, -1, 2**63, 1.5, True, "5", None):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.store.record("bad", amount)
                self.assertEqual(self.store.entries(), expected)

    def test_independent_open_connection_observes_committed_write(self):
        other = EventStore(self.path)
        try:
            self.assertEqual(other.entries(), [])
            self.store.record("later", 9)
            self.assertEqual(other.entries(), [("later", 9)])
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
