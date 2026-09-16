import csv
import io
import unittest
from export import export

class ExportTests(unittest.TestCase):
    def test_formats_round_trip(self):
        rows = [["name", "note"], ["a,b", "tab\there"], ["quote\"", "two\nlines"], ["", "snowman ☃"]]
        for fmt, delimiter in [("csv", ","), ("tsv", "\t")]:
            with self.subTest(format=fmt):
                actual = list(csv.reader(io.StringIO(export(rows, fmt), newline=""), delimiter=delimiter))
                self.assertEqual(rows, actual)
    def test_csv_bytes(self):
        self.assertEqual(export([["a,b", "c"]]), '"a,b",c\n')
    def test_unknown_format(self):
        with self.assertRaises(KeyError):
            export([["x"]], "html")
