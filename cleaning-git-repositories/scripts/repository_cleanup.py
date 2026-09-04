#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = 1
SKILL_NAME = "cleaning-git-repositories"
OID_RE = re.compile(r"^[0-9a-f]{40,64}$")


class GitFailure(RuntimeError):
    pass


def run_git(
    repo: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        shell=False,
    )
    if check and result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Git command failed"
        )
        raise GitFailure(message)
    return result


def repository_identity(repo: Path) -> dict[str, str]:
    top = Path(
        run_git(repo, "rev-parse", "--show-toplevel").stdout.strip()
    ).resolve()
    common_raw = run_git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    common = Path(common_raw)
    if not common.is_absolute():
        common = (top / common).resolve()
    return {"top_level": str(top), "common_dir": str(common)}


def validate_integration_ref(repo: Path, name: str) -> tuple[str, str]:
    ref = f"refs/heads/{name}"
    checked = run_git(
        repo, "check-ref-format", "--branch", name, check=False
    )
    oid = run_git(
        repo, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False
    )
    if checked.returncode != 0 or oid.returncode != 0:
        raise ValueError(f"integration branch does not exist locally: {name}")
    return ref, oid.stdout.strip()


def has_symlink_component(path: Path) -> bool:
    absolute = path.absolute()
    return any(part.is_symlink() for part in [absolute, *absolute.parents])


def assert_trusted_installation(script: Path) -> None:
    absolute = script.absolute()
    if has_symlink_component(absolute):
        raise ValueError(
            "apply-local requires a protected non-symlinked installation"
        )
    normalized = absolute.as_posix()
    project_suffix = (
        f"/.agents/skills/{SKILL_NAME}/scripts/repository_cleanup.py"
    )
    admin_path = f"/etc/codex/skills/{SKILL_NAME}/scripts/repository_cleanup.py"
    if not normalized.endswith(project_suffix) and normalized != admin_path:
        raise ValueError(
            "apply-local requires a protected non-symlinked installation"
        )


def build_plan(
    repo: Path, integration: str, protected: Iterable[str]
) -> dict[str, Any]:
    integration_ref, integration_oid = validate_integration_ref(
        repo, integration
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "repository": {
            **repository_identity(repo),
            "integration_ref": integration_ref,
            "integration_oid": integration_oid,
        },
        "protected_branches": sorted(set(protected) | {integration}),
        "worktrees": [],
        "branches": [],
        "remote_tracking_branches": [],
        "retained": [],
        "actions": [],
        "decisions": [],
    }


def render_summary(plan: dict[str, Any]) -> str:
    del plan
    return "# Repository cleanup plan\n\nNo eligible cleanup actions.\n"


def write_plan(path: Path, plan: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        json.dump(plan, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def load_plan(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or malformed cleanup plan")
    return value


def revalidate_plan(plan: dict[str, Any]) -> None:
    del plan
    raise ValueError("cleanup plan application is not implemented")


def apply_plan(plan: dict[str, Any]) -> list[dict[str, str]]:
    revalidate_plan(plan)
    return []


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan and apply conservative local Git repository cleanup."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser(
        "plan", help="inspect a repository and write a cleanup plan"
    )
    plan_parser.add_argument("--repo", type=Path, required=True)
    plan_parser.add_argument("--integration", required=True)
    plan_parser.add_argument("--plan", type=Path, required=True)
    plan_parser.add_argument("--protect", action="append", default=[])

    apply_parser = subparsers.add_parser(
        "apply-local", help="apply a revalidated safe local cleanup plan"
    )
    apply_parser.add_argument("--plan", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.command == "plan":
            plan = build_plan(args.repo, args.integration, args.protect)
            write_plan(args.plan, plan)
            print(render_summary(plan), end="")
            return 0

        assert_trusted_installation(Path(__file__))
        events = apply_plan(load_plan(args.plan))
        print(json.dumps(events, indent=2, sort_keys=True))
        return 0
    except (GitFailure, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
