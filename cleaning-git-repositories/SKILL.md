---
name: cleaning-git-repositories
description: Use when cleaning a Git repository by removing merged local branches, unused worktrees, or stale worktree metadata, and when unmerged branches need concise human decisions. Exclude ordinary branch creation and active feature development.
---

# Cleaning Git Repositories

Remove only locally provable clutter. Treat the cleanup request as authorization for safe local cleanup, not force deletion, ambiguous branch deletion, or remote deletion.

AGENTS.md remains authoritative. Read the repository's controlling instructions before inventory or mutation.

## Establish the cleanup basis

Identify the integration branch and protected branches from reliable repository configuration or explicit user direction. Stop and ask when multiple integration branches or authoritative remotes remain plausible.

Fetch and prune remote-tracking metadata only when the request and environment permit network access. If freshness cannot be established, disclose that limitation and do not draw remote-dependent conclusions from stale refs.

Resolve this skill's own directory, then create a read-only plan:

```text
python3 <skill-directory>/scripts/repository_cleanup.py plan \
  --repo <repository> \
  --integration <local-integration-branch> \
  --plan <plan.json> \
  --protect <protected-branch>
```

Repeat `--protect` as needed. Review the generated Markdown summary and JSON plan before applying anything.

The helper treats a branch as safe only when its exact tip is an ancestor of the recorded integration commit. It treats a worktree as removable only when it is non-current, clean, unlocked, attached to such a merged branch, and still matches the plan. Stale worktree metadata is eligible only when the recorded path is absent and Git marks the entry prunable. Age, naming, a missing upstream, and pull-request metadata are never deletion proof.

## Apply safe local actions

Use `apply-local` only when the script is a reviewed, real, non-symlinked installation under `.agents/skills/cleaning-git-repositories` or `/etc/codex/skills/cleaning-git-repositories`, and the active permission profile keeps that installation recursively outside agent-writable space. Assume invocation may not prompt for approval.

```text
python3 <protected-skill-directory>/scripts/repository_cleanup.py apply-local \
  --repo <repository> \
  --integration <local-integration-branch> \
  --plan <plan.json>
```

Repeat `--protect <protected-branch>` exactly as for `plan`. Supply the repository, integration branch, and protected branches again from the independently established cleanup basis; never copy them from the plan. The helper rejects a plan whose recorded authority differs from these trusted apply-time inputs.

The helper revalidates repository identity, integration commit, protected branches, the complete action set, branch tips, and worktree state. It removes worktrees before branches, uses `git branch -d`, and never force-deletes or mutates a remote.

If the installation is writable, symlinked, or its protection is uncertain, use the helper for planning only. Perform approved local changes as visible, individually scoped Git commands after repeating the same checks. Never turn a failed safe deletion into a forceful fallback.

If repository state changes, stop acting on the stale plan. Report completed actions before generating a fresh plan for what remains.

## Route uncertain items to the human

Never automatically delete the current branch, integration branch, a protected branch, a branch in a retained worktree, or a dirty, locked, detached, unmerged, or unverifiable worktree.

For each branch that needs a decision, present a concise comparable record:

- branch name, tip commit, upstream, and worktree state;
- ahead/behind counts against the integration commit;
- last commit subject, author, and date;
- changed-file summary or diff stat; and
- an evidence-labeled assessment such as active work, possible squash merge, abandoned candidate, or uncertain.

Offer only relevant choices: keep, inspect the full diff, archive with a tag, or delete. Say explicitly when deletion would require force. Wait for the human's explicit selection before mutating any uncertain item.

## Keep remote deletion separate

After local cleanup and branch decisions, offer remote cleanup as a distinct follow-up. Enumerate each candidate by remote, branch, tip commit, and merge evidence. Exclude protected names and unmerged tips.

Remote deletion requires explicit approval of the exact target or clearly enumerated batch. Revalidate each approved ref immediately before using a visible command such as `git push --delete <remote> <branch>`. Approval of repository cleanup or local deletion never implies remote approval.

## Report the result

Report removed worktrees and branches, pruned metadata, retained or skipped items with reasons, failures and partial progress, unresolved human decisions, and any separately approved remote actions. Include recorded tip commits and practical reflog or tag-based recovery guidance. Do not call the repository clean while candidates remain unresolved or required freshness checks were unavailable.
