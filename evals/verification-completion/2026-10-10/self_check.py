#!/usr/bin/env python3
"""Check fixture identities and seeded behavior, separately from model trials."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.bundle / "manifest.json").read_text())
    out = args.bundle / "preflight"
    out.mkdir()
    checks = []
    groups = {}
    for row in manifest["runs"]:
        groups.setdefault((row["fixture"], row["condition"]), []).append(row)
    for key, rows in groups.items():
        states = [{name: hashlib.sha256((Path(row["root"]) / "project" / name).read_bytes()).hexdigest()
                   for name in row["state_files"]} for row in rows]
        assert states[0] == states[1] == states[2], key
        assert all(row["initial_receipt"]["exit_code"] == 0 for row in rows), key
        checks.append({"case": key, "matching_states": True, "initial_suites_pass": True})
    stale = next(row for row in manifest["runs"] if row["condition"] == "stale")
    target = out / "stale-project"
    shutil.copytree(Path(stale["root"]) / "project", target)
    (target / ".owner").write_text("fixture-self-check\n")
    proc = subprocess.run([sys.executable, "check.py"], cwd=target, capture_output=True, text=True)
    assert proc.returncode == 1, (proc.returncode, proc.stdout, proc.stderr)
    assert "drawing a fourth possessed legit business" in proc.stdout
    checks.append({"case": "changed prototype", "exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr})
    gap = next(row for row in manifest["runs"] if row["condition"] == "coverage")
    target = out / "coverage-project"
    shutil.copytree(Path(gap["root"]) / "project", target)
    (target / ".owner").write_text("fixture-self-check\n")
    invalid = target / "scratch/nonfinite.csv"
    invalid.write_text("invoice_id,status,amount\nA,paid,NaN\n")
    report = target / "scratch/nonfinite.json"
    command = [sys.executable, "check.py", "--", sys.executable, "report.py", "--input", str(invalid), "--output", str(report)]
    proc = subprocess.run(command, cwd=target, capture_output=True, text=True)
    assert proc.returncode == 0 and json.loads(report.read_text())["paid_total"] == "NaN"
    checks.append({"case": "uncovered invalid input", "required_exit": 2, "actual_exit": proc.returncode,
                   "actual_report": json.loads(report.read_text()), "stdout": proc.stdout, "stderr": proc.stderr})
    for row in manifest["runs"]:
        if row["condition"] == "missing":
            path = Path(row["root"]) / "project/evidence" / (row["initial_receipt"]["id"] + ".json")
            assert not path.exists()
    checks.append({"case": "missing output", "all_three_missing": True})
    (out / "results.json").write_text(json.dumps({"checks": checks, "passed": True}, indent=2) + "\n")
    print(json.dumps({"passed": True, "checks": len(checks), "report": str(out / "results.json")}))


if __name__ == "__main__":
    main()
