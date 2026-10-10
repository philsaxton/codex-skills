#!/usr/bin/env python3
"""Project-local command recorder for the completion-guidance trials."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parent


def state():
    config = json.loads((ROOT / "check-config.json").read_text())
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in config["state_files"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", default="development")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    config = json.loads((ROOT / "check-config.json").read_text())
    command = args.command or config["suite"]
    if command[0] == "--":
        command = command[1:]
    (ROOT / "evidence").mkdir(exist_ok=True)
    run_id = uuid.uuid4().hex
    started = time.monotonic()
    record = {"id": run_id, "actor": (ROOT / ".owner").read_text().strip(),
              "stage": args.stage, "command": command, "state": state(),
              "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "environment": {"python": platform.python_version(), "platform": platform.system(),
                              "node": config.get("node_version"), "dependencies": "standard library only"}}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    local_scratch = ROOT / "scratch"
    local_scratch.mkdir(exist_ok=True)
    # This is a disposable project-output directory, not a Git worktree.
    env.update(TMPDIR=str(local_scratch), TMP=str(local_scratch), TEMP=str(local_scratch))
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    record.update(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                  elapsed_seconds=time.monotonic() - started)
    path = ROOT / "evidence" / f"{run_id}.json"
    path.write_text(json.dumps(record, indent=2) + "\n")
    with (ROOT / "evidence" / "commands.jsonl").open("a") as log:
        log.write(json.dumps({k: v for k, v in record.items() if k not in ("stdout", "stderr")}) + "\n")
    print(proc.stdout, end="")
    print(proc.stderr, end="", file=sys.stderr)
    print(f"Evidence: {path}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
