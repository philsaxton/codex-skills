#!/usr/bin/env python3
"""Create the fixed, minimal layout for a new garage workspace."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


GITIGNORE = """/apps/
/artifacts/
/tmp/
/.worktrees/
"""

README = """# Agent workspace

This workspace keeps application repositories, generated work, and workspace governance separate.

- Clone independent application repositories under `apps/`.
- Put generated reports and other runtime work under `artifacts/`.
- Keep workspace-wide guidance in `AGENTS.md`.
- Put lasting workspace plans, migration contracts and decisions in `docs/`; workspace documents, including nested paths and other formats, are eligible for garage tracking by default. Application-specific documentation belongs in its application repository.
- Use `tmp/<task>/` for disposable task scratch and `.worktrees/<app>/<task>/` for application worktrees. Both stay ignored.

Use a unique `tmp/<task>/` directory for disposable work and supported temporary-directory settings for tools that honor them. Stop writers and inspect the exact task directory before cleanup; keep deliverables, repositories, and recovery evidence elsewhere. An installed scratch-maintenance skill may provide a helper, but none is copied into this workspace.

Applications should remain usable from an independent checkout. Configure their output locations through supported flags, environment variables, or settings rather than hard-coding this workspace path.

Designate one authoritative migration document, for example `docs/migration.md`, and link it here or in `AGENTS.md` when created. Mark handoff/recovery copies as snapshots with their source revision or content identity and a pointer to the authoritative record; document location changes. Retained generated reports belong in `artifacts/`, disposable work in `tmp/`. Keep migration contracts and recovery evidence out of scratch. Review documentation before staging; keep machine-local or sensitive recovery data retained outside scratch and ignored unless deliberately selected for tracking.
"""

AGENTS = """# Workspace instructions

- `apps/` contains independent application repositories. Before editing an application, read its own README, contributor documentation, and applicable instructions. Those application documents are authoritative for application work.
- Preserve each application's independent Git repository, history, and origin. Do not add application contents or runtime outputs to the workspace repository.
- Classify documents by purpose, not by being agent-generated. Lasting workspace organization plans, migration contracts and decisions default to tracked `docs/`; application-specific docs stay with the app. Workspace documents and support files are eligible by default. Add narrow ignore rules for private or generated content, and inspect content before staging.
- Identify one authoritative migration document and link it from root guidance. Label handoff/recovery copies as snapshots with source revision/content identity and the authoritative location. Record location transitions and reconcile with the current authoritative record before resuming. Keep contracts and recovery evidence out of disposable scratch; retain machine-local or sensitive evidence outside scratch and ignored unless intentionally selected for tracking.
- `artifacts/` contains generated reports, exchanges, and runtime work. Keep outputs outside product source by using each application's supported flags, environment variables, or settings.
- Use unique `tmp/<task>/` directories and supported temporary-directory settings for disposable task work. Keep deliverables, recovery evidence, repositories, and other tasks' data outside your scratch. Before cleanup, stop writers, inspect the exact directory, and retain anything needed. Never clean worktrees as scratch.
- Create requested application worktrees under `.worktrees/<app>/<task>/`, using the owning application's Git repository and collision-free paths. Preserve existing worktrees; inspect shared Git metadata access as well as destination access. Remove worktrees through Git-aware cleanup after checking active use, changes, locks and merge status.
- Check effective write permissions; these locations do not override protected paths or host-managed worktree placement.
- The root Git repository makes workspace files eligible for tracking by default. Explicitly ignore application and runtime directories: `/apps/`, `/artifacts/`, `/tmp/`, and `/.worktrees/`. Adapt application exclusions to the chosen layout; do not add application files or Git links to the outer index.
"""

FILES = {
    ".gitignore": GITIGNORE,
    "AGENTS.md": AGENTS,
    "README.md": README,
}
DIRECTORIES = ("apps", "docs", "artifacts", "tmp", ".worktrees")
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
