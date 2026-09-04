# Cleaning Git Repositories Skill Design

## Purpose

Create a portable Codex skill named `cleaning-git-repositories` for safely removing stale Git branches and unused worktrees. The skill should make routine, locally provable cleanup automatic while reserving ambiguous or remote-destructive decisions for a human.

## Scope

The skill will guide Codex to:

- discover the repository's integration branch, remotes, branches, and worktrees;
- refresh and prune remote-tracking metadata when network access and the user's request permit it;
- remove clean, unused worktrees and local branches whose tips are proven merged;
- summarize unmerged or otherwise ambiguous branches for human decisions;
- offer remote-branch deletion as a separate follow-up step requiring explicit approval; and
- report actions, skipped items, retained commit IDs, and recovery guidance.

The initial version will be a concise, self-contained `SKILL.md`. It will not add scripts, references, or assets unless validation reveals a need for deterministic supporting logic.

## Safety Model

The user's repository-cleanup request authorizes deletion of local items only when the skill can establish the required proof. It does not authorize force deletion, remote deletion, or deletion of ambiguous work.

The skill must never automatically delete:

- the current branch, the integration/default branch, or a protected branch;
- a branch checked out in any worktree;
- a dirty, locked, detached, missing-but-unverified, or otherwise ambiguous worktree; or
- a branch merely because it is old, its upstream is gone, its name looks temporary, or hosting metadata says a pull request was merged.

A local branch is automatically eligible only when Git proves its tip is an ancestor of the selected integration branch. Squash merges and rebases commonly fail that proof and must enter the human decision queue.

A worktree is automatically eligible only when its path and administrative state have been inspected, it is clean, it is not the active worktree, and removing it will not strand an unmerged branch. Stale administrative records may be pruned only after verifying that the recorded path is genuinely absent.

Before each deletion, retain enough evidence to report the item name and tip commit ID. Prefer ordinary safe deletion over force deletion. If the observed repository state changes during cleanup, stop and reassess instead of acting on stale inventory.

## Workflow

### 1. Preflight and inventory

Read the repository's controlling instructions and inspect Git state without mutation. Identify the current worktree, all linked worktrees, local branches, remote-tracking branches, remotes, and the likely integration branch. Infer the integration branch from reliable repository or remote metadata; ask the human when multiple plausible integration branches or authoritative remotes remain.

Fetch and prune remote-tracking references only when doing so is permitted and useful. A fetch failure does not make stale local knowledge trustworthy; disclose the limitation and restrict automatic cleanup to conclusions that do not depend on fresh remote state.

Record the inventory before mutating anything so the final report can account for every candidate.

### 2. Classify candidates

Classify each worktree and local branch as:

- **safe local cleanup**: all required proof is present;
- **retain**: active, protected, current, or clearly still useful; or
- **human decision required**: unmerged, dirty, detached, locked, conflicting, or insufficiently evidenced.

Age, naming patterns, missing upstreams, and pull-request state are supporting signals only. They may help rank or describe candidates but cannot independently authorize deletion.

### 3. Apply safe local cleanup

Remove eligible worktrees before deleting their associated branches. Recheck cleanliness, branch attachment, and ancestry immediately before the relevant mutation. Use non-force branch deletion for branches proven merged. Do not turn a failed safe deletion into a force deletion; move the item to the decision queue with the failure summarized.

Prune verified stale worktree metadata after real worktree paths have been checked.

### 4. Present ambiguous branches

For each branch needing a decision, provide a concise, comparable summary:

- branch name and tip commit ID;
- upstream and associated worktree state;
- ahead/behind counts relative to the integration branch;
- last commit subject, author, and date;
- changed-file summary and diff stat relative to the integration branch; and
- an evidence-labeled assessment such as active, abandoned candidate, possible squash merge, or uncertain.

Offer appropriate choices such as keep, inspect the full diff, archive with a tag, or delete. State which choice would require force deletion. Wait for explicit human direction before taking any destructive action on these items.

### 5. Offer remote cleanup separately

After local cleanup and human branch decisions are complete, list remote branches that appear eligible and explain the evidence for each. Remote deletion is a separate phase and requires explicit approval naming the targets or approving a clearly enumerated batch. Revalidate the targets before deletion and never infer remote-deletion permission from approval of local cleanup.

### 6. Report and recover

Report:

- worktrees and branches removed;
- stale metadata pruned;
- items retained or skipped and why;
- unresolved decisions;
- remote actions, if separately approved; and
- the recorded tip commit IDs and practical reflog or tag-based recovery guidance.

Do not claim the repository is clean if candidates remain unresolved or if freshness checks were unavailable.

## Error Handling

Treat inaccessible repository instructions, uncertain integration-branch selection, dirty worktrees, concurrent state changes, and failed proof checks as stopping conditions for the affected item. Continue with independent candidates only when their evidence remains valid.

Command failures should be reported with their practical consequence. Retrying is appropriate only after identifying a transient cause; force flags are not a generic recovery mechanism.

## Validation

Validate the skill's structure with the repository's skill validator. Review the instructions against representative cases:

- a feature branch fully merged into the integration branch;
- a squash-merged branch whose tip is not an ancestor;
- a branch with a gone upstream but unique commits;
- clean and dirty linked worktrees;
- stale worktree metadata with an absent path;
- multiple remotes or ambiguous integration branches; and
- an approved local cleanup followed by an unapproved remote deletion.

The skill passes when it routes only provably safe local items to automatic deletion, supplies concise decision evidence for the rest, and preserves the separate authorization boundary for remote deletion.
