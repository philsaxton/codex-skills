---
name: cleaning-git-repositories
description: Use for repository-wide or cycle-scoped Git cleanup of merged local branches, released worktrees, and stale worktree metadata, and when unmerged branches need concise human decisions. Exclude ordinary branch creation and active feature development.
---

# Cleaning Git Repositories

Remove only locally provable clutter. Treat the cleanup request as authorization for safe local cleanup, not force deletion, ambiguous branch deletion, or remote deletion.

AGENTS.md remains authoritative. Read the repository's controlling instructions before inventory or mutation.

Establish whether the assignment covers the repository or an explicitly bounded work cycle. A coordinator's cleanup handoff authorizes only its named targets and actions under the project's completion rule. Repository-wide inventory may supply evidence; it never expands a cycle's mutation scope. Follow the cycle-specific section below for a bounded assignment.

## Establish the cleanup basis

Identify the integration branch and protected branches from reliable repository configuration or explicit user direction. Stop and ask when multiple integration branches or authoritative remotes remain plausible.

Record the primary worktree and any checkout designated by repository instructions for the integration branch. Flag a branch-to-worktree mismatch even when no worktree or branch is eligible for deletion; placement alone is never deletion proof.

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

The helper treats a branch as safe only when its exact tip is an ancestor of the recorded integration commit. It treats a worktree as removable only when it is non-current, clean, unlocked, attached to such a merged branch, and still matches the plan. Before removing a worktree, establish that no active task or other writer is using it; clean and unlocked state alone does not establish that it is unused. Stale worktree metadata is eligible only when the recorded path is absent and Git marks the entry prunable. Age, naming, a missing upstream, and pull-request metadata are never deletion proof.

## Clean up a completed cycle

Read the handoff's repository identities, exact allowed refs and expected tips, worktree paths, completion rule and its authority, completion evidence, and worker release evidence. Check these against the controlling instructions and current repository state. Missing scope, unresolved policy, or a failed required completion step leaves the affected artifacts pending; return the gap to the coordinator without merging or pushing to make cleanup possible.

Use the helper for planning only in this mode. Its action list and `apply-local` operation cover the repository, not a selected subset. Do not edit a generated plan to narrow it and then apply it. Perform only visible, individually scoped Git commands, repeating the identity, tip, ancestry, protection, and worktree checks immediately before each action. Do not run repository-wide worktree pruning; report any in-scope stale registrations for a separately scoped follow-up.

Remove only explicitly released worktrees that are non-current, unlocked, attached to the expected retained branch tip, unused by any task or writer, and clean of tracked, untracked, and ignored files needing preservation. Retain needed evidence outside the worktree before removal and recheck cleanliness. Preserve designated integration checkouts and checkouts on protected branches. Honor host ownership and use supported controls for host-managed worktrees; do not bypass an unavailable or refusing control with raw removal.

An unmerged worktree may be removed only when the project rule explicitly permits it and all required completion steps have succeeded. Verify that its branch still retains the exact commit, leave that branch intact, and report its ref and tip. This exception releases a checkout, not its unmerged history. Without that rule, retain both branch and worktree. The helper remains conservative and does not implement this exception.

For branch deletion, require the exact tip to be an ancestor of the selected integration commit, all required completion steps to have succeeded, and the branch to be outside current, protected, or retained-worktree state. A retention rule overrides deletion eligibility. Remove eligible worktrees before branches, use `git branch -d`, and never force a failed deletion. If relevant state changes, stop the affected actions and return the changed evidence and any partial progress.

Return removals, intentional retention, failures, and unresolved in-scope decisions to the coordinator. Leave unrelated backlog and remote branches alone; do not solicit repository-wide or remote cleanup decisions as part of this cycle.

## Apply safe local actions

This section applies to repository-wide cleanup. Cycle-scoped assignments use the individually scoped actions above.

Use `apply-local` only when the script is a reviewed, real, non-symlinked installation under `.agents/skills/cleaning-git-repositories` or `/etc/codex/skills/cleaning-git-repositories`, and the active permission profile keeps that installation recursively outside agent-writable space. Assume invocation may not prompt for approval.

If the installation is writable, symlinked, or its protection is uncertain, use the helper for planning only. Perform approved local changes as visible, individually scoped Git commands after repeating the same checks. Never turn a failed safe deletion into a forceful fallback.

```text
python3 <protected-skill-directory>/scripts/repository_cleanup.py apply-local \
  --repo <repository> \
  --integration <local-integration-branch> \
  --plan <plan.json>
```

Repeat `--protect <protected-branch>` exactly as for `plan`. Supply the repository, integration branch, and protected branches again from the independently established cleanup basis; never copy them from the plan. The helper rejects a plan whose recorded authority differs from these trusted apply-time inputs.

The helper revalidates repository identity, integration commit, protected branches, the complete action set, branch tips, and worktree state. It removes worktrees before branches, uses `git branch -d`, and never force-deletes or mutates a remote.

If repository state changes, stop acting on the stale plan. Report completed actions before generating a fresh plan for what remains.

## Restore checkout placement

When cleanup includes restoring a repository's declared checkout layout, handle it separately from branch or worktree deletion. Inspect both affected worktrees for changes, locks, active writers, and tasks that rely on their current branches. An active feature task in the designated checkout is a reason to defer restoration, even if Git reports a clean working tree. If neither checkout is in use and both can switch safely, release the integration branch from the linked worktree, then switch the designated checkout to that branch and verify the resulting mapping. Preserve all branch refs and uncommitted work. Do not auto-stash, reset, force a checkout, or remove a host-managed worktree to make restoration possible. If either checkout is in use or cannot switch safely, leave it in place and report the exact paths, branches, and blocker. Regenerate any cleanup plan after a branch switch.

## Route uncertain items to the human

Never automatically delete the current branch, integration branch, a protected branch, a branch in a retained worktree, or a dirty, locked, detached, or unverifiable worktree. Retain unmerged worktrees except for the explicitly permitted cycle-scoped checkout release above; never treat that exception as authority to delete the unmerged branch.

For each branch that needs a decision, present a concise comparable record:

- branch name, tip commit, upstream, and worktree state;
- ahead/behind counts against the integration commit;
- last commit subject, author, and date;
- changed-file summary or diff stat; and
- an evidence-labeled assessment such as active work, possible squash merge, abandoned candidate, or uncertain.

Offer only relevant choices: keep, inspect the full diff, archive with a tag, or delete. Say explicitly when deletion would require force. Wait for the human's explicit selection before mutating any uncertain item.

## Keep remote deletion separate

For repository-wide assignments, after local cleanup and branch decisions, offer remote cleanup as a distinct follow-up. Enumerate each candidate by remote, branch, tip commit, and merge evidence. Exclude protected names and unmerged tips.

Remote deletion requires explicit approval of the exact target or clearly enumerated batch. Revalidate each approved ref immediately before using a visible command such as `git push --delete <remote> <branch>`. Approval of repository cleanup or local deletion never implies remote approval.

## Report the result

Report the assignment's scope, removed worktrees and branches, pruned metadata, retained or skipped items with reasons, failures and partial progress, unresolved human decisions, and any separately approved remote actions. Include recorded tip commits and practical reflog or tag-based recovery guidance. Do not call the repository clean after cycle-scoped cleanup, while candidates remain unresolved, or when required freshness checks were unavailable.
