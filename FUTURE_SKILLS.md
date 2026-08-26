# Future Skills Candidate Backlog

This document records workflow patterns that may deserve reusable Codex skills. It is a candidate backlog, not an implementation commitment, execution plan, or source of authority. Project instructions and user direction remain controlling.

## Qualification criteria

Promote a pattern only when:

- evidence from multiple projects, or repeated failures in materially different workflows, shows a stable need;
- it contains a non-obvious invariant or decision process that improves outcomes beyond ordinary model capability;
- its trigger boundary is narrow enough to avoid burdening routine work;
- the portable behavior can be separated cleanly from project terminology, schemas, paths, permissions, and authority rules;
- it owns a coherent outcome without duplicating an existing skill; and
- realistic examples exist for forward-testing the smallest useful skill.

## Initial candidates

### Governed change control and evidence provenance

- **Trigger boundary:** Changes whose governing policy requires state transitions or consequential completion actions to be bound to exact artifacts, approvals, and durable evidence. It should not trigger for ordinary edits, routine verification, or informal progress tracking.
- **Reusable invariant/workflow:** Preserve a verifiable chain from authorized starting state to applied result. A candidate could bundle tracking-first state transitions, exact artifact identity, approval binding, risk-proportionate checkpoints, atomic completion application, and post-application fidelity checking. The reusable contract is that approval and completion apply to the same identified payload, and that the resulting state can be mechanically reconciled with it.
- **Must remain project-specific:** Status vocabulary and allowed transitions; evidence locations and retention rules; record schemas; designated authorities; protected files; required hashes or identifiers; retry limits; and which actions require checkpoints or atomic application.
- **Dependencies and overlap:** Complements the thin `coordinator` skill's routing and evidence-aware handoffs. Git worktree, commit, merge, and push mechanics belong to existing dedicated Git/worktree workflows unless repeated evidence demonstrates a gap that those skills cannot own.
- **Evidence needed before authoring:** At least two distinct control planes with the same provenance invariant but different records and terminology; examples where ordinary coordination loses artifact/approval identity; and pressure tests showing which checks must be mandatory versus project-configurable.
- **Current disposition:** Promising, but hold for cross-project evidence and boundary testing. Prefer one cohesive change-control skill over separate speculative skills for each mechanism.

### Governed review loop

- **Trigger boundary:** Workflows that genuinely require separated authorship, independent requirements review, implementation, and final verification because independence is mandated or materially reduces authority, safety, irreversibility, or broad-impact risk. It should not turn normal implementation or ordinary code review into a four-role ceremony.
- **Reusable invariant/workflow:** Keep role ownership and judgments independent; bind implementation to approved requirements; route findings to the role that owns the underlying artifact; preserve adverse findings through focused remediation; and allow completion only after final verification of the current implementation against the approved requirements.
- **Must remain project-specific:** Role names, freshness rules, review report formats, retry counts, acceptance gates, escalation authorities, allowed-file boundaries, required evidence, and the exact meaning of approval or completion.
- **Dependencies and overlap:** Specializes the staged path already recognized by `coordinator`; it must not absorb general delegation, workspace orchestration, or specialist implementation. Workspace isolation may use existing Git/worktree skills, but Git operations are not the review loop itself.
- **Evidence needed before authoring:** Repeated use in more than one project; examples where a general coordinator handoff is insufficient; demonstrated independence failures or gate confusion; and forward tests proving a dedicated skill selects the governed loop only when warranted.
- **Current disposition:** Conditional candidate. Author only if real workflows demonstrate a recurring, portable review protocol beyond the coordinator's current general guidance.

## Project-policy boundary

The following are control-plane choices, not standalone reusable skills: exact retry counts, project status names, evidence paths, record schemas, backlog selection rules, and repository permissions. They may configure a reusable workflow but must remain in the applicable project's authoritative instructions.

Likewise, worktree creation, commit construction, merge strategy, and push mechanics overlap with dedicated Git/worktree workflows. Extend those workflows only for a demonstrated reusable gap; do not recreate them inside coordination, change-control, or review-loop skills.

Revisit this backlog when new project evidence changes a candidate's boundary, demonstrates a missing invariant, or shows that an existing skill already covers the need.
