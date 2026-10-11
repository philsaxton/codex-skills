"""Build the executable archive from explicit source and packaging inputs."""

import argparse
from pathlib import Path
import shutil
import sys
import tempfile
import zipapp

ROOT = Path(__file__).resolve().parent


def build(output):
    inputs = {
        "__main__.py": ROOT / "packaging/__main__.py",
        "receipt.py": ROOT / "receipt.py",
        "tax_rules.py": ROOT / "tax_rules.py",
    }
    for source in inputs.values():
        if not source.is_file():
            raise FileNotFoundError(f"required package input is missing: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="receipt-build-") as scratch:
        staging = Path(scratch) / "source"
        staging.mkdir()
        for name, source in inputs.items():
            shutil.copyfile(source, staging / name)
        archive = Path(scratch) / "receipt.pyz"
        zipapp.create_archive(staging, target=archive, interpreter="/usr/bin/env python3")
        shutil.copy2(archive, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build/receipt.pyz")
    args = parser.parse_args()
    try:
        build(args.output)
    except (OSError, ValueError) as error:
        print(f"build error: {error}", file=sys.stderr)
        return 1
    print(f"built {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
