---
name: agent-handoff
description: Prepare or recover a manual transfer of unfinished implementation between agent sessions or native tools, including an abrupt stop without a final checkpoint. Preserve editing ownership, partial work, and test and review history.
---

# Agent handoff

Make an unfinished assignment resumable without the predecessor's conversation. This skill owns transfer and recovery; the assignment's implementation, review, tracker, and release rules still govern the work. A tool switch grants no new scope or authority.

## Record before launch

The operator or coordinator owns one retained handoff record for the assignment. Put it and its evidence outside any worktree scheduled for removal, following the project's retained-output convention. Link authoritative requirements and tracker records instead of maintaining a second backlog or copying the conversation. Keep earlier attempts and evidence when updating the record.

Include only task-relevant information authorized for the replacement provider; exclude credentials and unrelated private material. Record the stop cause as unknown unless observed, and label simulated interruptions as simulated.

Before starting a worker, record the assignment, its preservation baseline, and a unique attempt identity. Resolve required inputs and authorization before dependent work. Use this compact outline, combining inapplicable fields; write `unknown` for unavailable facts instead of guessing:

```text
ASSIGNMENT: task/slice; objective; authoritative request/contract and version;
acceptance criteria; instructions and selected skills to read directly.
AUTHORITY: allowed edits/actions; exclusions; decision owner; completion steps
and their authorization sources; who may accept, integrate, or release work.
WORKSPACE: repository; exact worktree; branch; starting revision; pre-existing
staged/unstaged/untracked work and preservation evidence; retained evidence path.
ATTEMPT: unique ID; assigned tool/model; operator/worker; launch or session handle;
other sessions, commands, children, or background jobs that may write or retry.
RELEASE: each prior possible writer; release status; who confirmed it, when,
and from what observation; retry/resume disposition; current editing owner.
PROGRESS: checkpoint time; observed changes; unfinished work; next bounded action;
assumptions, failures, and unknown or partially completed external operations.
CHECKS: exact commands; observed results; state tested; retained output locations.
REVIEW: resolved reviewer command/model and authorization source; packets/reports;
exchanges used; pending/failed invocations; stable findings and dispositions,
including disagreements; models that materially authored the change.
```

An attempt ID and a locatable launch context must exist before execution. On entry, confirm the actual tool/model against the assignment. A native session ID created by launch is initially `not yet created`; add it when available. Record model uncertainty explicitly and resolve it before work requiring reviewer independence. A first launch must also establish that no other writer owns the checkout.

Give the worker access to this same skill and record. Paste the following instruction into a fresh native Claude Code or Codex session in the assigned checkout, replacing the placeholders with resolved absolute paths and the recorded attempt ID:

```text
Read and apply <path to agent-handoff/SKILL.md> and read <path to handoff record>.
You are attempt <ID>. Establish its ownership and recovery gates from current
sources, then continue the authorized assignment in <exact worktree path>.
Preserve prior work and evidence; report unresolved gates to the recorded owner.
```

This entry instruction uses the same source in either tool; it needs no launcher, copied skill, hook, or permanent tool configuration. Tool choice and supported session controls remain the operator's responsibility.

## Checkpoint during work

The worker refreshes progress and evidence after meaningful edits, checks, or review exchanges, and before a planned stop when possible. Identify what each check actually tested: a commit plus relevant dirty content or retained diff when needed, including untracked files and a different index version. A working-tree check does not validate different staged content. Preserve the command, observed outcome, and durable output link, including failures.

Record tool/model authorship and newly launched possible writers as they arise. Mark a check or external operation interrupted or unknown if no result was observed. A final message, clean Git status, quota error, or turn boundary is neither release evidence nor proof of completion. Recovery must work from the pre-launch assignment even if no checkpoint was refreshed.

## Transfer editing ownership

The operator or coordinator confirms release before the replacement edits. Inventory every session, child, running command, background job, or automatic retry that may still write this checkout. Use the native session/process controls and the owners' confirmations to stop or relinquish them; record the observations and their limits. A paused or idle worker alone is insufficient: it must surrender the assignment and must not resume or retry into the transferred checkout.

Name the inspected session/process scope: an empty process group alone does not establish that no other writer exists.

Confirm each possible writer's disposition and designate exactly one replacement owner. When the inventory is incomplete, liveness is unknown, or a writer can still resume automatically, replacement editing waits. Read-only inspection and resolving the stop are allowed; a stale checkpoint or lack of visible activity cannot clear this gate. Do not terminate unrelated work. Returning to an old session later requires the same release and reconciliation procedure.

## Reconcile actual state

Once release is established, the recovering owner compares the last record with the actual checkout before implementation. Read the controlling instructions and authoritative requirements directly; a summary locates them but does not replace them. Confirm repository, exact worktree, branch, HEAD, and any commits since the recorded revision.

Inspect the staged, unstaged, and untracked states separately: `git status --porcelain --untracked-files=all`, `git diff --cached`, `git diff`, and the files enumerated by `git ls-files --others --exclude-standard -z`. Handle that last inventory as NUL-delimited filenames and read the relevant file contents. Inspect task-owned ignored evidence and outstanding external operations separately when they affect continuation.

Reconcile those observations against the preservation baseline and checkpoint. Record discrepancies, useful partial work, unfinished changes, and the next bounded action. Keep unrelated edits and staged/unstaged distinctions intact; do not reset, clean, blindly overwrite, or stage everything to simplify transfer. A clean commit is not a prerequisite. If preservation or ownership of overlapping changes is uncertain, stop the affected edits and route the conflict to its owner.

Keep historic check results with their tested state. Later changes make an affected result's applicability unresolved until the relevant check is rerun on the current state. Missing output, an interrupted command, or a checkpoint's unsupported claim is unknown, never passing. Investigate an uncertain external operation before retrying it so a switch does not duplicate a side effect. The replacement records its reconciled starting state and then continues only within the assignment's authority.

## Carry review and authority forward

When the assignment uses `cross-model-review`, read that skill from its resolved location and continue the same task's advisory loop. Preserve the reviewer command/model and authorization, all packets and reports, stable finding IDs and dispositions, contested findings, and exchanges already used. Record invocation failures separately from review outcomes. Reconcile pending invocations and uncertain history before another call; switching sessions, tools, or reviewers does not restart the three-exchange allowance.

Before another review, recheck that the configured reviewer differs from the current implementer model. A matching or uncertain identity returns to the coordinator or other designated configuration owner; do not silently substitute a reviewer. Also disclose any overlap with earlier material author models and apply the governing independence policy. Prefer a reviewer outside that author set when available; any stronger requirement or changed reviewer assignment belongs to the designated authority.

Return the current files, preservation result, check evidence, review history, unresolved gates, and next owner. Distinguish returning implementation for review from acceptance or release. The switch changes neither required independent verification nor the authorization for commits, merges, publication, installation, or cleanup.
