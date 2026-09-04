from __future__ import annotations

from contextlib import redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = ROOT / "scripts" / "repository_cleanup.py"


def run(
    command: list[str], cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {command}\n{result.stdout}\n{result.stderr}"
        )
    return result


class RepositoryCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run(["git", "init", "-b", "main"], self.repo)
        run(["git", "config", "user.name", "Cleanup Test"], self.repo)
        run(
            ["git", "config", "user.email", "cleanup@example.invalid"],
            self.repo,
        )
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        run(["git", "add", "base.txt"], self.repo)
        run(["git", "commit", "-m", "base"], self.repo)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def install_script(self, *, symlink: bool = False) -> Path:
        target = (
            self.root
            / "host"
            / ".agents"
            / "skills"
            / "cleaning-git-repositories"
        )
        (target / "scripts").mkdir(parents=True)
        installed = target / "scripts" / "repository_cleanup.py"
        if symlink:
            installed.symlink_to(SOURCE_SCRIPT)
        else:
            shutil.copy2(SOURCE_SCRIPT, installed)
        return installed

    def install_script_with_symlinked_ancestor(self, ancestor: str) -> Path:
        host = self.root / f"host-{ancestor}"
        if ancestor == ".agents":
            real_agents = host / "real-agents"
            real_agents.mkdir(parents=True)
            (host / ".agents").symlink_to(
                real_agents, target_is_directory=True
            )
        elif ancestor == "skills":
            agents = host / ".agents"
            agents.mkdir(parents=True)
            real_skills = host / "real-skills"
            real_skills.mkdir()
            (agents / "skills").symlink_to(
                real_skills, target_is_directory=True
            )
        else:
            raise AssertionError(f"unsupported ancestor: {ancestor}")
        target = (
            host
            / ".agents"
            / "skills"
            / "cleaning-git-repositories"
            / "scripts"
        )
        target.mkdir(parents=True)
        installed = target / "repository_cleanup.py"
        shutil.copy2(SOURCE_SCRIPT, installed)
        return installed

    def load_installed_module(self, script: Path):
        spec = importlib.util.spec_from_file_location(
            "installed_repository_cleanup", script
        )
        if spec is None or spec.loader is None:
            raise AssertionError("could not load installed helper")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def apply_local(
        self,
        script: Path,
        plan: Path,
        *,
        protect: tuple[str, ...] = (),
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(script),
            "apply-local",
            "--repo",
            str(self.repo),
            "--integration",
            "main",
            "--plan",
            str(plan),
        ]
        for branch in protect:
            command.extend(["--protect", branch])
        return run(command, self.repo, check=check)

    def plan_repository(self, *extra: str, script: Path | None = None) -> dict:
        path = self.root / "plan.json"
        result = run(
            [
                sys.executable,
                str(script or SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--plan",
                str(path),
                *extra,
            ],
            self.repo,
        )
        self.assertIn("Repository cleanup plan", result.stdout)
        return json.loads(path.read_text(encoding="utf-8"))

    def commit_file(
        self, path: Path, content: str, message: str
    ) -> None:
        relative = path.relative_to(self.repo)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        run(["git", "add", str(relative)], self.repo)
        run(["git", "commit", "-m", message], self.repo)

    def test_plan_requires_a_local_integration_branch(self) -> None:
        plan = self.root / "plan.json"
        result = run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "missing",
                "--plan",
                str(plan),
            ],
            self.repo,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integration branch", result.stderr)
        self.assertFalse(plan.exists())

    def test_apply_local_rejects_source_and_symlinked_installations(self) -> None:
        plan = self.root / "plan.json"
        run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--plan",
                str(plan),
            ],
            self.repo,
        )
        source_result = self.apply_local(
            SOURCE_SCRIPT, plan, check=False
        )
        symlink_result = self.apply_local(
            self.install_script(symlink=True), plan, check=False
        )
        self.assertIn(
            "protected non-symlinked installation", source_result.stderr
        )
        self.assertIn(
            "protected non-symlinked installation", symlink_result.stderr
        )

    def assert_symlinked_ancestor_is_rejected(self, ancestor: str) -> None:
        linked = self.create_merged_linked_worktree()
        installed = self.install_script_with_symlinked_ancestor(ancestor)
        plan_path = self.write_plan_with(installed)

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("protected non-symlinked installation", result.stderr)
        self.assertTrue(linked.exists())

    def test_apply_local_rejects_a_symlinked_agents_ancestor(self) -> None:
        self.assert_symlinked_ancestor_is_rejected(".agents")

    def test_apply_local_rejects_a_symlinked_skills_ancestor(self) -> None:
        self.assert_symlinked_ancestor_is_rejected("skills")

    def test_merged_branch_and_clean_linked_worktree_are_safe_actions(
        self,
    ) -> None:
        run(["git", "switch", "-c", "merged"], self.repo)
        self.commit_file(
            self.repo / "merged.txt", "merged\n", "merged change"
        )
        run(["git", "switch", "main"], self.repo)
        run(["git", "merge", "--ff-only", "merged"], self.repo)
        linked = self.root / "linked-merged"
        run(["git", "worktree", "add", str(linked), "merged"], self.repo)

        plan = self.plan_repository()

        self.assertEqual(
            [action["kind"] for action in plan["actions"]],
            ["remove_worktree", "delete_branch"],
        )
        self.assertEqual(plan["actions"][0]["path"], str(linked.resolve()))
        self.assertEqual(plan["actions"][1]["branch"], "merged")

    def test_squash_merged_branch_requires_a_human_decision(self) -> None:
        run(["git", "switch", "-c", "squashed"], self.repo)
        self.commit_file(
            self.repo / "squashed.txt", "unique\n", "squashed work"
        )
        run(["git", "switch", "main"], self.repo)
        run(["git", "merge", "--squash", "squashed"], self.repo)
        run(["git", "commit", "-m", "squash merge"], self.repo)

        plan = self.plan_repository()

        decision = next(
            item for item in plan["decisions"] if item["branch"] == "squashed"
        )
        self.assertEqual(
            decision["reason"], "tip is not an ancestor of integration"
        )
        self.assertEqual(decision["assessment"], "possible squash merge")
        self.assertIn("diff_stat", decision)

    def test_human_decision_summary_contains_comparable_evidence(self) -> None:
        run(["git", "switch", "-c", "unmerged"], self.repo)
        self.commit_file(
            self.repo / "unmerged.txt", "unique\n", "unique work"
        )
        tip = run(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        run(["git", "switch", "main"], self.repo)
        plan_path = self.root / "plan.json"

        result = run(
            [
                sys.executable,
                str(SOURCE_SCRIPT),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--plan",
                str(plan_path),
            ],
            self.repo,
        )

        self.assertIn(f"`unmerged` at `{tip[:12]}`", result.stdout)
        self.assertIn("upstream: none", result.stdout)
        self.assertIn("worktree: none", result.stdout)
        self.assertIn("ahead 1, behind 0", result.stdout)
        self.assertIn("unique work", result.stdout)
        self.assertIn("Cleanup Test", result.stdout)
        self.assertIn("unmerged.txt", result.stdout)

    def test_unrelated_history_is_reported_without_blocking_the_plan(self) -> None:
        run(["git", "switch", "--orphan", "unrelated"], self.repo)
        self.commit_file(
            self.repo / "unrelated.txt", "separate\n", "unrelated root"
        )
        run(["git", "switch", "main"], self.repo)

        plan = self.plan_repository()

        decision = next(
            item for item in plan["decisions"] if item["branch"] == "unrelated"
        )
        self.assertIn("unrelated.txt", decision["diff_stat"])
        self.assertIn("no merge base", decision["diff_stat"])

    def test_dirty_locked_and_detached_worktrees_are_never_actions(
        self,
    ) -> None:
        run(["git", "branch", "work"], self.repo)
        dirty = self.root / "dirty"
        run(["git", "worktree", "add", str(dirty), "work"], self.repo)
        (dirty / "dirty.txt").write_text("dirty\n", encoding="utf-8")
        run(["git", "worktree", "lock", str(dirty)], self.repo)
        detached = self.root / "detached"
        run(
            ["git", "worktree", "add", "--detach", str(detached), "main"],
            self.repo,
        )

        plan = self.plan_repository()

        action_paths = {item.get("path") for item in plan["actions"]}
        self.assertNotIn(str(dirty.resolve()), action_paths)
        self.assertNotIn(str(detached.resolve()), action_paths)
        reasons = {item["reason"] for item in plan["decisions"]}
        self.assertIn("worktree is locked", reasons)
        self.assertIn("worktree is detached", reasons)

    def test_protected_and_current_branches_are_retained(self) -> None:
        run(["git", "branch", "release/next"], self.repo)

        plan = self.plan_repository("--protect", "release/next")

        action_branches = {item.get("branch") for item in plan["actions"]}
        self.assertNotIn("main", action_branches)
        self.assertNotIn("release/next", action_branches)
        retained = {item["branch"] for item in plan["retained"]}
        self.assertIn("main", retained)
        self.assertIn("release/next", retained)

    def test_branch_deletion_requires_every_checkout_to_be_removable(self) -> None:
        run(["git", "branch", "merged"], self.repo)
        removable = self.root / "removable"
        retained = self.root / "retained"
        run(["git", "worktree", "add", str(removable), "merged"], self.repo)
        run(
            ["git", "worktree", "add", "--force", str(retained), "merged"],
            self.repo,
        )
        (retained / "dirty.txt").write_text("dirty\n", encoding="utf-8")

        plan = self.plan_repository()

        removed_paths = {
            action["path"]
            for action in plan["actions"]
            if action["kind"] == "remove_worktree"
        }
        deleted_branches = {
            action["branch"]
            for action in plan["actions"]
            if action["kind"] == "delete_branch"
        }
        self.assertEqual(removed_paths, {str(removable.resolve())})
        self.assertNotIn("merged", deleted_branches)

    def test_gone_upstream_with_unique_commits_requires_a_decision(
        self,
    ) -> None:
        remote = self.root / "remote.git"
        run(["git", "init", "--bare", str(remote)], self.root)
        run(["git", "remote", "add", "origin", str(remote)], self.repo)
        run(["git", "switch", "-c", "gone"], self.repo)
        self.commit_file(self.repo / "gone.txt", "pushed\n", "pushed work")
        run(["git", "push", "-u", "origin", "gone"], self.repo)
        run(["git", "push", "origin", "--delete", "gone"], self.repo)
        self.commit_file(
            self.repo / "gone.txt", "pushed\nlocal\n", "local unique work"
        )
        run(["git", "switch", "main"], self.repo)
        run(["git", "fetch", "--prune", "origin"], self.repo)

        plan = self.plan_repository()

        decision = next(
            item for item in plan["decisions"] if item["branch"] == "gone"
        )
        self.assertEqual(decision["upstream_state"], "gone")
        self.assertGreater(decision["ahead"], 0)
        self.assertFalse(
            any(
                item.get("branch") == "gone" for item in plan["actions"]
            )
        )

    def create_merged_linked_worktree(self) -> Path:
        run(["git", "branch", "merged"], self.repo)
        linked = self.root / "linked"
        run(["git", "worktree", "add", str(linked), "merged"], self.repo)
        return linked

    def write_plan_with(self, script: Path) -> Path:
        plan_path = self.root / "plan.json"
        run(
            [
                sys.executable,
                str(script),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--plan",
                str(plan_path),
            ],
            self.repo,
        )
        return plan_path

    def test_apply_local_removes_only_planned_merged_worktree_and_branch(
        self,
    ) -> None:
        linked = self.create_merged_linked_worktree()
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)

        result = self.apply_local(installed, plan_path)

        events = json.loads(result.stdout)
        self.assertEqual(
            [event["status"] for event in events], ["removed", "deleted"]
        )
        self.assertFalse(linked.exists())
        self.assertNotEqual(
            run(
                ["git", "show-ref", "--verify", "refs/heads/merged"],
                self.repo,
                False,
            ).returncode,
            0,
        )

    def test_apply_local_rejects_a_stale_branch_tip_before_any_mutation(
        self,
    ) -> None:
        linked = self.create_merged_linked_worktree()
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        run(
            ["git", "commit", "--allow-empty", "-m", "changed"],
            linked,
        )

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale cleanup plan", result.stderr)
        self.assertTrue(linked.exists())
        self.assertEqual(
            run(
                ["git", "show-ref", "--verify", "refs/heads/merged"],
                self.repo,
            ).returncode,
            0,
        )

    def test_apply_local_rejects_a_worktree_dirtied_after_planning(
        self,
    ) -> None:
        linked = self.create_merged_linked_worktree()
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        (linked / "dirty.txt").write_text("dirty\n", encoding="utf-8")

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stale cleanup plan", result.stderr)
        self.assertTrue(linked.exists())

    def test_apply_local_rejects_a_changed_integration_commit(self) -> None:
        linked = self.create_merged_linked_worktree()
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        self.commit_file(
            self.repo / "after-plan.txt", "changed\n", "integration changed"
        )

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integration commit changed", result.stderr)
        self.assertTrue(linked.exists())

    def test_apply_local_rejects_tampered_paths_and_extra_actions(self) -> None:
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["actions"].append(
            {
                "kind": "remove_worktree",
                "path": str(self.root.resolve()),
                "branch_ref": "refs/heads/main",
                "expected_head": "0" * 40,
            }
        )
        plan_path.write_text(json.dumps(plan), encoding="utf-8")

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plan does not match current safe action set", result.stderr)

    def test_apply_local_binds_plan_to_independent_trusted_inputs(self) -> None:
        run(["git", "branch", "protected"], self.repo)
        installed = self.install_script()
        trusted_plan = self.root / "trusted-plan.json"
        run(
            [
                sys.executable,
                str(installed),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--protect",
                "protected",
                "--plan",
                str(trusted_plan),
            ],
            self.repo,
        )
        attacker_repo = self.root / "attacker-repo"
        shutil.copytree(self.repo, attacker_repo)
        run(["git", "branch", "attacker-target"], attacker_repo)
        attacker_plan = self.root / "attacker-plan.json"
        run(
            [
                sys.executable,
                str(installed),
                "plan",
                "--repo",
                str(attacker_repo),
                "--integration",
                "main",
                "--plan",
                str(attacker_plan),
            ],
            attacker_repo,
        )
        trusted_plan.write_text(
            attacker_plan.read_text(encoding="utf-8"), encoding="utf-8"
        )

        result = run(
            [
                sys.executable,
                str(installed),
                "apply-local",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--protect",
                "protected",
                "--plan",
                str(trusted_plan),
            ],
            self.repo,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trusted cleanup inputs", result.stderr)
        self.assertEqual(
            run(
                ["git", "show-ref", "--verify", "refs/heads/attacker-target"],
                attacker_repo,
            ).returncode,
            0,
        )

    def test_apply_local_rejects_a_plan_for_an_untrusted_integration(self) -> None:
        run(["git", "branch", "alternate"], self.repo)
        installed = self.install_script()
        plan_path = self.root / "plan.json"
        run(
            [
                sys.executable,
                str(installed),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "alternate",
                "--plan",
                str(plan_path),
            ],
            self.repo,
        )

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trusted cleanup inputs: integration", result.stderr)

    def test_apply_local_rejects_removed_protection_even_without_new_actions(
        self,
    ) -> None:
        run(["git", "switch", "-c", "protected-work"], self.repo)
        self.commit_file(
            self.repo / "protected.txt", "unique\n", "protected work"
        )
        run(["git", "switch", "main"], self.repo)
        installed = self.install_script()
        plan_path = self.root / "plan.json"
        run(
            [
                sys.executable,
                str(installed),
                "plan",
                "--repo",
                str(self.repo),
                "--integration",
                "main",
                "--protect",
                "protected-work",
                "--plan",
                str(plan_path),
            ],
            self.repo,
        )
        tampered = json.loads(plan_path.read_text(encoding="utf-8"))
        tampered["protected_branches"].remove("protected-work")
        plan_path.write_text(json.dumps(tampered), encoding="utf-8")

        result = self.apply_local(
            installed,
            plan_path,
            protect=("protected-work",),
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("trusted cleanup inputs: protected branches", result.stderr)
        self.assertEqual(
            run(
                ["git", "show-ref", "--verify", "refs/heads/protected-work"],
                self.repo,
            ).returncode,
            0,
        )

    def test_apply_local_rejects_malformed_oids_and_unknown_actions(
        self,
    ) -> None:
        self.create_merged_linked_worktree()
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        original = json.loads(plan_path.read_text(encoding="utf-8"))

        malformed = json.loads(json.dumps(original))
        malformed["actions"][0]["expected_head"] = "not-an-oid"
        plan_path.write_text(json.dumps(malformed), encoding="utf-8")
        malformed_result = self.apply_local(
            installed, plan_path, check=False
        )

        wrong_length = json.loads(json.dumps(original))
        wrong_length["actions"][0]["expected_head"] = "0" * 41
        plan_path.write_text(json.dumps(wrong_length), encoding="utf-8")
        wrong_length_result = self.apply_local(
            installed, plan_path, check=False
        )

        unknown = json.loads(json.dumps(original))
        unknown["actions"][0]["kind"] = "remote-delete"
        plan_path.write_text(json.dumps(unknown), encoding="utf-8")
        unknown_result = self.apply_local(installed, plan_path, check=False)

        self.assertIn("malformed cleanup plan", malformed_result.stderr)
        self.assertIn("malformed cleanup plan", wrong_length_result.stderr)
        self.assertIn("unknown cleanup action", unknown_result.stderr)

    def test_apply_local_reports_completed_actions_when_git_stops_midway(
        self,
    ) -> None:
        remote = self.root / "remote.git"
        run(["git", "init", "--bare", str(remote)], self.root)
        run(["git", "remote", "add", "origin", str(remote)], self.repo)
        run(["git", "push", "origin", "main:tracking-base"], self.repo)
        run(["git", "switch", "-c", "merged"], self.repo)
        self.commit_file(
            self.repo / "merged.txt", "merged\n", "merged but not upstream"
        )
        run(["git", "switch", "main"], self.repo)
        run(["git", "merge", "--ff-only", "merged"], self.repo)
        run(
            [
                "git",
                "branch",
                "--set-upstream-to",
                "origin/tracking-base",
                "merged",
            ],
            self.repo,
        )
        linked = self.root / "linked"
        run(["git", "worktree", "add", str(linked), "merged"], self.repo)
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)

        result = self.apply_local(installed, plan_path, check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(linked.exists())
        self.assertIn("completed-actions:", result.stderr)
        self.assertIn('"status": "removed"', result.stderr)
        self.assertIn("failed-target: merged", result.stderr)
        self.assertEqual(
            run(
                ["git", "show-ref", "--verify", "refs/heads/merged"],
                self.repo,
            ).returncode,
            0,
        )

    def test_apply_local_reports_completed_actions_on_a_recheck_failure(
        self,
    ) -> None:
        run(["git", "branch", "merged-one"], self.repo)
        run(["git", "branch", "merged-two"], self.repo)
        first = self.root / "linked-one"
        second = self.root / "linked-two"
        run(["git", "worktree", "add", str(first), "merged-one"], self.repo)
        run(["git", "worktree", "add", str(second), "merged-two"], self.repo)
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        module = self.load_installed_module(installed)
        real_collect_worktrees = module.collect_worktrees

        def collect_with_concurrent_change(repo: Path):
            worktrees = real_collect_worktrees(repo)
            if not first.exists():
                for worktree in worktrees:
                    if worktree["path"] == str(second.resolve()):
                        worktree["dirty"] = True
            return worktrees

        module.collect_worktrees = collect_with_concurrent_change
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            returncode = module.main(
                [
                    "apply-local",
                    "--repo",
                    str(self.repo),
                    "--integration",
                    "main",
                    "--plan",
                    str(plan_path),
                ]
            )

        self.assertEqual(returncode, 3)
        self.assertFalse(first.exists())
        self.assertTrue(second.exists())
        self.assertIn("completed-actions:", stderr.getvalue())
        self.assertIn('"target": "' + str(first.resolve()), stderr.getvalue())
        self.assertIn("failed-target: " + str(second.resolve()), stderr.getvalue())

    def test_stale_worktree_metadata_is_pruned_only_for_an_absent_path(
        self,
    ) -> None:
        linked = self.create_merged_linked_worktree()
        shutil.rmtree(linked)
        installed = self.install_script()
        plan_path = self.write_plan_with(installed)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))

        prune = next(
            action
            for action in plan["actions"]
            if action["kind"] == "prune_worktree_metadata"
        )
        self.assertEqual(prune["expected_paths"], [str(linked.resolve())])
        self.assertFalse(
            any(action["kind"] == "remove_worktree" for action in plan["actions"])
        )

        self.apply_local(installed, plan_path)

        listing = run(
            ["git", "worktree", "list", "--porcelain"], self.repo
        ).stdout
        self.assertNotIn(str(linked.resolve()), listing)

    def test_remote_refs_are_evidence_only_and_never_actions(self) -> None:
        origin = self.root / "origin.git"
        backup = self.root / "backup.git"
        run(["git", "init", "--bare", str(origin)], self.root)
        run(["git", "init", "--bare", str(backup)], self.root)
        run(["git", "remote", "add", "origin", str(origin)], self.repo)
        run(["git", "remote", "add", "backup", str(backup)], self.repo)
        run(["git", "push", "origin", "main"], self.repo)
        run(["git", "push", "backup", "main"], self.repo)
        run(["git", "branch", "merged-remote"], self.repo)
        run(["git", "push", "origin", "merged-remote"], self.repo)
        run(["git", "switch", "-c", "remote-only"], self.repo)
        self.commit_file(
            self.repo / "remote-only.txt", "unique\n", "remote-only work"
        )
        run(["git", "push", "origin", "remote-only"], self.repo)
        run(["git", "switch", "main"], self.repo)

        plan = self.plan_repository()

        remote_refs = {
            item["ref"]: item for item in plan["remote_tracking_branches"]
        }
        self.assertTrue(remote_refs["refs/remotes/origin/main"]["merged"])
        self.assertTrue(remote_refs["refs/remotes/backup/main"]["merged"])
        self.assertFalse(
            remote_refs["refs/remotes/origin/main"]["follow_up_candidate"]
        )
        self.assertTrue(
            remote_refs["refs/remotes/origin/merged-remote"][
                "follow_up_candidate"
            ]
        )
        self.assertFalse(
            remote_refs["refs/remotes/origin/remote-only"]["merged"]
        )
        self.assertFalse(
            remote_refs["refs/remotes/origin/remote-only"][
                "follow_up_candidate"
            ]
        )
        self.assertTrue(
            all(
                action["kind"]
                in {
                    "remove_worktree",
                    "prune_worktree_metadata",
                    "delete_branch",
                }
                for action in plan["actions"]
            )
        )

        unsupported = run(
            [sys.executable, str(SOURCE_SCRIPT), "remote-delete"],
            self.repo,
            check=False,
        )
        self.assertNotEqual(unsupported.returncode, 0)


if __name__ == "__main__":
    unittest.main()
