"""Read an order and write its receipt. All money values are integer cents."""

import argparse
import json
import os
from pathlib import Path
import sys

from tax_rules import tax_cents


def make_receipt(order, rounding):
    if not isinstance(order, dict):
        raise ValueError("order must be a JSON object")
    order_id = order.get("order_id")
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("order_id must be a nonempty string")
    items = order.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("items must be a nonempty list")
    subtotal = 0
    item_count = 0
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")
        quantity = item.get("quantity")
        price = item.get("unit_price_cents")
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        if type(price) is not int or price < 0:
            raise ValueError("unit_price_cents must be a nonnegative integer")
        item_count += quantity
        subtotal += quantity * price
    tax = tax_cents(subtotal, rounding)
    return {
        "order_id": order_id,
        "currency": "USD",
        "item_count": item_count,
        "subtotal_cents": subtotal,
        "tax_cents": tax,
        "total_cents": subtotal + tax,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        order = json.loads(args.input.read_text(encoding="utf-8"))
        receipt = make_receipt(order, os.environ.get("RECEIPT_ROUNDING", "half_up"))
        rendered = json.dumps(receipt, sort_keys=True) + "\n"
        args.output.write_text(rendered, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"receipt error: {error}", file=sys.stderr)
        return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
