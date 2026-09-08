---
name: workspace-scratch
description: Create, use, and safely clean named temporary task directories in an existing workspace. Use for disposable scratch lifecycle and temporary-file routing, not workspace setup, retained-artifact deletion, or Git branch/worktree cleanup.
---

# Manage workspace scratch

Keep disposable task files in a known location while preserving active work, deliverables, and recovery evidence.

## Select the workspace

Read the workspace instructions and identify the workspace the user intends to maintain; do not infer it from the skill's location or the current shell directory. The bundled POSIX helper accepts an explicit absolute `--workspace` path and manages only its existing real `tmp/` child. It rejects filesystem root, relative paths, traversal, and symlinked workspace/scratch paths. If the workspace uses a different scratch location, follow that convention without this helper.

Run the helper from the installed skill.

## Create and use task scratch

Use a unique, simple task name. If `tmp/` is absent, create that directory only within the workspace's authorized scratch policy. The helper does not initialize workspaces, choose retention policy, or adopt existing unmarked directories.

```sh
python3 <installed-skill>/scripts/workspace_scratch.py --workspace <absolute-workspace> create <task>
```

Use the printed absolute task path for explicit temporary files and process-scoped `TMPDIR`, `TMP`, or `TEMP` where supported. Verify actual placement: tools may ignore those settings. Track any temporary files created elsewhere separately; this helper cannot clean them.

Keep application repositories, worktrees, deliverables, reports, and recovery evidence out of task scratch. A marker records the task's lifecycle, not an authenticated owner or proof that every file is disposable.

## Complete, preview, and clean

Before completion, stop the task's writers, inspect its contents, and move retained data to its proper home. Work only on the caller's authorized task; a completed marker does not grant permission to delete another task's files.

```sh
python3 <installed-skill>/scripts/workspace_scratch.py --workspace <absolute-workspace> complete <task>
python3 <installed-skill>/scripts/workspace_scratch.py --workspace <absolute-workspace> clean <task>
python3 <installed-skill>/scripts/workspace_scratch.py --workspace <absolute-workspace> clean <task> --apply
```

Review the preview before applying cleanup. Cleanup removes only the named completed task and never the workspace or scratch root. Do not manufacture a marker to make an unknown directory eligible.

The helper refuses repositories, worktree markers, symlinks, hard links, special files, nested filesystem boundaries, and detected changes during cleanup. It does not lock out other processes: keep writers stopped and do not relocate the directory during deletion. A failure partway through cleanup may leave partial removal; inspect and report what remains before retrying. Git worktrees require Git-aware lifecycle handling, outside this skill.

Report the task location, retained data moved elsewhere, cleanup performed or previewed, and any refusal. Do not report cleanup complete when files remain unresolved.
