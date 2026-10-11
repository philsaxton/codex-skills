"""Compare the actual receipt with a separately supplied partner system export."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--partner-export", type=Path, required=True)
    args = parser.parse_args()
    try:
        actual = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(actual, dict):
            raise ValueError("actual receipt must be a JSON object")
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "failed", "reason": f"invalid actual receipt: {error}"}))
        return 1
    try:
        partner = json.loads(args.partner_export.read_text(encoding="utf-8"))
        if not isinstance(partner, dict) or set(partner) != set(actual):
            raise ValueError("partner export is not a receipt with the required fields")
    except (OSError, ValueError) as error:
        print(json.dumps({
            "status": "unavailable", "scope": "partner acceptance",
            "reason": f"required partner system export unavailable: {error}",
        }))
        return 2
    if actual != partner:
        print(json.dumps({"status": "failed", "scope": "partner acceptance", "reason": "receipt differs from partner export"}))
        return 1
    print(json.dumps({"status": "passed", "scope": "comparison with supplied partner export"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
