# Workspace document ownership — 2026-09-05

The user requested three clarifications through the Set Up Garage Workspace task: lasting workspace plans/contracts/decisions belong in tracked garage documentation; retained reports and disposable scratch have different ownership and retention; migration handoffs need one authoritative document with clearly identified snapshots and location transitions. Scope is the reusable skill source only. No ACKS workspace, application, pinned installation or recovery data was inspected or changed.

## Changes

- The skill distinguishes workspace documentation, application documentation, retained generated work and disposable scratch by purpose, including agent-generated documents.
- The scaffold creates an empty `docs/` directory and makes top-level `docs/*.md` eligible for tracking. Its generated README and AGENTS guidance direct lasting workspace plans, decisions and contracts there, require explicit exceptions for other selected paths/formats, and require content review before staging. Raw recovery data and nested local files remain ignored by default; Markdown eligibility is not proof that content is safe to track.
- The refactoring reference retains copy-first migration and source cleanup safeguards, while specifying an interim authoritative location when the garage is not yet writable, verified transfer into tracked garage docs, one authority at a time, snapshot source identity and forwarding pointers, and receiving-session reconciliation against the current record. Contracts and recovery snapshots stay outside disposable scratch. Sensitive/machine-local evidence is referenced from retained appropriate storage rather than indiscriminately tracked.
- Existing local scratch and worktree behavior is unchanged.

## Verification

All 20 tests passed with `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_workspace_*.py'`. The added real-Git test stages workspace plans/contracts/decisions in the garage while application README stays in its own repository; reports, scratch, raw recovery and nested local files remain excluded. It also explicitly includes one nested documentation file while keeping its adjacent local data ignored. Existing scaffold refusal and scratch/worktree tests passed unchanged apart from the new empty `docs/` layout expectations.

The bundled skill validator and `git diff --check` passed. These checks establish scaffold/tracking behavior; they do not mechanically prove an agent will resolve document authority correctly in every migration. No live migration or skill reinstallation was performed.

An independent read-only review applied the instructions to an already-copied application with an ignored contract, an older handoff in source scratch, retained reports, a machine-local backup and normal build docs. It proposed a reviewed tracked garage contract, an identified retained snapshot outside scratch, ignored report/backup storage and application-owned build docs. It required reconciliation and verified authority transfer without using timestamps or deleting anything under planning-only authorization. It found no material contradiction across the skill, refactoring reference and scaffold guidance, and confirmed copy-first and local scratch/worktree rules were preserved. This is a bounded planning review, not execution of a document migration or fresh-host startup test.

## Subsequent user-directed planning and retirement changes

The user additionally requested early naming choices and a visual migration planning checkpoint. The entry point and reference now require a proposed directory tree/diagram and keep/copy/rename map, allow user revisions, and obtain approval of that concrete layout before migration mutations. Already supplied names and approved plans are reused; the scaffold is optional and no automatic “garage” suffix is imposed.

The reference also makes original-checkout disposition explicit at cutover. Immediate authorized deletion can skip an unnecessary retirement notice; a retained copy can receive a notice when needed, using the project's applicable amendment workflow. Retirement is not mandatory for every migration, does not waive deletion rules and does not establish that active sessions have reloaded instructions. No live retirement or deletion was performed.

These later changes are instruction-only. Skill validation and diff whitespace checks passed; the earlier 20-test run covers the unchanged scaffold code, while the independent review above predates these later planning/retirement additions.
