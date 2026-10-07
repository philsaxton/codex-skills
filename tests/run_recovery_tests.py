#!/usr/bin/env python3
"""Run unchanged recovery-release tests against the single bundled implementation.

Use --list to inspect discovery without executing the synthetic recovery tests.
"""
import argparse
import hashlib
from pathlib import Path
import sys
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_HASHES = {
    "test_garage_rebuild": "f9272791370b4dfd0f72ab952508ad260458e47fe1ee1fc3d5084668de0b0309",
    "test_connector_workspace": "cb3119573f46dc7e40a257d8957ee22891c7012b4885bcfb6d68fd562cf1da33",
    "test_streaming_private": "4edd5715ff1c486bc097580ec72b44b1bc2dc4bb8cac474a63c9fe55e84d6008",
}


def load_module(name, path, expected=None):
    raw = path.read_bytes()
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError("Preserved recovery test hash mismatch")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    helper = load_module("cloud_readiness_for_tests", ROOT / "workspace-setup/scripts/check_cloud_readiness.py")
    dependency = ROOT / "workspace-setup/scripts/recovery"
    core, connector = helper.dependency(dependency)
    sys.modules["garage_rebuild"], sys.modules["garage_workspace"] = core, connector
    suite = unittest.TestSuite()
    for name, expected in TEST_HASHES.items():
        module = load_module(name, ROOT / "tests/recovery" / (name + ".py"), expected)
        # Preserve the original test bytes while binding their CLI constants to
        # the same implementation used by in-process imports. No copied mirror.
        if name == "test_garage_rebuild":
            module.SCRIPT = dependency / "garage_rebuild.py"
        if name == "test_connector_workspace":
            module.SCRIPT = dependency / "garage_workspace.py"
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    if args.list:
        for case in cases(suite):
            print(case.id())
        return 0
    return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
