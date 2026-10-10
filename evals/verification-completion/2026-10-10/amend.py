#!/usr/bin/env python3
"""Apply the disclosed fixture amendment without altering original trial inputs."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
import setup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("application", "superpowers", "city", "bundle"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    manifest_path = args.bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if len(manifest["runs"]) != 21:
        raise SystemExit("Amend only the original 21-input bundle once")
    shutil.copy2(manifest_path, args.bundle / "original-manifest.json")
    for row in manifest["runs"]:
        if row["condition"] == "stage":
            assert not (Path(row["root"]) / "project/review/REPORT.md").exists()
            row["status"] = "superseded-before-dispatch"
            row["reason"] = "Prototype not a clean acceptance fixture; see protocol amendment"
    source = (args.superpowers / "skills/subagent-driven-development/task-reviewer-prompt.md").read_text()
    block = textwrap.dedent(source[source.index("    ## Tests\n"):source.index("    ## Part 1: Spec Compliance")])
    for number, arm, kind, condition in [(22, "A", "cli", "stage"), (23, "B", "cli", "stage"), (24, "C", "cli", "stage"),
                                          (25, "B", "store", "intact"), (26, "C", "store", "intact"), (27, "A", "store", "intact")]:
        root = args.bundle / "runs" / f"run-{number:02d}"
        root.mkdir()
        setup.guidance(root, arm, args.application, args.superpowers, block)
        prepared = setup.prepare_project(root / "project", kind, condition, args.application, args.city)
        setup.write(root / "TASK.md", setup.task(root, "reviewer"))
        setup.write(root / "CONTROLLER_TASK.md", setup.task(root, "controller"))
        setup.write(root / "project/.owner", "reviewer\n")
        prepared["initial_protected_hashes"][".owner"] = setup.digest(root / "project/.owner")
        manifest["runs"].append(dict(id=root.name, arm=arm, fixture=kind, condition=condition, root=str(root),
                                     amendment=True, guidance_hashes={str(p.relative_to(root / "guidance")): setup.digest(p) for p in (root / "guidance").rglob("*") if p.is_file()}, **prepared))
    manifest["amendment_recorded_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    setup.write(manifest_path, json.dumps(manifest, indent=2) + "\n")
    setup.write(args.bundle / "amended-protocol.md", (setup.HERE / "protocol.md").read_text())
    # Validate the new method against a real persistence defect in a separate copy.
    control = args.bundle / "preflight/store-mutation"
    shutil.copytree(args.bundle / "runs/run-25/project", control)
    product = control / "store.py"
    product.write_text(product.read_text().replace("INSERT OR IGNORE", "INSERT OR REPLACE"))
    (control / ".owner").write_text("fixture-self-check\n")
    proc = subprocess.run([sys.executable, "check.py"], cwd=control, capture_output=True, text=True)
    assert proc.returncode == 1 and "test_duplicate_preserves_original_amount" in proc.stderr
    setup.write(args.bundle / "preflight/store-mutation.json", json.dumps({"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "detected": True}, indent=2) + "\n")
    print(json.dumps({"added": 6, "superseded_before_dispatch": 3, "mutation_detected": True}))


if __name__ == "__main__":
    main()
