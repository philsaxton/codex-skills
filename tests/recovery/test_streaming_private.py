"""Bounded streaming and size controls; synthetic files only."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import garage_rebuild as core
import garage_workspace as connector


class StreamingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="garage-stream-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_secret_split_across_chunk_boundary_is_refused(self):
        path = self.root / "payload.bin"
        path.write_bytes(b"\0" * (core.STREAM_CHUNK_BYTES - 12) + b"-----BEGIN OPENSSH PRIVATE KEY-----\nfixture")
        with self.assertRaisesRegex(core.Refusal, "secret"):
            core.stream_file(path, private=True)

    def test_source_mutation_during_streaming_is_refused(self):
        path = self.root / "payload.bin"
        path.write_bytes(b"x" * (core.STREAM_CHUNK_BYTES + 10))
        class MutatingWriter:
            changed = False
            def write(self, data):
                if not self.changed:
                    self.changed = True
                    with path.open("ab") as source:
                        source.write(b"changed")
                return len(data)
        with self.assertRaisesRegex(core.Refusal, "source changed"):
            core.stream_file(path, private=True, output=MutatingWriter())

    def test_private_file_size_limit_is_checked_before_open(self):
        path = self.root / "oversized.zip"
        with path.open("wb") as file:
            file.truncate(core.MAX_PRIVATE_FILE_BYTES + 1)
        with patch.object(core.os, "open", side_effect=AssertionError("oversized file must not be opened")):
            with self.assertRaisesRegex(core.Refusal, "2 GiB"):
                core.stream_file(path, private=True)

    def test_garage_and_connector_caps_are_not_inflated(self):
        self.assertEqual(core.MAX_FILE_BYTES, 128 * 1024 * 1024)
        self.assertEqual(connector.MAX_BLOB_BYTES, 32 * 1024 * 1024)
        self.assertEqual(connector.MAX_BUNDLE_BYTES, 128 * 1024 * 1024)
        path = self.root / "public.zip"
        with path.open("wb") as file:
            file.truncate(core.MAX_FILE_BYTES + 1)
        with self.assertRaisesRegex(core.Refusal, "128 MiB"):
            core.stream_file(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
