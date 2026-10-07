"""Exercise skips with real storage aliases or a labeled symlink stand-in."""
import unittest

import run_recovery_tests as runner


class RecoveryCaseFixtureTests(unittest.TestCase):
    def exercise_alias(self, method, alias, target):
        module = runner.load_module("case_alias_fixture_tests", runner.ROOT / "tests/recovery/test_garage_rebuild.py",
                                    runner.TEST_HASHES["test_garage_rebuild"])
        module.SCRIPT = runner.ROOT / "workspace-setup/scripts/recovery/garage_rebuild.py"

        class AliasedFixture(module.GarageTests):
            def setUp(self):
                super().setUp()
                probe = self.root / "CaseProbe"
                probe.write_text("fixture filesystem probe")
                if not (self.root / "caseprobe").exists():
                    # Case-sensitive storage needs a synthetic alias to reach
                    # the skip branch. On aliasing storage this would self-link.
                    (self.source / alias).symlink_to(target)
                probe.unlink()

        result = unittest.TestResult()
        AliasedFixture(method).run(result)
        self.assertEqual(len(result.skipped), 1, (result.failures, result.errors))
        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])
        self.assertIn("filesystem aliases", result.skipped[0][1])

    def test_file_collision_fixture_skips_when_names_alias(self):
        self.exercise_alias("test_case_collision_refused", "scripts/notes", "Notes")

    def test_directory_collision_fixture_skips_when_names_alias(self):
        self.exercise_alias("test_implicit_ancestor_case_collision_refused", "foo", "Foo")


if __name__ == "__main__":
    unittest.main()
