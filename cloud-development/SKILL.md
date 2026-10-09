---
name: cloud-development
description: Keep ongoing development in ephemeral cloud workspaces recoverable through verified code checkpoints, private-artifact accounting, and recovery handoffs. Use while work proceeds or resumes after interruption; exclude initial workspace setup, provider administration, and deployment.
---

# Cloud development

Keep a truthful recovery point for work that could disappear with its cloud workspace. Own checkpoint evidence and loss exposure, not project acceptance or permission.

AGENTS.md and current user authorization remain authoritative. This skill grants no publication, upload, credential, computer-task, restoration, deletion or recurring-transfer permission. A stored destination, old receipt or loaded skill is not authorization.

## Establish the current boundary

Inspect the actual workspace, governing instructions, repository/worktree or source snapshot, selected branch and commit, ongoing writers, and last verified checkpoint. Preserve pre-existing and concurrent work. Establish the approved publication route, destination and content scope separately from any private-copy route.

Reuse an existing versioned `workspace-setup.json` by identity and SHA-256, including its application identities and recipe/private-manifest references. Read the selected profile's own format documentation when needed; do not redefine it here. Treat readiness receipts as prior observations, not durability or acceptance. If no profile exists, use inspected equivalent evidence, label gaps and provisional assumptions, and block only operations whose prerequisites cannot be established. No other skill must have run.

Where available, `workspace-setup` owns setup/recovery readiness and `coordinator` owns roles, review gates and assignments. Supply them checkpoint facts; do not duplicate or override their decisions.

## Keep work recoverable as it proceeds

- At a small coherent milestone, identify the earliest real checkpoint eligible under current review, test and publication requirements. Preserve versioned tests, docs and approved evidence. Publish eligible commits promptly through the supported authorized route; do not wait for task completion or an unrelated private-copy gap. Open the authorized draft PR after the first real commit and keep it draft. Read [publication checkpoints](references/publication.md).
- At milestones, writer completion and handoff, inventory important new or changed untracked, ignored and generated artifacts as well as uncommitted code. Separate unique evidence/private inputs from reproducible caches. Record what remains cloud-only since the last verified copy. For a proposed or authorized private fallback, read [private artifacts](references/private-artifacts.md).
- Before a stable copy, reconcile active writers and in-flight operations with their owners. Do not interrupt someone else's work without authority. Include only a stable selected version, or exclude moving files and report the gap. A worker's “done” is a lead: inspect actual outputs, identities and terminal state. If a worker stalls, check its state and partial outputs before requesting redirection or replacement; avoid duplicate writers or transfers.
- At interruption, handoff or resume, select a coherent code-plus-artifact checkpoint and inspect current state before retrying any action. Read [recovery handoffs](references/recovery-handoff.md). Recovery planning and verification do not themselves authorize restoration.
- After verifying publication to origin, and at handoff, assess redundant backups using [backup retirement](references/backup-retirement.md). Inventory complete contents and dependency chains; preserve unique private material and exact history. Retire only proven redundant copies under current deletion authority, with a verified replacement and restore drill where needed. Do not let obsolete code-only copies accumulate, or treat a pushed tree as proof that a whole backup is redundant.

## When a checkpoint cannot finish

Pause the affected mutation on missing authority, canceled or denied action, unsafe content, identity mismatch, unavailable route or unresolved ownership. Report the exact operation/target, last verified checkpoint, exposed material and smallest needed decision or access. Do not repeat a canceled action, switch destination, initiate a new computer task or configure credentials to work around the stop. Reconcile uncertain remote effects read-only before any authorized retry.

Continue independent permitted work only where it preserves evidence and does not cross the blocked gate. An unavailable computer or credential need not block a separate already-authorized route, but it never authorizes inventing one. Do not promise automatic backup or schedule recurring transfers from this skill.

## Hand back facts

Report verified code identity/ref/time and PR state, separately verified private-copy identity/scope, pending operations or checks, remaining cloud-only exposure and the recovery record location. Qualify source snapshot versus full history, complete declared snapshot versus prerequisite-dependent overlay, and integrity verification versus tested restoration. Durability does not mean reviewed, accepted, merged or deployed.
