#!/usr/bin/env python3
"""Create the fixed, minimal layout for a new garage workspace."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


GITIGNORE = """/*
!/.gitignore
!/AGENTS.md
!/README.md
"""

README = """# Agent workspace

This workspace keeps application repositories, generated work, and workspace governance separate.

- Clone independent application repositories under `apps/`.
- Put generated reports and other runtime work under `artifacts/`.
- Keep workspace-wide guidance in `AGENTS.md`.

Applications should remain usable from an independent checkout. Configure their output locations through supported flags, environment variables, or settings rather than hard-coding this workspace path.
"""

AGENTS = """# Workspace instructions

- `apps/` contains independent application repositories. Before editing an application, read its own README, contributor documentation, and applicable instructions. Those application documents are authoritative for application work.
- Preserve each application's independent Git repository, history, and origin. Do not add application contents or generated work to the workspace repository.
- `artifacts/` contains generated reports, exchanges, and runtime work. Keep outputs outside product source by using each application's supported flags, environment variables, or settings.
- The root Git repository owns only `.gitignore`, `AGENTS.md`, and `README.md` by default.
"""

FILES = {
    ".gitignore": GITIGNORE,
    "AGENTS.md": AGENTS,
    "README.md": README,
}
DIRECTORIES = ("apps", "artifacts")
GIT_ENVIRONMENT_VARIABLES = (
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
)


class PreflightError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set up a new, minimal garage workspace (dry run by default)."
    )
    parser.add_argument("target", help="absent or empty directory to initialize")
    parser.add_argument(
        "--apply", action="store_true", help="create the workspace described by the dry run"
    )
    return parser.parse_args()


def git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in GIT_ENVIRONMENT_VARIABLES:
        environment.pop(name, None)
    return environment


def existing_anchor(target: Path) -> Path:
    candidate = target
    while not candidate.exists():
        if candidate == candidate.parent:
            raise PreflightError(f"no existing parent directory for {target}")
        candidate = candidate.parent
    if not candidate.is_dir():
        candidate = candidate.parent
    return candidate


def reject_symlink_components(raw_target: str) -> None:
    path = Path(raw_target)
    if not path.is_absolute():
        path = Path.cwd() / path
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise PreflightError(f"target crosses symbolic link: {current}")


def is_bare_repository(path: Path, environment: dict[str, str]) -> bool:
    result = subprocess.run(
        ["git", f"--git-dir={path}", "rev-parse", "--is-bare-repository"],
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def reject_git_ownership(target: Path) -> None:
    environment = git_environment()
    anchor = existing_anchor(target)
    discovered = subprocess.run(
        ["git", "-C", os.fspath(anchor), "rev-parse", "--absolute-git-dir"],
        text=True,
        capture_output=True,
        check=False,
        env=environment,
    )
    if discovered.returncode == 0:
        raise PreflightError(f"target is owned by an existing Git repository: {anchor}")

    for ancestor in (anchor, *anchor.parents):
        git_entry = ancestor / ".git"
        if git_entry.exists() or git_entry.is_symlink() or is_bare_repository(ancestor, environment):
            raise PreflightError(f"target is owned by an existing Git repository: {ancestor}")


def preflight(raw_target: str) -> Path:
    reject_symlink_components(raw_target)
    target = Path(os.path.abspath(raw_target))
    if target.exists():
        if not target.is_dir():
            raise PreflightError(f"target is not a directory: {target}")
        if any(target.iterdir()):
            raise PreflightError(f"target directory is not empty: {target}")
    elif not target.parent.is_dir():
        raise PreflightError(f"target parent directory does not exist: {target.parent}")
    reject_git_ownership(target)
    return target


def print_plan(target: Path, applying: bool) -> None:
    mode = "apply" if applying else "dry run"
    print(f"Workspace setup ({mode})")
    print(f"Target: {target}")
    print("Initialize an empty Git repository with no template hooks")
    for name in FILES:
        print(f"Create: {target / name}")
    for name in DIRECTORIES:
        print(f"Create: {target / name}/")


def apply_scaffold(target: Path) -> None:
    if not target.exists():
        target.mkdir()
    subprocess.run(
        ["git", "-C", os.fspath(target), "init", "--quiet", "--template="],
        check=True,
        env=git_environment(),
    )
    for name, content in FILES.items():
        with (target / name).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    for name in DIRECTORIES:
        (target / name).mkdir()


def main() -> int:
    args = parse_args()
    try:
        target = preflight(args.target)
        print_plan(target, args.apply)
        if args.apply:
            apply_scaffold(target)
            print("Workspace created; files remain unstaged and no remote was configured.")
        else:
            print("No changes made. Re-run with --apply to create this workspace.")
    except (OSError, PreflightError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
