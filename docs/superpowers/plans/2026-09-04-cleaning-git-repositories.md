# Cleaning Git Repositories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a durable skill that safely removes provably merged local branches and clean unused worktrees, while presenting concise evidence for every branch that needs a human decision.

**Architecture:** A concise `SKILL.md` drives a two-phase workflow through a standard-library-only Python helper. The helper first emits a repository-bound JSON plan and Markdown summary, then a guarded `apply-local` command revalidates the complete plan before making non-force local changes; remote deletion remains outside the helper and requires separate human approval.

**Tech Stack:** Markdown, YAML frontmatter, Python 3 standard library, Git CLI, `unittest`, bundled skill validator

**Spec:** `docs/superpowers/specs/2026-09-04-cleaning-git-repositories-design.md`

## Global Constraints

- Assume the helper can execute without an approval prompt; safety must not depend on a prompt appearing.
- Use only Python's standard library and Git CLI commands invoked as argument arrays with `shell=False`.
- The helper must not accept arbitrary commands, force deletion, delete remote refs, or use age, branch naming, missing upstreams, or hosting metadata as deletion proof.
- `apply-local` may run only from a real, non-symlinked `cleaning-git-repositories` installation beneath `.agents/skills` or `/etc/codex/skills`; source and symlinked development copies are planning-only.
- A local branch is automatically eligible only when its exact tip is an ancestor of the exact integration commit recorded in the plan.
- Never automatically delete the current branch, integration branch, a protected branch, a branch checked out in any remaining worktree, or a dirty, locked, detached, or ambiguous worktree.
- Revalidate repository identity, integration commit, branch tips, worktree state, and the full action set before the first mutation; recheck each target immediately before its mutation.
- Remove eligible worktrees before their branches. Use `git branch -d`, never `-D`.
- Treat plan files as untrusted input. Reject unknown schema versions, malformed refs or object IDs, path mismatches, extra actions, and stale state.
- Keep remote deletion as visible Git commands after a separately approved, enumerated proposal.
- Run all behavioral tests in disposable temporary repositories.

## File Map

- `cleaning-git-repositories/SKILL.md` — trigger boundary, authorization contract, helper invocation, decision presentation, remote follow-up, and reporting workflow.
- `cleaning-git-repositories/scripts/repository_cleanup.py` — self-contained CLI for repository inspection, deterministic classification, report generation, protected-install validation, plan revalidation, and safe local application.
- `cleaning-git-repositories/tests/test_repository_cleanup.py` — disposable-repository behavioral tests for classification, stale-plan rejection, protected-install enforcement, and safe application.

---

### Task 1: Establish the helper contract and repository fixtures

**Files:**
- Create: `cleaning-git-repositories/scripts/repository_cleanup.py`
- Create: `cleaning-git-repositories/tests/test_repository_cleanup.py`
- Read: `docs/superpowers/specs/2026-09-04-cleaning-git-repositories-design.md`

**Interfaces:**
- Consumes: `plan --repo PATH --integration REF --plan PATH [--protect BRANCH ...]`
- Produces: schema-versioned JSON at `--plan`, a Markdown summary on stdout, and a nonzero exit with one concise stderr message on invalid input
- Defines for later tasks: `GitFailure`, `run_git()`, `repository_identity()`, `validate_integration_ref()`, `assert_trusted_installation()`, `build_plan()`, `render_summary()`, `write_plan()`, `load_plan()`, `revalidate_plan()`, and `apply_plan()`

- [ ] **Step 1: Write the failing CLI and trust-boundary tests**

Create the initial test module with a disposable Git repository fixture and tests that define the public command shape:

```python
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = ROOT / "scripts" / "repository_cleanup.py"


def run(command: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(f"command failed: {command}\n{result.stdout}\n{result.stderr}")
    return result


class RepositoryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run(["git", "init", "-b", "main"], self.repo)
        run(["git", "config", "user.name", "Cleanup Test"], self.repo)
        run(["git", "config", "user.email", "cleanup@example.invalid"], self.repo)
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "base.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def install_script(self, *, symlink: bool = False) -> Path:
        target = self.root / "host" / ".agents" / "skills" / "cleaning-git-repositories"
        (target / "scripts").mkdir(parents=True)
        installed = target / "scripts" / "repository_cleanup.py"
        if symlink:
            installed.symlink_to(SOURCE_SCRIPT)
        else:
            shutil.copy2(SOURCE_SCRIPT, installed)
        return installed

    def test_plan_requires_a_local_integration_branch(self) -> None:
        plan = self.root / "plan.json"
        result = run(
            [sys.executable, str(SOURCE_SCRIPT), "plan", "--repo", str(self.repo),
             "--integration", "missing", "--plan", str(plan)],
            self.repo,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integration branch", result.stderr)
        self.assertFalse(plan.exists())

    def test_apply_local_rejects_source_and_symlinked_installations(self) -> None:
        plan = self.root / "plan.json"
        run(
            [sys.executable, str(SOURCE_SCRIPT), "plan", "--repo", str(self.repo),
             "--integration", "main", "--plan", str(plan)],
            self.repo,
        )
        source_result = run(
            [sys.executable, str(SOURCE_SCRIPT), "apply-local", "--plan", str(plan)],
            self.repo,
            check=False,
        )
        symlink_result = run(
            [sys.executable, str(self.install_script(symlink=True)),
             "apply-local", "--plan", str(plan)],
            self.repo,
            check=False,
        )
        self.assertIn("protected non-symlinked installation", source_result.stderr)
        self.assertIn("protected non-symlinked installation", symlink_result.stderr)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: FAIL because `repository_cleanup.py` does not exist.

- [ ] **Step 3: Implement the minimal CLI, Git runner, identity checks, and installation guard**

Create `repository_cleanup.py` with these public shapes and fail-closed defaults:

```python
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


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        shell=False,
    )
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise GitFailure(message)
    return result


def repository_identity(repo: Path) -> dict[str, str]:
    top = Path(run_git(repo, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    common_raw = run_git(repo, "rev-parse", "--git-common-dir").stdout.strip()
    common = Path(common_raw)
    if not common.is_absolute():
        common = (top / common).resolve()
    return {"top_level": str(top), "common_dir": str(common)}


def validate_integration_ref(repo: Path, name: str) -> tuple[str, str]:
    ref = f"refs/heads/{name}"
    checked = run_git(repo, "check-ref-format", "--branch", name, check=False)
    oid = run_git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
    if checked.returncode != 0 or oid.returncode != 0:
        raise ValueError(f"integration branch does not exist locally: {name}")
    return ref, oid.stdout.strip()


def has_symlink_component(path: Path) -> bool:
    absolute = path.absolute()
    return any(part.is_symlink() for part in [absolute, *absolute.parents])


def assert_trusted_installation(script: Path) -> None:
    absolute = script.absolute()
    if has_symlink_component(absolute):
        raise ValueError("apply-local requires a protected non-symlinked installation")
    normalized = absolute.as_posix()
    project_suffix = f"/.agents/skills/{SKILL_NAME}/scripts/repository_cleanup.py"
    admin_suffix = f"/etc/codex/skills/{SKILL_NAME}/scripts/repository_cleanup.py"
    if not normalized.endswith(project_suffix) and normalized != admin_suffix:
        raise ValueError("apply-local requires a protected non-symlinked installation")


def build_plan(repo: Path, integration: str, protected: Iterable[str]) -> dict[str, Any]:
    integration_ref, integration_oid = validate_integration_ref(repo, integration)
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
        "actions": [],
        "decisions": [],
    }


def render_summary(plan: dict[str, Any]) -> str:
    return "# Repository cleanup plan\n\nNo eligible cleanup actions.\n"


def write_plan(path: Path, plan: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
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
    raise ValueError("cleanup plan application is not implemented")


def apply_plan(plan: dict[str, Any]) -> list[dict[str, str]]:
    revalidate_plan(plan)
    return []
```

Add `argparse` subcommands `plan` and `apply-local`. `plan` calls `build_plan()`, writes JSON, and prints Markdown. `apply-local` must call `assert_trusted_installation(Path(__file__))` before loading or acting on a plan. Catch `GitFailure`, `ValueError`, `OSError`, and `json.JSONDecodeError` at the CLI boundary, print `error: <message>` to stderr, and return exit code 2 without a traceback.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: both tests pass.

- [ ] **Step 5: Commit the CLI contract**

Run:

```bash
git add cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py
```

Run:

```bash
git commit -m "feat: establish repository cleanup helper contract"
```

Expected: one commit containing the helper skeleton and its initial behavioral tests.

---

### Task 2: Build deterministic inventory, classification, and reports

**Files:**
- Modify: `cleaning-git-repositories/scripts/repository_cleanup.py`
- Modify: `cleaning-git-repositories/tests/test_repository_cleanup.py`

**Interfaces:**
- Consumes: the validated repository path, explicit local integration branch, and repeated protected branch names from Task 1
- Produces: a complete schema-version-1 plan with `repository`, `protected_branches`, `worktrees`, `branches`, `remote_tracking_branches`, `actions`, and `decisions`
- Preserves: `plan` command and trust guard defined in Task 1

- [ ] **Step 1: Add failing classification tests for the core branch and worktree cases**

Add fixture helpers `commit_file()`, `create_branch()`, `add_worktree()`, and `read_plan()`. Then add these tests:

```python
def plan_repository(self, *extra: str) -> dict[str, object]:
    path = self.root / "plan.json"
    result = run(
        [sys.executable, str(SOURCE_SCRIPT), "plan", "--repo", str(self.repo),
         "--integration", "main", "--plan", str(path), *extra],
        self.repo,
    )
    self.assertIn("Repository cleanup plan", result.stdout)
    return json.loads(path.read_text(encoding="utf-8"))

def test_merged_branch_and_clean_linked_worktree_are_safe_actions(self) -> None:
    run(["git", "switch", "-c", "merged"], self.repo)
    (self.repo / "merged.txt").write_text("merged\n", encoding="utf-8")
    run(["git", "add", "merged.txt"], self.repo)
    run(["git", "commit", "-m", "merged change"], self.repo)
    run(["git", "switch", "main"], self.repo)
    run(["git", "merge", "--ff-only", "merged"], self.repo)
    linked = self.root / "linked-merged"
    run(["git", "worktree", "add", str(linked), "merged"], self.repo)

    plan = self.plan_repository()

    self.assertEqual(
        [action["kind"] for action in plan["actions"]],
        ["remove_worktree", "delete_branch"],
    )

def test_squash_merged_branch_requires_a_human_decision(self) -> None:
    run(["git", "switch", "-c", "squashed"], self.repo)
    (self.repo / "squashed.txt").write_text("unique\n", encoding="utf-8")
    run(["git", "add", "squashed.txt"], self.repo)
    run(["git", "commit", "-m", "squashed work"], self.repo)
    run(["git", "switch", "main"], self.repo)
    run(["git", "merge", "--squash", "squashed"], self.repo)
    run(["git", "commit", "-m", "squash merge"], self.repo)

    plan = self.plan_repository()

    decision = next(item for item in plan["decisions"] if item["branch"] == "squashed")
    self.assertEqual(decision["reason"], "tip is not an ancestor of integration")
    self.assertIn("diff_stat", decision)

def test_dirty_locked_and_detached_worktrees_are_never_actions(self) -> None:
    run(["git", "branch", "work"], self.repo)
    dirty = self.root / "dirty"
    run(["git", "worktree", "add", str(dirty), "work"], self.repo)
    (dirty / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    run(["git", "worktree", "lock", str(dirty)], self.repo)
    detached = self.root / "detached"
    run(["git", "worktree", "add", "--detach", str(detached), "main"], self.repo)

    plan = self.plan_repository()

    action_paths = {item.get("path") for item in plan["actions"]}
    self.assertNotIn(str(dirty.resolve()), action_paths)
    self.assertNotIn(str(detached.resolve()), action_paths)

def test_protected_and_current_branches_are_retained(self) -> None:
    run(["git", "branch", "release/next"], self.repo)
    plan = self.plan_repository("--protect", "release/next")
    action_branches = {item.get("branch") for item in plan["actions"]}
    self.assertNotIn("main", action_branches)
    self.assertNotIn("release/next", action_branches)
```

Also add a gone-upstream test using a temporary bare remote: push a branch with `-u`, delete its remote ref, fetch with `--prune`, add a unique local commit, and assert it becomes a decision with `upstream_state == "gone"`, never an action.

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: the new tests fail because the plan has no inventory or classification.

- [ ] **Step 3: Implement porcelain parsing and evidence collection**

Add focused helpers with these signatures:

```python
def parse_worktree_porcelain(raw: str) -> list[dict[str, Any]]: ...
def collect_worktrees(repo: Path) -> list[dict[str, Any]]: ...
def collect_local_branches(repo: Path) -> list[dict[str, Any]]: ...
def collect_remote_tracking_branches(repo: Path) -> list[dict[str, str]]: ...
def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool: ...
def ahead_behind(repo: Path, integration_oid: str, branch_oid: str) -> tuple[int, int]: ...
def commit_summary(repo: Path, oid: str) -> dict[str, str]: ...
def branch_diff_stat(repo: Path, integration_oid: str, branch_oid: str) -> str: ...
```

Use `git worktree list --porcelain -z` and parse NUL-delimited fields rather than display-oriented output. For each existing worktree path, run `git status --porcelain=v1 -z --untracked-files=all`; a nonempty result is dirty. Record `locked`, `prunable`, `detached`, `bare`, exact `HEAD`, and full branch ref.

Use `git for-each-ref` over `refs/heads` with tab-separated fields for ref name, object ID, upstream ref, and upstream tracking status. Git ref names cannot contain ASCII control characters, so tabs are safe delimiters. Derive:

- `ahead` and `behind` from `git rev-list --left-right --count <integration>...<branch>`;
- ancestry from `git merge-base --is-ancestor <branch> <integration>`;
- last commit author/date/subject from `git show -s --format=%an%x00%aI%x00%s <oid>`; and
- the concise comparison from `git diff --stat <integration>...<branch>`.

Do not parse localized prose from `git branch`, `git status`, or `git worktree prune --verbose`.

- [ ] **Step 4: Implement deterministic classification and summary rendering**

Replace `build_plan()` so it:

1. Adds the current branch, integration branch, and each `--protect` value to `protected_branches`.
2. Maps every checked-out full branch ref to its worktree.
3. Classifies non-current worktrees as removable only when they are existing, clean, unlocked, attached, and attached to a branch whose exact tip is an ancestor of the integration commit.
4. Classifies a local branch as deletable only when it is merged, not protected/current, and either not checked out or attached only to a worktree already scheduled for removal.
5. Emits worktree-removal actions first, then one metadata-prune action only when all currently prunable entries are recorded, then branch-deletion actions.
6. Sends every non-eligible candidate to `decisions` or `retained` with one precise reason.

Each action must contain only the exact data needed for revalidation:

```json
{"kind":"remove_worktree","path":"/absolute/path","branch_ref":"refs/heads/merged","expected_head":"<oid>"}
{"kind":"prune_worktree_metadata","expected_paths":["/absolute/missing/path"]}
{"kind":"delete_branch","branch":"merged","ref":"refs/heads/merged","expected_oid":"<oid>"}
```

Render Markdown sections in this order: `Safe local actions`, `Human decisions`, `Retained`, and `Remote follow-up candidates`. For each decision show branch, abbreviated tip, upstream state, ahead/behind counts, last commit author/date/subject, and diff stat. Label possible squash merges as an inference when the tree diff is empty but ancestry proof fails; never convert that inference into an automatic action.

- [ ] **Step 5: Run the classification suite and verify GREEN**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: all Task 1 and Task 2 tests pass.

- [ ] **Step 6: Commit deterministic planning**

Run:

```bash
git add cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py
```

Run:

```bash
git commit -m "feat: plan safe repository cleanup"
```

Expected: one commit adding read-only inventory, classification, and reporting.

---

### Task 3: Implement guarded local application and stale-plan rejection

**Files:**
- Modify: `cleaning-git-repositories/scripts/repository_cleanup.py`
- Modify: `cleaning-git-repositories/tests/test_repository_cleanup.py`

**Interfaces:**
- Consumes: a schema-version-1 plan emitted by Task 2 and a trusted real installation path
- Produces: exit code 0 plus a JSON action log only when every planned precondition validates; exit code 2 with no new mutation when preflight validation fails
- Preserves: no force flags, arbitrary commands, remote deletion, or source/symlink application

- [ ] **Step 1: Add failing application and tamper-resistance tests**

Add these behavioral cases:

```python
def test_apply_local_removes_only_planned_merged_worktree_and_branch(self) -> None:
    run(["git", "branch", "merged"], self.repo)
    linked = self.root / "linked"
    run(["git", "worktree", "add", str(linked), "merged"], self.repo)
    installed = self.install_script()
    plan_path = self.root / "plan.json"
    run(
        [sys.executable, str(installed), "plan", "--repo", str(self.repo),
         "--integration", "main", "--plan", str(plan_path)],
        self.repo,
    )

    result = run(
        [sys.executable, str(installed), "apply-local", "--plan", str(plan_path)],
        self.repo,
    )

    events = json.loads(result.stdout)
    self.assertEqual([event["status"] for event in events], ["removed", "deleted"])
    self.assertFalse(linked.exists())
    self.assertNotEqual(run(["git", "show-ref", "--verify", "refs/heads/merged"], self.repo, False).returncode, 0)

def test_apply_local_rejects_a_stale_branch_tip_before_any_mutation(self) -> None:
    run(["git", "branch", "merged"], self.repo)
    linked = self.root / "linked"
    run(["git", "worktree", "add", str(linked), "merged"], self.repo)
    installed = self.install_script()
    plan_path = self.root / "plan.json"
    run([sys.executable, str(installed), "plan", "--repo", str(self.repo),
         "--integration", "main", "--plan", str(plan_path)], self.repo)
    run(["git", "-C", str(linked), "commit", "--allow-empty", "-m", "changed"], self.repo)

    result = run(
        [sys.executable, str(installed), "apply-local", "--plan", str(plan_path)],
        self.repo,
        check=False,
    )

    self.assertNotEqual(result.returncode, 0)
    self.assertIn("stale cleanup plan", result.stderr)
    self.assertTrue(linked.exists())
    self.assertEqual(run(["git", "show-ref", "--verify", "refs/heads/merged"], self.repo).returncode, 0)

def test_apply_local_rejects_tampered_paths_and_extra_actions(self) -> None:
    installed = self.install_script()
    plan_path = self.root / "plan.json"
    run([sys.executable, str(installed), "plan", "--repo", str(self.repo),
         "--integration", "main", "--plan", str(plan_path)], self.repo)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["actions"].append({"kind": "remove_worktree", "path": str(self.root),
                            "branch_ref": "refs/heads/main", "expected_head": "0" * 40})
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = run([sys.executable, str(installed), "apply-local", "--plan", str(plan_path)],
                 self.repo, check=False)
    self.assertIn("plan does not match current safe action set", result.stderr)
```

Add separate tests for a dirty worktree created after planning, a changed integration commit, a malformed object ID, unknown action kind, verified stale worktree metadata, and a partial command failure whose completed actions are accurately reported.

- [ ] **Step 2: Run the application tests and verify RED**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: application tests fail because `revalidate_plan()` still refuses every plan.

- [ ] **Step 3: Implement full-plan structural and state revalidation**

Implement `validate_plan_shape(plan)` before accessing any path or ref. Require exact top-level keys, `SCHEMA_VERSION`, absolute `top_level` and `common_dir`, a local `refs/heads/*` integration ref, valid hexadecimal object IDs, recognized action keys, and canonical absolute worktree paths. Reject duplicate targets and any branch name whose reconstructed full ref does not equal the recorded ref.

Implement `revalidate_plan(plan)` as follows:

```python
def revalidate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    validate_plan_shape(plan)
    repo = Path(plan["repository"]["top_level"])
    if repository_identity(repo) != {
        "top_level": plan["repository"]["top_level"],
        "common_dir": plan["repository"]["common_dir"],
    }:
        raise ValueError("stale cleanup plan: repository identity changed")
    integration_ref = plan["repository"]["integration_ref"]
    current_integration = run_git(repo, "rev-parse", "--verify", f"{integration_ref}^{{commit}}").stdout.strip()
    if current_integration != plan["repository"]["integration_oid"]:
        raise ValueError("stale cleanup plan: integration commit changed")
    rebuilt = build_plan(
        repo,
        integration_ref.removeprefix("refs/heads/"),
        plan["protected_branches"],
    )
    if canonical_actions(rebuilt["actions"]) != canonical_actions(plan["actions"]):
        raise ValueError("plan does not match current safe action set")
    return rebuilt
```

Compare the complete canonical action set, not merely each user-supplied action. This prevents a tampered plan from omitting a worktree removal while retaining its branch deletion or adding a target that was never classified as safe.

- [ ] **Step 4: Implement ordered mutation with immediate rechecks and an action log**

Implement `apply_plan()` to:

1. finish full-plan revalidation before the first mutation;
2. before each worktree removal, re-read the worktree record, verify the expected head/ref and clean status, then run `git worktree remove -- <path>` without `--force`;
3. before metadata pruning, confirm the complete current prunable path set equals `expected_paths`, then run `git worktree prune --expire now`;
4. before each branch deletion, verify its exact object ID, ancestry, protection status, and absence from all remaining worktrees, then run `git branch -d -- <branch>`; and
5. append `{kind, target, expected_oid, status}` to the emitted JSON log after each successful action.

If a Git command fails after earlier actions succeeded, return a nonzero status and emit both the completed action log and the failing target to stderr. Never retry with force. The final skill report will use this evidence rather than claiming an all-or-nothing result.

- [ ] **Step 5: Run all helper tests and verify GREEN**

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: all tests pass, including stale-plan, tampered-plan, protected-install, and safe-application cases.

- [ ] **Step 6: Prove the helper has no force or remote-deletion surface**

Run:

```bash
python3 cleaning-git-repositories/scripts/repository_cleanup.py --help
```

Expected: only `plan` and `apply-local` subcommands are shown; no `force`, `push`, `remote-delete`, or arbitrary-command option exists.

Run:

```bash
rg -n "branch -D|push|remote-delete|shell=True|os\.system|subprocess\.Popen" cleaning-git-repositories/scripts cleaning-git-repositories/tests
```

Expected: no production-code match. Test descriptions or assertions may mention forbidden terms only to verify their absence.

- [ ] **Step 7: Commit guarded local cleanup**

Run:

```bash
git add cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py
```

Run:

```bash
git commit -m "feat: apply verified local repository cleanup"
```

Expected: one commit implementing revalidation and non-force local actions.

---

### Task 4: Author the skill workflow and verify the complete artifact

**Files:**
- Create: `cleaning-git-repositories/SKILL.md`
- Modify: `cleaning-git-repositories/tests/test_repository_cleanup.py`
- Verify: `cleaning-git-repositories/scripts/repository_cleanup.py`

**Interfaces:**
- Consumes: a user request to clean stale Git branches or worktrees, current repository instructions, an explicit integration branch, protected branch names, and the helper from Tasks 1-3
- Produces: automatic cleanup of only revalidated safe local candidates; concise human choices for ambiguous branches; separately approved visible remote deletions; and a final recovery-aware report

- [ ] **Step 1: Add final end-to-end tests for stale metadata and remote boundaries**

Add a test that creates a linked worktree, removes only its disposable directory with `shutil.rmtree`, verifies Git reports it as prunable, plans from a protected copied helper, applies the plan, and confirms the stale administrative record disappears.

Add a test with two remotes and remote-tracking branches. Assert `plan` inventories them as follow-up candidates but `actions` contains no remote mutation. Also assert the CLI rejects `remote-delete` as an unknown subcommand.

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: the stale-metadata or remote-inventory assertion fails until any remaining planner coverage is implemented.

- [ ] **Step 2: Complete the smallest helper changes needed for the final tests**

Add only the missing read-only remote inventory or verified prunable-record handling. Do not add hosting-provider APIs, pull-request lookups, network operations, remote deletion, age thresholds, or configurable policy frameworks.

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: the complete behavioral suite passes.

- [ ] **Step 3: Write the concise skill entrypoint**

Create `cleaning-git-repositories/SKILL.md` with this structure and contract:

```markdown
---
name: cleaning-git-repositories
description: Use when cleaning a Git repository by removing merged local branches, unused worktrees, or stale worktree metadata, and when unmerged branches need concise human decisions. Exclude ordinary branch creation and active feature development.
---

# Cleaning Git Repositories

Read the repository's controlling instructions before classifying protected branches or choosing an integration branch. Treat the user's cleanup request as authorization only for the provably safe local actions defined below.

## Establish current evidence

Identify the integration branch and protected branches from repository and remote metadata. Ask when multiple plausible integration branches or authoritative remotes remain. Fetch and prune remote-tracking refs only when permitted; if freshness cannot be established, disclose that limitation.

Run `scripts/repository_cleanup.py plan` with the repository, explicit integration branch, output plan path, and every protected branch. Review its complete summary before applying anything.

## Apply safe local cleanup

Use `apply-local` only from a reviewed, real, non-symlinked installation in a recursively read-only skill location and only under a permission profile that preserves that protection. Assume invocation itself may not prompt.

The helper may remove only clean non-current worktrees attached to provably merged branches, verified stale worktree metadata, and local branches whose exact tips are ancestors of the recorded integration commit. A cleanup failure never authorizes force.

If the installation is writable, symlinked, or uncertain, use the helper only for planning and perform the same authorized actions as visible, individually scoped Git commands after rechecking their evidence.

## Route human decisions

For every decision candidate, present branch and tip, upstream/worktree state, ahead/behind counts, last commit author/date/subject, diff stat, and the helper's evidence-labeled assessment. Offer keep, inspect, archive with a tag, or delete. Identify any choice that would require force and wait for explicit direction.

## Offer remote cleanup separately

After local cleanup and decisions, enumerate remote candidates and their evidence. Require separate approval for the exact remote targets, revalidate them, and execute remote deletion visibly outside the helper.

## Report

List removed, retained, skipped, failed, and unresolved items. Include recorded tip commits and practical reflog or tag recovery guidance. Do not call the repository clean when evidence is stale or decisions remain.
```

Adjust wording only to match the helper's exact final option names and output fields. Keep non-obvious safety invariants; remove duplicated implementation detail that the helper enforces mechanically.

- [ ] **Step 4: Validate the skill and run the behavioral suite**

Run:

```bash
python3 /Users/phil-mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py cleaning-git-repositories
```

Expected: validation succeeds with no frontmatter, naming, or placeholder errors.

Run:

```bash
python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v
```

Expected: all behavioral tests pass in disposable repositories.

- [ ] **Step 5: Run final static and repository checks**

Run:

```bash
python3 -m py_compile cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py
```

Expected: no output and exit code 0.

Run:

```bash
git diff --check
```

Expected: no output.

Run:

```bash
git status --short
```

Expected: only the intended `cleaning-git-repositories` files are uncommitted.

- [ ] **Step 6: Commit the completed skill**

Run:

```bash
git add cleaning-git-repositories/SKILL.md cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py
```

Run:

```bash
git commit -m "feat: add repository cleanup skill"
```

Expected: the final implementation commit contains the skill entrypoint plus any focused test/helper adjustments from this task.

- [ ] **Step 7: Verify committed state**

Run:

```bash
git status --short --branch
```

Expected: a clean worktree with the branch ahead only by the intended design, plan, and implementation commits.

Run:

```bash
git log -5 --oneline --decorate
```

Expected: the repository-cleanup implementation commits appear in order, ending with `feat: add repository cleanup skill`.
