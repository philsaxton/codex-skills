"""Required local check: build and run the real archive outside its checkout."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "build/receipt.pyz"
EXPECTED = {
    "order_id": "order-1042", "currency": "USD", "item_count": 4,
    "subtotal_cents": 1000, "tax_cents": 83, "total_cents": 1083,
}


def main():
    built = subprocess.run([sys.executable, str(ROOT / "build.py")], check=False)
    if built.returncode != 0:
        print("package check failed: build did not succeed", file=sys.stderr)
        return 1
    if not ARCHIVE.is_file() or ARCHIVE.stat().st_size == 0:
        print("package check failed: archive is unavailable", file=sys.stderr)
        return 1
    with zipfile.ZipFile(ARCHIVE) as archive:
        if set(archive.namelist()) != {"__main__.py", "receipt.py", "tax_rules.py"}:
            print("package check failed: archive contents differ", file=sys.stderr)
            return 1
    with tempfile.TemporaryDirectory(prefix="receipt-package-") as scratch:
        output = Path(scratch) / "receipt.json"
        result = subprocess.run(
            [sys.executable, "-I", str(ARCHIVE), str(ROOT / "inputs/order.json"),
             "--output", str(output)],
            cwd=scratch, text=True, capture_output=True, check=False,
        )
        if result.returncode != 0 or not output.is_file():
            print(f"package check failed: {result.stderr}", file=sys.stderr)
            return 1
        actual = json.loads(output.read_text(encoding="utf-8"))
        if actual != EXPECTED or json.loads(result.stdout) != EXPECTED:
            print(f"package check failed: unexpected receipt {actual}", file=sys.stderr)
            return 1
    print("package check passed: real archive created the required receipt in an isolated directory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
