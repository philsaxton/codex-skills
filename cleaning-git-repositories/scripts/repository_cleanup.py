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


def parse_worktree_porcelain(raw: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] = {}
    for field in raw.split("\0"):
        if not field:
            if current:
                records.append(current)
                current = {}
            continue
        key, separator, value = field.partition(" ")
        if separator:
            current[key] = value
        else:
            current[key] = True
    if current:
        records.append(current)
    return records


def collect_worktrees(repo: Path) -> list[dict[str, Any]]:
    identity = repository_identity(repo)
    current_root = Path(identity["top_level"])
    raw = run_git(repo, "worktree", "list", "--porcelain", "-z").stdout
    worktrees: list[dict[str, Any]] = []
    for parsed in parse_worktree_porcelain(raw):
        path = Path(parsed["worktree"]).resolve()
        exists = path.exists()
        dirty: bool | None = None
        status_error = ""
        if exists and not parsed.get("bare"):
            status = run_git(
                path,
                "status",
                "--porcelain=v1",
                "-z",
                "--untracked-files=all",
                check=False,
            )
            if status.returncode == 0:
                dirty = bool(status.stdout)
            else:
                status_error = status.stderr.strip() or status.stdout.strip()
        worktrees.append(
            {
                "path": str(path),
                "head": parsed.get("HEAD", ""),
                "branch_ref": parsed.get("branch"),
                "current": path == current_root,
                "exists": exists,
                "dirty": dirty,
                "locked": bool(parsed.get("locked")),
                "lock_reason": (
                    parsed.get("locked")
                    if isinstance(parsed.get("locked"), str)
                    else ""
                ),
                "detached": bool(parsed.get("detached")),
                "bare": bool(parsed.get("bare")),
                "prunable": bool(parsed.get("prunable")),
                "prune_reason": (
                    parsed.get("prunable")
                    if isinstance(parsed.get("prunable"), str)
                    else ""
                ),
                "status_error": status_error,
            }
        )
    return worktrees


def collect_local_branches(repo: Path) -> list[dict[str, Any]]:
    output = run_git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(upstream)%09%(upstream:track)",
        "refs/heads",
    ).stdout
    branches: list[dict[str, Any]] = []
    for line in output.splitlines():
        if not line:
            continue
        ref, oid, upstream, tracking = line.split("\t", 3)
        upstream_state = "none"
        if upstream:
            present = run_git(
                repo, "rev-parse", "--verify", upstream, check=False
            )
            upstream_state = "present" if present.returncode == 0 else "gone"
        branches.append(
            {
                "name": ref.removeprefix("refs/heads/"),
                "ref": ref,
                "oid": oid,
                "upstream": upstream or None,
                "upstream_state": upstream_state,
                "tracking": tracking,
            }
        )
    return branches


def collect_remote_tracking_branches(repo: Path) -> list[dict[str, str]]:
    output = run_git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(symref)",
        "refs/remotes",
    ).stdout
    branches: list[dict[str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        ref, oid, symref = line.split("\t", 2)
        if symref or ref.endswith("/HEAD"):
            continue
        remote_and_branch = ref.removeprefix("refs/remotes/")
        remote, separator, branch = remote_and_branch.partition("/")
        if separator:
            branches.append(
                {"remote": remote, "branch": branch, "ref": ref, "oid": oid}
            )
    return branches


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    result = run_git(
        repo,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise GitFailure(result.stderr.strip() or "could not determine ancestry")
    return result.returncode == 0


def ahead_behind(
    repo: Path, integration_oid: str, branch_oid: str
) -> tuple[int, int]:
    output = run_git(
        repo,
        "rev-list",
        "--left-right",
        "--count",
        f"{integration_oid}...{branch_oid}",
    ).stdout
    behind_text, ahead_text = output.split()
    return int(ahead_text), int(behind_text)


def commit_summary(repo: Path, oid: str) -> dict[str, str]:
    output = run_git(
        repo, "show", "-s", "--format=%an%x00%aI%x00%s", oid
    ).stdout.rstrip("\n")
    author, date, subject = output.split("\0", 2)
    return {"author": author, "date": date, "subject": subject}


def branch_diff_stat(repo: Path, integration_oid: str, branch_oid: str) -> str:
    return run_git(
        repo, "diff", "--stat", f"{integration_oid}...{branch_oid}"
    ).stdout.strip()


def trees_equal(repo: Path, left_oid: str, right_oid: str) -> bool:
    result = run_git(repo, "diff", "--quiet", left_oid, right_oid, check=False)
    if result.returncode not in (0, 1):
        raise GitFailure(result.stderr.strip() or "could not compare trees")
    return result.returncode == 0


def current_branch(repo: Path) -> str | None:
    result = run_git(
        repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def decision_for_branch(
    repo: Path,
    branch: dict[str, Any],
    integration_oid: str,
    reason: str,
    worktree: str | None = None,
) -> dict[str, Any]:
    ahead, behind = ahead_behind(repo, integration_oid, branch["oid"])
    assessment = "uncertain"
    if trees_equal(repo, integration_oid, branch["oid"]):
        assessment = "possible squash merge"
    elif ahead > 0:
        assessment = "active or abandoned work"
    return {
        "branch": branch["name"],
        "ref": branch["ref"],
        "tip": branch["oid"],
        "upstream": branch["upstream"],
        "upstream_state": branch["upstream_state"],
        "worktree": worktree,
        "ahead": ahead,
        "behind": behind,
        "last_commit": commit_summary(repo, branch["oid"]),
        "diff_stat": branch_diff_stat(repo, integration_oid, branch["oid"]),
        "assessment": assessment,
        "reason": reason,
    }


def build_plan(
    repo: Path, integration: str, protected: Iterable[str]
) -> dict[str, Any]:
    integration_ref, integration_oid = validate_integration_ref(
        repo, integration
    )
    identity = repository_identity(repo)
    worktrees = collect_worktrees(repo)
    branches = collect_local_branches(repo)
    branch_by_ref = {branch["ref"]: branch for branch in branches}
    active_branch = current_branch(repo)
    protected_names = set(protected) | {integration}
    if active_branch:
        protected_names.add(active_branch)
    for name in protected_names:
        checked = run_git(
            repo, "check-ref-format", "--branch", name, check=False
        )
        if checked.returncode != 0:
            raise ValueError(f"invalid protected branch name: {name}")

    worktree_actions: list[dict[str, Any]] = []
    prunable_paths: list[str] = []
    decisions: list[dict[str, Any]] = []
    removable_branch_refs: set[str] = set()
    worktree_by_branch: dict[str, dict[str, Any]] = {}

    for worktree in worktrees:
        branch_ref = worktree["branch_ref"]
        if branch_ref:
            worktree_by_branch[branch_ref] = worktree
        if worktree["current"]:
            continue
        if worktree["prunable"] and not worktree["exists"]:
            prunable_paths.append(worktree["path"])
            if branch_ref:
                removable_branch_refs.add(branch_ref)
            continue
        if worktree["locked"]:
            decisions.append(
                {
                    "kind": "worktree",
                    "path": worktree["path"],
                    "branch": (
                        branch_ref.removeprefix("refs/heads/")
                        if branch_ref
                        else None
                    ),
                    "reason": "worktree is locked",
                }
            )
            continue
        if worktree["detached"]:
            decisions.append(
                {
                    "kind": "worktree",
                    "path": worktree["path"],
                    "branch": None,
                    "reason": "worktree is detached",
                }
            )
            continue
        if not worktree["exists"] or worktree["dirty"] is not False:
            reason = (
                "worktree is dirty"
                if worktree["dirty"]
                else "worktree state could not be verified"
            )
            decisions.append(
                {
                    "kind": "worktree",
                    "path": worktree["path"],
                    "branch": (
                        branch_ref.removeprefix("refs/heads/")
                        if branch_ref
                        else None
                    ),
                    "reason": reason,
                }
            )
            continue
        branch = branch_by_ref.get(branch_ref)
        if not branch or not is_ancestor(
            repo, branch["oid"], integration_oid
        ):
            decisions.append(
                {
                    "kind": "worktree",
                    "path": worktree["path"],
                    "branch": branch["name"] if branch else None,
                    "reason": "worktree branch is not merged",
                }
            )
            continue
        worktree_actions.append(
            {
                "kind": "remove_worktree",
                "path": worktree["path"],
                "branch_ref": branch["ref"],
                "expected_head": worktree["head"],
            }
        )
        removable_branch_refs.add(branch["ref"])

    retained: list[dict[str, str]] = []
    branch_actions: list[dict[str, str]] = []
    for branch in branches:
        worktree = worktree_by_branch.get(branch["ref"])
        if branch["name"] in protected_names:
            retained.append(
                {"kind": "branch", "branch": branch["name"], "reason": "protected"}
            )
            continue
        merged = is_ancestor(repo, branch["oid"], integration_oid)
        if worktree and branch["ref"] not in removable_branch_refs:
            decisions.append(
                decision_for_branch(
                    repo,
                    branch,
                    integration_oid,
                    "branch is checked out in a retained worktree",
                    worktree["path"],
                )
            )
            continue
        if merged:
            branch_actions.append(
                {
                    "kind": "delete_branch",
                    "branch": branch["name"],
                    "ref": branch["ref"],
                    "expected_oid": branch["oid"],
                }
            )
            continue
        decisions.append(
            decision_for_branch(
                repo,
                branch,
                integration_oid,
                "tip is not an ancestor of integration",
                worktree["path"] if worktree else None,
            )
        )

    actions: list[dict[str, Any]] = list(worktree_actions)
    if prunable_paths:
        actions.append(
            {
                "kind": "prune_worktree_metadata",
                "expected_paths": sorted(prunable_paths),
            }
        )
    actions.extend(branch_actions)

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": {
            **identity,
            "integration_ref": integration_ref,
            "integration_oid": integration_oid,
        },
        "protected_branches": sorted(protected_names),
        "worktrees": worktrees,
        "branches": branches,
        "remote_tracking_branches": collect_remote_tracking_branches(repo),
        "retained": retained,
        "actions": actions,
        "decisions": decisions,
    }


def render_summary(plan: dict[str, Any]) -> str:
    lines = ["# Repository cleanup plan", "", "## Safe local actions", ""]
    if plan["actions"]:
        for action in plan["actions"]:
            target = action.get("path") or action.get("branch") or ", ".join(
                action.get("expected_paths", [])
            )
            lines.append(f"- `{action['kind']}`: {target}")
    else:
        lines.append("- None")

    lines.extend(["", "## Human decisions", ""])
    if plan["decisions"]:
        for decision in plan["decisions"]:
            target = decision.get("branch") or decision.get("path")
            details = decision["reason"]
            if "ahead" in decision:
                details += (
                    f"; ahead {decision['ahead']}, behind {decision['behind']}; "
                    f"assessment: {decision['assessment']}"
                )
            lines.append(f"- `{target}`: {details}")
            if decision.get("diff_stat"):
                for stat_line in decision["diff_stat"].splitlines():
                    lines.append(f"  {stat_line}")
    else:
        lines.append("- None")

    lines.extend(["", "## Retained", ""])
    if plan["retained"]:
        for item in plan["retained"]:
            lines.append(f"- `{item['branch']}`: {item['reason']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Remote follow-up candidates", ""])
    if plan["remote_tracking_branches"]:
        for item in plan["remote_tracking_branches"]:
            lines.append(
                f"- `{item['remote']}/{item['branch']}` at `{item['oid'][:12]}`"
            )
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


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
