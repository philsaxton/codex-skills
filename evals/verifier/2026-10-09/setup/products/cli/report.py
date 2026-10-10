#!/usr/bin/env python3
"""Write a paid-invoice summary as JSON."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys


def read_rows(path):
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                amount = Decimal(row["amount"])
                if not amount.is_finite():
                    raise InvalidOperation
            except (InvalidOperation, ValueError):
                raise ValueError(f"invalid amount for invoice {row['invoice_id']}") from None
            rows.append({**row, "amount": amount})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        rows = read_rows(args.input)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    paid = [row for row in rows if row["status"] == "paid"]
    total = sum((row["amount"] for row in paid), Decimal("0.00"))
    args.output.write_text(json.dumps({"paid_count": len(paid), "paid_total": f"{total:.2f}"}) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
