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
OID_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class GitFailure(RuntimeError):
    pass


class ApplyFailure(RuntimeError):
    def __init__(
        self,
        target: str,
        completed: list[dict[str, str]],
        cause: Exception,
    ) -> None:
        super().__init__(str(cause))
        self.target = target
        self.completed = completed


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
    components = [absolute]
    for parent in absolute.parents:
        components.append(parent)
        if parent.name == ".agents":
            break
    return any(component.is_symlink() for component in components)


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


def collect_remote_tracking_branches(
    repo: Path, integration_oid: str, protected_names: set[str]
) -> list[dict[str, Any]]:
    output = run_git(
        repo,
        "for-each-ref",
        "--format=%(refname)%09%(objectname)%09%(symref)",
        "refs/remotes",
    ).stdout
    branches: list[dict[str, Any]] = []
    for line in output.splitlines():
        if not line:
            continue
        ref, oid, symref = line.split("\t", 2)
        if symref or ref.endswith("/HEAD"):
            continue
        remote_and_branch = ref.removeprefix("refs/remotes/")
        remote, separator, branch = remote_and_branch.partition("/")
        if separator:
            ahead, behind = ahead_behind(repo, integration_oid, oid)
            merged = is_ancestor(repo, oid, integration_oid)
            branches.append(
                {
                    "remote": remote,
                    "branch": branch,
                    "ref": ref,
                    "oid": oid,
                    "ahead": ahead,
                    "behind": behind,
                    "merged": merged,
                    "follow_up_candidate": (
                        merged and branch not in protected_names
                    ),
                }
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
    merge_base = run_git(
        repo, "merge-base", integration_oid, branch_oid, check=False
    )
    if merge_base.returncode == 0:
        return run_git(
            repo, "diff", "--stat", f"{integration_oid}...{branch_oid}"
        ).stdout.strip()
    if merge_base.returncode == 1:
        stat = run_git(
            repo, "diff", "--stat", integration_oid, branch_oid
        ).stdout.strip()
        return f"no merge base; full tree diff:\n{stat}"
    raise GitFailure(
        merge_base.stderr.strip() or "could not determine a diff base"
    )


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
    scheduled_worktree_paths: set[str] = set()
    worktrees_by_branch: dict[str, list[dict[str, Any]]] = {}

    for worktree in worktrees:
        branch_ref = worktree["branch_ref"]
        if branch_ref:
            worktrees_by_branch.setdefault(branch_ref, []).append(worktree)
        if worktree["current"]:
            continue
        if worktree["prunable"] and not worktree["exists"]:
            prunable_paths.append(worktree["path"])
            scheduled_worktree_paths.add(worktree["path"])
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
        scheduled_worktree_paths.add(worktree["path"])

    retained: list[dict[str, str]] = []
    branch_actions: list[dict[str, str]] = []
    for branch in branches:
        branch_worktrees = worktrees_by_branch.get(branch["ref"], [])
        retained_worktrees = [
            worktree
            for worktree in branch_worktrees
            if worktree["path"] not in scheduled_worktree_paths
        ]
        retained_worktree = retained_worktrees[0] if retained_worktrees else None
        if branch["name"] in protected_names:
            retained.append(
                {"kind": "branch", "branch": branch["name"], "reason": "protected"}
            )
            continue
        merged = is_ancestor(repo, branch["oid"], integration_oid)
        if retained_worktree:
            decisions.append(
                decision_for_branch(
                    repo,
                    branch,
                    integration_oid,
                    "branch is checked out in a retained worktree",
                    retained_worktree["path"],
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
                branch_worktrees[0]["path"] if branch_worktrees else None,
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
        "remote_tracking_branches": collect_remote_tracking_branches(
            repo, integration_oid, protected_names
        ),
        "retained": retained,
        "actions": actions,
        "decisions": decisions,
    }


def render_summary(plan: dict[str, Any]) -> str:
    lines = ["# Repository cleanup plan", "", "## Safe local actions", ""]
    if plan["actions"]:
        for action in plan["actions"]:
            if action["kind"] == "remove_worktree":
                target = (
                    f"{action['path']} at `{action['expected_head'][:12]}`"
                )
            elif action["kind"] == "delete_branch":
                target = (
                    f"{action['branch']} at `{action['expected_oid'][:12]}`"
                )
            else:
                target = ", ".join(action["expected_paths"])
            lines.append(f"- `{action['kind']}`: {target}")
    else:
        lines.append("- None")

    lines.extend(["", "## Human decisions", ""])
    if plan["decisions"]:
        for decision in plan["decisions"]:
            target = decision.get("branch") or decision.get("path")
            if "ahead" in decision:
                upstream = decision["upstream"] or "none"
                if decision["upstream_state"] == "gone":
                    upstream += " (gone)"
                worktree = decision["worktree"] or "none"
                lines.append(
                    f"- `{target}` at `{decision['tip'][:12]}`; "
                    f"upstream: {upstream}; worktree: {worktree}; "
                    f"ahead {decision['ahead']}, behind {decision['behind']}; "
                    f"assessment: {decision['assessment']}"
                )
                last = decision["last_commit"]
                lines.append(
                    f"  Last: {last['subject']} — {last['author']}, "
                    f"{last['date']}"
                )
                lines.append(f"  Reason: {decision['reason']}")
                if decision["diff_stat"]:
                    lines.append("  Diff stat:")
                    for stat_line in decision["diff_stat"].splitlines():
                        lines.append(f"    {stat_line}")
            else:
                lines.append(f"- `{target}`: {decision['reason']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Retained", ""])
    if plan["retained"]:
        for item in plan["retained"]:
            lines.append(f"- `{item['branch']}`: {item['reason']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Remote follow-up candidates", ""])
    remote_candidates = [
        item
        for item in plan["remote_tracking_branches"]
        if item["follow_up_candidate"]
    ]
    if remote_candidates:
        for item in remote_candidates:
            lines.append(
                f"- `{item['remote']}/{item['branch']}` at "
                f"`{item['oid'][:12]}`; exact tip is merged; "
                f"ahead {item['ahead']}, behind {item['behind']}"
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


def validate_plan_shape(plan: dict[str, Any]) -> None:
    expected_top_level = {
        "schema_version",
        "repository",
        "protected_branches",
        "worktrees",
        "branches",
        "remote_tracking_branches",
        "retained",
        "actions",
        "decisions",
    }
    if set(plan) != expected_top_level or plan.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("malformed cleanup plan")

    repository = plan.get("repository")
    if not isinstance(repository, dict) or set(repository) != {
        "top_level",
        "common_dir",
        "integration_ref",
        "integration_oid",
    }:
        raise ValueError("malformed cleanup plan")
    for key in ("top_level", "common_dir"):
        value = repository.get(key)
        if (
            not isinstance(value, str)
            or not Path(value).is_absolute()
            or str(Path(value).resolve()) != value
        ):
            raise ValueError("malformed cleanup plan")
    integration_ref = repository.get("integration_ref")
    if not isinstance(integration_ref, str) or not integration_ref.startswith(
        "refs/heads/"
    ):
        raise ValueError("malformed cleanup plan")
    if not isinstance(repository.get("integration_oid"), str) or not OID_RE.fullmatch(
        repository["integration_oid"]
    ):
        raise ValueError("malformed cleanup plan")

    protected = plan.get("protected_branches")
    actions = plan.get("actions")
    if (
        not isinstance(protected, list)
        or not all(isinstance(item, str) for item in protected)
        or not isinstance(actions, list)
    ):
        raise ValueError("malformed cleanup plan")

    seen_targets: set[tuple[str, str]] = set()
    for action in actions:
        if not isinstance(action, dict) or not isinstance(action.get("kind"), str):
            raise ValueError("malformed cleanup plan")
        kind = action["kind"]
        if kind == "remove_worktree":
            if set(action) != {
                "kind",
                "path",
                "branch_ref",
                "expected_head",
            }:
                raise ValueError("malformed cleanup plan")
            path = action["path"]
            if (
                not isinstance(path, str)
                or not Path(path).is_absolute()
                or str(Path(path).resolve()) != path
                or not isinstance(action["branch_ref"], str)
                or not action["branch_ref"].startswith("refs/heads/")
                or not isinstance(action["expected_head"], str)
                or not OID_RE.fullmatch(action["expected_head"])
            ):
                raise ValueError("malformed cleanup plan")
            target = path
        elif kind == "prune_worktree_metadata":
            if set(action) != {"kind", "expected_paths"}:
                raise ValueError("malformed cleanup plan")
            paths = action["expected_paths"]
            if (
                not isinstance(paths, list)
                or not paths
                or not all(
                    isinstance(path, str)
                    and Path(path).is_absolute()
                    and str(Path(path).resolve()) == path
                    for path in paths
                )
                or len(paths) != len(set(paths))
            ):
                raise ValueError("malformed cleanup plan")
            target = "\0".join(sorted(paths))
        elif kind == "delete_branch":
            if set(action) != {
                "kind",
                "branch",
                "ref",
                "expected_oid",
            }:
                raise ValueError("malformed cleanup plan")
            branch = action["branch"]
            ref = action["ref"]
            if (
                not isinstance(branch, str)
                or not isinstance(ref, str)
                or ref != f"refs/heads/{branch}"
                or not isinstance(action["expected_oid"], str)
                or not OID_RE.fullmatch(action["expected_oid"])
            ):
                raise ValueError("malformed cleanup plan")
            target = ref
        else:
            raise ValueError(f"unknown cleanup action: {kind}")
        marker = (kind, target)
        if marker in seen_targets:
            raise ValueError("malformed cleanup plan")
        seen_targets.add(marker)


def canonical_actions(actions: list[dict[str, Any]]) -> list[str]:
    return [
        json.dumps(action, sort_keys=True, separators=(",", ":"))
        for action in actions
    ]


def revalidate_plan(
    plan: dict[str, Any],
    trusted_repo: Path,
    trusted_integration: str,
    trusted_protected: Iterable[str],
) -> dict[str, Any]:
    validate_plan_shape(plan)
    repository = plan["repository"]
    trusted_identity = repository_identity(trusted_repo)
    if trusted_identity != {
        "top_level": repository["top_level"],
        "common_dir": repository["common_dir"],
    }:
        raise ValueError(
            "cleanup plan does not match trusted cleanup inputs: repository"
        )
    repo = Path(trusted_identity["top_level"])
    integration_ref, integration_oid = validate_integration_ref(
        repo, trusted_integration
    )
    if integration_ref != repository["integration_ref"]:
        raise ValueError(
            "cleanup plan does not match trusted cleanup inputs: integration"
        )
    if integration_oid != repository["integration_oid"]:
        raise ValueError("stale cleanup plan: integration commit changed")
    rebuilt = build_plan(
        repo,
        trusted_integration,
        trusted_protected,
    )
    if rebuilt["protected_branches"] != plan["protected_branches"]:
        raise ValueError(
            "cleanup plan does not match trusted cleanup inputs: "
            "protected branches"
        )
    if canonical_actions(rebuilt["actions"]) != canonical_actions(
        plan["actions"]
    ):
        raise ValueError(
            "stale cleanup plan: plan does not match current safe action set"
        )
    return rebuilt


def run_mutation(
    repo: Path,
    target: str,
    completed: list[dict[str, str]],
    *args: str,
) -> None:
    try:
        run_git(repo, *args)
    except GitFailure as error:
        raise ApplyFailure(target, completed.copy(), error) from error


def apply_action(
    repo: Path,
    integration_oid: str,
    protected: set[str],
    action: dict[str, Any],
    events: list[dict[str, str]],
) -> None:
    kind = action["kind"]
    if kind == "remove_worktree":
        worktree = next(
            (
                item
                for item in collect_worktrees(repo)
                if item["path"] == action["path"]
            ),
            None,
        )
        if (
            worktree is None
            or worktree["head"] != action["expected_head"]
            or worktree["branch_ref"] != action["branch_ref"]
            or worktree["current"]
            or worktree["dirty"] is not False
            or worktree["locked"]
            or worktree["detached"]
        ):
            raise ValueError(
                f"stale cleanup plan: worktree changed: {action['path']}"
            )
        run_mutation(
            repo,
            action["path"],
            events,
            "worktree",
            "remove",
            "--",
            action["path"],
        )
        events.append(
            {
                "kind": kind,
                "target": action["path"],
                "expected_oid": action["expected_head"],
                "status": "removed",
            }
        )
        return

    if kind == "prune_worktree_metadata":
        current_prunable = sorted(
            item["path"]
            for item in collect_worktrees(repo)
            if item["prunable"] and not item["exists"]
        )
        if current_prunable != action["expected_paths"]:
            raise ValueError(
                "stale cleanup plan: prunable worktree metadata changed"
            )
        target = ", ".join(current_prunable)
        run_mutation(
            repo,
            target,
            events,
            "worktree",
            "prune",
            "--expire",
            "now",
        )
        events.append(
            {
                "kind": kind,
                "target": target,
                "expected_oid": "",
                "status": "pruned",
            }
        )
        return

    branch = next(
        (
            item
            for item in collect_local_branches(repo)
            if item["ref"] == action["ref"]
        ),
        None,
    )
    checked_out = {
        item["branch_ref"]
        for item in collect_worktrees(repo)
        if item["branch_ref"]
    }
    if (
        branch is None
        or branch["oid"] != action["expected_oid"]
        or branch["name"] in protected
        or branch["ref"] in checked_out
        or not is_ancestor(repo, branch["oid"], integration_oid)
    ):
        raise ValueError(
            f"stale cleanup plan: branch changed: {action['branch']}"
        )
    run_mutation(
        repo,
        action["branch"],
        events,
        "branch",
        "-d",
        "--",
        action["branch"],
    )
    events.append(
        {
            "kind": kind,
            "target": action["branch"],
            "expected_oid": action["expected_oid"],
            "status": "deleted",
        }
    )


def action_target(action: dict[str, Any]) -> str:
    if action["kind"] == "remove_worktree":
        return action["path"]
    if action["kind"] == "prune_worktree_metadata":
        return ", ".join(action["expected_paths"])
    return action["branch"]


def apply_plan(
    plan: dict[str, Any],
    trusted_repo: Path,
    trusted_integration: str,
    trusted_protected: Iterable[str],
) -> list[dict[str, str]]:
    rebuilt = revalidate_plan(
        plan, trusted_repo, trusted_integration, trusted_protected
    )
    repo = Path(rebuilt["repository"]["top_level"])
    integration_oid = rebuilt["repository"]["integration_oid"]
    protected = set(rebuilt["protected_branches"])
    events: list[dict[str, str]] = []

    for action in rebuilt["actions"]:
        target = action_target(action)
        try:
            apply_action(repo, integration_oid, protected, action, events)
        except ApplyFailure:
            raise
        except (GitFailure, ValueError, OSError) as error:
            raise ApplyFailure(target, events.copy(), error) from error
    return events


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
    apply_parser.add_argument("--repo", type=Path, required=True)
    apply_parser.add_argument("--integration", required=True)
    apply_parser.add_argument("--plan", type=Path, required=True)
    apply_parser.add_argument("--protect", action="append", default=[])
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
        events = apply_plan(
            load_plan(args.plan), args.repo, args.integration, args.protect
        )
        print(json.dumps(events, indent=2, sort_keys=True))
        return 0
    except ApplyFailure as error:
        print(f"error: {error}", file=sys.stderr)
        print(
            "completed-actions: "
            + json.dumps(error.completed, indent=2, sort_keys=True),
            file=sys.stderr,
        )
        print(f"failed-target: {error.target}", file=sys.stderr)
        return 3
    except (GitFailure, ValueError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
