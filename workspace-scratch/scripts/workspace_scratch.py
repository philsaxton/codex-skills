#!/usr/bin/env python3
"""Manage named disposable tasks under an explicit workspace/tmp (POSIX)."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import stat
import sys


MARKER = ".scratch-state.json"
DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class Refusal(RuntimeError):
    pass


@contextmanager
def open_directory(name: str, parent: int | None = None):
    fd = os.open(name, DIRECTORY_FLAGS, dir_fd=parent)
    try:
        yield fd
    finally:
        os.close(fd)


@contextmanager
def open_absolute_directory(path: Path):
    """Open each component without following symlinks, including ancestors."""
    fd = os.open(path.anchor, DIRECTORY_FLAGS)
    try:
        for part in path.parts[1:]:
            next_fd = os.open(part, DIRECTORY_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        yield fd
    finally:
        os.close(fd)


def signature(info: os.stat_result) -> tuple:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def inventory(fd: int, device: int) -> dict:
    names = set(os.listdir(fd))
    if names & {".git", ".worktrees", ".worktree"} or {"HEAD", "objects", "refs"} <= names:
        raise Refusal("repository or worktree content is not disposable scratch")
    result = {}
    for name in sorted(names):
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if info.st_dev != device:
            raise Refusal("scratch crosses a filesystem boundary")
        if stat.S_ISDIR(info.st_mode):
            with open_directory(name, fd) as child:
                if signature(os.fstat(child)) != signature(info):
                    raise Refusal("directory changed during inspection")
                result[name] = (signature(info), inventory(child, device))
        elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            result[name] = (signature(info), None)
        else:
            raise Refusal("symlinks, hard links and special files are not supported")
    return result


def read_state(fd: int, task: str) -> tuple[dict, tuple]:
    marker_fd = os.open(MARKER, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(marker_fd, "r") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > 4096:
            raise Refusal("invalid scratch ownership marker")
        state = json.load(stream)
    if state not in (
        {"version": 1, "task": task, "state": "active"},
        {"version": 1, "task": task, "state": "complete"},
    ):
        raise Refusal("directory was not created for this scratch task")
    return state, signature(info)


def write_state(fd: int, task: str, state: str, *, create: bool = False):
    flags = os.O_WRONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    if create:
        flags |= os.O_CREAT | os.O_EXCL
    marker_fd = os.open(MARKER, flags, 0o600, dir_fd=fd)
    with os.fdopen(marker_fd, "w") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise Refusal("invalid scratch ownership marker")
        stream.truncate(0)
        json.dump({"version": 1, "task": task, "state": state}, stream)
        stream.write("\n")


def remove_inventory(fd: int, entries: dict):
    """Delete only inspected entries, using pinned directory descriptors."""
    if set(os.listdir(fd)) != set(entries):
        raise Refusal("scratch entries changed after inspection")
    # Keep the ownership marker until the other contents have been removed.
    for name in sorted(entries, key=lambda item: (item == MARKER, item)):
        if name == MARKER and set(os.listdir(fd)) != {MARKER}:
            raise Refusal("new entries appeared; retaining ownership marker")
        expected, children = entries[name]
        actual = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if signature(actual) != expected:
            raise Refusal("scratch changed during cleanup; partial removal may have occurred")
        if children is None:
            os.unlink(name, dir_fd=fd)
        else:
            with open_directory(name, fd) as child:
                if signature(os.fstat(child)) != expected:
                    raise Refusal("directory changed during cleanup")
                remove_inventory(child, children)
            # Never follow a replaced path when retiring a directory.
            current = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if signature(current)[:3] != expected[:3]:
                raise Refusal("directory replaced during cleanup")
            os.rmdir(name, dir_fd=fd)


def run(action: str, task: str, apply: bool, workspace: Path):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", task):
        raise Refusal("task must be one simple name, not a path")
    if not workspace.is_absolute() or workspace == Path(workspace.anchor) or ".." in workspace.parts:
        raise Refusal("workspace must be an absolute non-root directory without traversal")
    garage = workspace
    with open_absolute_directory(garage / "tmp") as scratch:
        names = set(os.listdir(scratch))
        if ".git" in names or {"HEAD", "objects", "refs"} <= names:
            raise Refusal("tmp itself is a repository, not a scratch root")
        if action == "create":
            os.mkdir(task, mode=0o700, dir_fd=scratch)
            with open_directory(task, scratch) as folder:
                write_state(folder, task, "active", create=True)
            print(garage / "tmp" / task)
            return
        with open_directory(task, scratch) as folder:
            identity = signature(os.fstat(folder))[:3]
            device = os.fstat(scratch).st_dev
            if identity[0] != device:
                raise Refusal("task crosses a filesystem boundary")
            state, marker_identity = read_state(folder, task)
            entries = inventory(folder, device)
            if entries.get(MARKER, (None,))[0] != marker_identity:
                raise Refusal("ownership marker changed during inspection")
            if action == "complete":
                write_state(folder, task, "complete")
                print(f"Marked complete: {task}")
                return
            if state["state"] != "complete":
                raise Refusal("task is active; finish its writers and mark it complete first")
            print(f"{'Remove' if apply else 'Preview'}: {garage / 'tmp' / task}")
            if not apply:
                print("No changes made. --apply permanently removes this completed scratch task.")
                return
            if inventory(folder, device) != entries:
                raise Refusal("scratch changed after inspection")
            if signature(os.stat(task, dir_fd=scratch, follow_symlinks=False))[:3] != identity:
                raise Refusal("task directory changed after inspection")
            remove_inventory(folder, entries)
        if signature(os.stat(task, dir_fd=scratch, follow_symlinks=False))[:3] != identity:
            raise Refusal("task directory replaced; refusing final removal")
        os.rmdir(task, dir_fd=scratch)
        print(f"Removed: {task}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True,
                        help="absolute workspace directory with an existing real tmp/ child")
    parser.add_argument("action", choices=("create", "complete", "clean"))
    parser.add_argument("task", help="unique task name, never a filesystem path")
    parser.add_argument("--apply", action="store_true", help="apply clean instead of previewing")
    args = parser.parse_args()
    if args.apply and args.action != "clean":
        parser.error("--apply is only used with clean")
    try:
        run(args.action, args.task, args.apply, args.workspace)
    except (OSError, ValueError, Refusal) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
