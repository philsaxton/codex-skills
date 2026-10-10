#!/usr/bin/env python3
"""Check fixture setup, not candidate skills; browser checks stop at HTTP serving."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import urlopen

from setup import materialize


def command(project, args):
    scratch = project / "scratch"
    scratch.mkdir(exist_ok=True)
    env = {**os.environ, "TMPDIR": str(scratch), "TMP": str(scratch),
           "TEMP": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, *args], cwd=project, env=env,
                            capture_output=True, text=True, timeout=15)
    return {"argv": [sys.executable, *args], "exit": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def request(url):
    try:
        response = urlopen(url, timeout=3)
    except HTTPError as error:
        response = error
    with response:
        body = response.read().decode()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        return {"status": response.status, "body": body}


@contextmanager
def server(project, program, evidence):
    scratch = project / "scratch"
    scratch.mkdir(exist_ok=True)
    port_file = scratch / "server.port"
    log_file = scratch / "server.log"
    env = {**os.environ, "TMPDIR": str(scratch), "TMP": str(scratch),
           "TEMP": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"}
    with log_file.open("w") as log:
        process = subprocess.Popen([sys.executable, program, "--port", "0", "--port-file", str(port_file)],
                                   cwd=project, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 5
            while not port_file.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            if not port_file.exists() or process.poll() is not None:
                raise RuntimeError(f"server unavailable: {log_file.read_text()}")
            yield f"http://127.0.0.1:{int(port_file.read_text())}"
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            evidence["server_exit"] = process.returncode
            evidence["server_stopped"] = process.poll() is not None
            evidence["server_log"] = log_file.read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="new disposable directory")
    parser.add_argument("--report", required=True, type=Path, help="retained JSON outside --work")
    args = parser.parse_args()
    work, report = args.work.resolve(), args.report.resolve()
    if work.exists() or work == report or work in report.parents:
        parser.error("work must be new and report must be outside it")
    work.mkdir(parents=True)
    results = {"started_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
               "work": str(work), "browser_ui_exercised": False, "cases": []}

    def record(case, variant):
        item = {"case": case, "variant": variant, "checks": []}
        results["cases"].append(item)
        return materialize(case, variant, work / f"{case}-{variant}"), item

    def check(item, name, observed, expected):
        item["checks"].append({"name": name, "observed": observed, "expected": expected,
                               "matches_oracle": observed == expected})

    try:
        for variant, expected_total, test_exit in (("good", "19.75", 0), ("wrong-total", "198.75", 1)):
            project, item = record("cli", variant)
            item["unit_tests"] = command(project, ["-m", "unittest", "discover", "-s", "tests", "-v"])
            check(item, "existing suite exit", item["unit_tests"]["exit"], test_exit)
            item["manual"] = command(project, ["report.py", "--input", "data/invoices.csv", "--output", "scratch/report.json"])
            check(item, "report command exit", item["manual"]["exit"], 0)
            check(item, "observable report", json.loads((project / "scratch/report.json").read_text()),
                  {"paid_count": 2, "paid_total": expected_total})

        project = work / "cli-good"
        verification = project / "verification"
        verification.mkdir()
        (verification / "method.txt").write_text("retained verification method\n")
        previous_hash = hashlib.sha256((project / "report.py").read_bytes()).hexdigest()
        materialize("cli", "wrong-total", project, update=True)
        results["update_preserves_method"] = (verification / "method.txt").read_text() == "retained verification method\n"
        results["update_changes_product"] = previous_hash != hashlib.sha256((project / "report.py").read_bytes()).hexdigest()

        for variant in ("good", "discount-regression", "route-change", "route-and-regression", "missing-catalog"):
            project, item = record("http", variant)
            if variant == "missing-catalog":
                item["startup"] = command(project, ["server.py", "--port", "0", "--port-file", "scratch/server.port"])
                check(item, "unavailable prerequisite exit", item["startup"]["exit"], 78)
                check(item, "no server port published", (project / "scratch/server.port").exists(), False)
                continue
            item["catalog_check"] = command(project, ["checks/check_catalog.py"])
            check(item, "catalog shape exit", item["catalog_check"]["exit"], 0)
            route = json.loads((project / "api.json").read_text())["quote_path"]
            regression = "regression" in variant
            with server(project, "server.py", item) as origin:
                for sku, quantity, price in (("mug", 1, 2500), ("mug", 2, 2500), ("mug", 3, 2500), ("tea", 3, 1200)):
                    discount = 10 if quantity >= (4 if regression else 3) else 0
                    check(item, f"{sku} quantity {quantity}", request(f"{origin}{route}?sku={sku}&quantity={quantity}"),
                          {"status": 200, "body": {"sku": sku, "quantity": quantity, "unit_price_cents": price,
                           "discount_percent": discount, "total_cents": price * quantity * (100 - discount) // 100}})
                for quantity in ("", "0", "-1", "1.5"):
                    suffix = f"&quantity={quantity}" if quantity else ""
                    check(item, f"invalid quantity {quantity!r}", request(f"{origin}{route}?sku=mug{suffix}"),
                          {"status": 400, "body": {"error": "invalid_quantity"}})
                check(item, "unknown SKU", request(f"{origin}{route}?sku=absent&quantity=1"),
                      {"status": 404, "body": {"error": "unknown_sku"}})
                if route != "/v1/quote":
                    check(item, "old route", request(f"{origin}/v1/quote?sku=mug&quantity=3"),
                          {"status": 404, "body": {"error": "not_found"}})

        for variant in ("good", "persistence-regression"):
            project, item = record("browser", variant)
            item["scope"] = "HTTP serving only; JavaScript and UI were not exercised"
            with server(project, "serve.py", item) as origin:
                page = request(origin + "/")
                check(item, "page status", page["status"], 200)
                check(item, "title", "<title>Receipt preferences</title>" in page["body"], True)
                for asset in ("app.js", "style.css"):
                    response = request(origin + "/" + asset)
                    check(item, asset + " status", response["status"], 200)
                    check(item, asset + " exact served bytes", response["body"], (project / asset).read_text())
    except Exception as error:
        results["error"] = f"{type(error).__name__}: {error}"
    results["completed_utc"] = datetime.now(timezone.utc).isoformat()
    results["setup_matches_oracle"] = ("error" not in results and results.get("update_preserves_method", False)
        and results.get("update_changes_product", False)
        and all(check["matches_oracle"] for item in results["cases"] for check in item["checks"]))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"setup_matches_oracle": results["setup_matches_oracle"],
                      "browser_ui_exercised": False, "report": str(report), "scratch_retained": str(work)}))
    return 0 if results["setup_matches_oracle"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
