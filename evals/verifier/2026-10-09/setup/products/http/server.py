#!/usr/bin/env python3
"""Local catalog quote service."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import parse_qs, urlsplit


def make_handler(catalog, quote_path):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, payload):
            body = (json.dumps(payload) + "\n").encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlsplit(self.path)
            if url.path != quote_path:
                self.send_json(404, {"error": "not_found"})
                return
            query = parse_qs(url.query, keep_blank_values=True)
            raw_quantity = query.get("quantity", [""])[0]
            if not raw_quantity.isdecimal() or int(raw_quantity) < 1:
                self.send_json(400, {"error": "invalid_quantity"})
                return
            quantity = int(raw_quantity)
            sku = query.get("sku", [""])[0]
            if sku not in catalog:
                self.send_json(404, {"error": "unknown_sku"})
                return
            unit_price = catalog[sku]
            discount = 10 if quantity >= 3 else 0
            total = unit_price * quantity * (100 - discount) // 100
            self.send_json(200, {"sku": sku, "quantity": quantity,
                "unit_price_cents": unit_price, "discount_percent": discount,
                "total_cents": total})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--port-file", type=Path)
    parser.add_argument("--catalog", type=Path, default=Path("data/catalog.json"))
    parser.add_argument("--api", type=Path, default=Path("api.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text())
        quote_path = json.loads(args.api.read_text())["quote_path"]
        if not catalog or not all(type(value) is int and value > 0 for value in catalog.values()):
            raise ValueError("catalog must contain positive integer prices")
        if not isinstance(quote_path, str) or not quote_path.startswith("/"):
            raise ValueError("quote_path must start with /")
    except (OSError, ValueError, KeyError) as error:
        print(f"prerequisite unavailable: {error}", file=sys.stderr)
        return 78
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(catalog, quote_path))
    port = server.server_address[1]
    if args.port_file:
        args.port_file.parent.mkdir(parents=True, exist_ok=True)
        args.port_file.write_text(str(port) + "\n")
    print(f"Serving quote API at http://127.0.0.1:{port}{quote_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
