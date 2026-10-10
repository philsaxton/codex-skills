#!/usr/bin/env python3
"""Check the supplied catalog's input shape."""
import json
from pathlib import Path

catalog = json.loads((Path(__file__).resolve().parents[1] / "data/catalog.json").read_text())
assert catalog and all(isinstance(key, str) and key for key in catalog)
assert all(type(value) is int and value > 0 for value in catalog.values())
print(f"Catalog shape OK ({len(catalog)} items)")
