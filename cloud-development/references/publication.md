# Publication checkpoints

Use at an eligible code checkpoint or after an uncertain publication outcome. Follow the project's Git and provider workflow; this reference defines evidence, not a replacement transport.

## Select and review the outgoing checkpoint

Choose a small coherent change that satisfies the project's gates for a checkpoint. Work in progress can be durable when those gates permit it; label pending tests/review honestly. Do not manufacture empty changes just to create a PR or bypass a required review to reduce cloud exposure.

Record repository, intended branch, base/parent, commit and root tree where available, plus the reviewed file/content manifest. Inspect staged/uncommitted changes and concurrent ownership before staging only the authorized scope. Include eligible tests, docs and provenance with their code. Review all newly reachable commits and their files, not just HEAD or the final diff, against current publication exclusions. Private source PDFs/extracts prohibited by project policy stay out even in a private repository; deleting them in a later commit does not remove them from history. Never publish credentials or unrelated private material. Stop affected publication when excluded content is reachable; report the problem without unapproved history rewriting.

Distinguish two source models:

- **Genuine Git checkout:** preserve the intended exact commits, parent order, trees, file modes and history through a supported route. If that route cannot preserve them, report the exact limitation. A reconstructed tree or new commit is not the original history.
- **Verified source snapshot:** identify its remote source commit/tree and complete file manifest. A supported provider can create an explicitly new reviewed commit based on that remote parent, preserving the existing remote ancestry. Record the returned new commit identity and verify it. Do not claim a local history push, manufacture historical metadata, or infer historical objects exist locally. If the task requires exact local commits/history, a snapshot is insufficient.

## Publish, then verify

Recheck the destination ref before publication. Respect concurrent changes; use supported expected-head safeguards and ordinary fast-forward behavior. A moved ref requires reconciliation and re-review of affected content, not force pushing. Use the project's approved connector/tool and current supported interface. Missing capability is a blocker, not permission to create a shell bridge, change transport, set credentials or use another computer.

Publish the first eligible real checkpoint and create its draft PR when authorized. Verify the PR's repository, base, head branch, head SHA, open/closed and draft state. For stacked work, record the precise upstream branch/commit and dependency; do not silently target main or retarget a PR.

Before saying **remote-verified**, read the actual destination ref and commit independently of the mutation response. Compare the exact intended commit and tree, and verify the tree against the reviewed complete manifest, including file modes and deletions. Git object identities may establish content identity when they were computed/verified from the exact reviewed bytes; an unverified reported SHA alone does not. Record the remote observation time and source of evidence. A successful command or created blob/commit that is not reachable from the intended ref is not a branch checkpoint.

Keep states separate: content created, ref verified, PR verified, required checks/reviews pending or complete. Ref durability can be established while PR creation fails; a visible PR cannot prove an unverified push. A code checkpoint does not cover uncommitted edits or private artifacts. Do not upgrade stale observations after the branch or files change.

## Reconcile partial or interrupted operations

For a timeout, disconnected worker or lost response, inspect the exact destination, existing PR and relevant object identities before retrying. The requested commit or PR may already exist. If the ref now matches but PR metadata is stale, retain the code result and recheck the PR through supported reads; do not recreate the commit or duplicate the PR.

A known denial or user cancellation stops the affected mutation until the required authority is re-established. For an ordinary transient failure, retry only within existing authorization and a risk-appropriate bounded policy after inspecting state. Stop repeated unchanged failures and return the blocker. Preserve local-only commits/changes and the last verified point; do not call them lost simply because publication failed.
