# Garage-local scratch and worktree placement — 2026-09-04

The user requested extending workspace-setup after reporting temporary-file and worktree placement friction. This update belongs to `codex/workspace-local-storage`, following the merged initial workspace-setup implementation. No live workspace, installation, approval rule or application repository was changed.

## Implemented behavior

The default scaffold now creates ignored `tmp/` and `.worktrees/` homes, records per-task scratch and per-app worktree conventions in root instructions, and installs `support/workspace_scratch.py`. The root ignore allowlist includes only that actual support file, not all support descendants. Existing garages use additive inspection/setup; the scaffold still refuses occupied directories and ancestor repository ownership. The refactoring reference includes active scratch/writers, retained recovery evidence and registered worktrees in its inventory.

The POSIX helper anchors its scope to its installation's `tmp/` directory. It accepts a single task name, not a root/path argument. `create` exclusively makes a directory and active ownership marker; `complete` declares writers stopped and contents disposable; `clean` previews unless given `--apply`. Completion is a caller declaration, not a process detector or a proof of retention policy. Repositories, worktrees, unmarked or active tasks, symlinks, hard links, special files and nested filesystem boundaries are refused. Cleanup deletes inventoried entries through directory descriptors, checks identities and refuses detected changes. It preserves other task directories and data outside scratch in the tested cases.

Worktree guidance preserves each application's Git ownership and shared metadata, distinct app/task paths, collision checks and actual access boundaries. It does not create worktrees during scaffolding, move existing worktrees for naming consistency, or promise control over app-managed worktree placement. Worktrees use Git-aware cleanup, never scratch deletion.

## Executable checks

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_workspace_*.py'` passed 19 tests: the 9 existing scaffold cases with updated layout/index expectations, plus 10 scratch/worktree cases. They exercise:

- Real Git initialization, root allowlist/exclusions, rerun and occupied-path preservation, ancestor repositories, bare repositories, linked worktrees, paths with spaces, and symlink refusal.
- Scratch create/complete/preview/apply, actual Python temporary-file routing with process-scoped settings, and preservation of a neighboring active task and artifact evidence.
- Invalid/path arguments, unmarked directories, occupied task names, active tasks, symlinks, hard links, FIFOs, repository/worktree content, scratch-root repositories, and unsupported/symlinked installation locations.
- Changed files, newly appeared entries, and directory-to-symlink substitution between inventory and deletion. External data and replaced directory contents survived the substitution case.
- Real linked worktrees for two independent apps under `.worktrees/<app>/task-a`, each resolving its own shared Git metadata, excluded from the garage index, and preserved with dirty files when scratch deletion was attempted using a traversal argument.

Tests requiring new garage initialization use permitted system temporary storage outside any ancestor repository, because the scaffold intentionally refuses initialization inside the skills repository. This is an explicit test constraint, not a claim that all system temporary storage is outside a sandbox.

Final validation passed all 19 tests after the last code changes, the bundled skill validator, changed-file whitespace and Markdown link checks, and `git diff --check`. No new dependency installation was needed.

## Independent review and limits

An independent reviewer read the implementation and exercised its own disposable fixture at `/private/tmp/scratch-review-ovf0764l`. Lifecycle, preview, neighboring-task preservation, refusal cases, installation symlinks, ignore boundaries and nested Git ownership passed. No blocking defect was found within the documented stopped-writers/no-relocation scope.

The reviewer reproduced an out-of-scope concurrent rename: moving an already-open task directory outside scratch just before removal allowed its original contents to be deleted through the pinned descriptor before final pathname verification failed. The skill now explicitly avoids claiming complete race isolation and requires no concurrent writers or relocation during cleanup. Subsequent edits also bind marker identity to inspection and preserve newly appeared entries/ownership markers when detected. Mid-cleanup failure may leave partial deletion; no rollback is promised for declared disposable scratch. A mutable helper must not receive standing outside-sandbox approval merely because it has a narrow CLI.

Actual mount-boundary behavior, malicious concurrent filesystem activity isolation, host-managed worktree destination changes, and fresh-host loading of the updated generated instructions were not tested. Prior standalone garage startup evidence applies to the earlier version. The tests establish actual local filesystem/Git behavior, not universal approval-free execution or a guarantee that every tool honors temporary-directory environment variables.
