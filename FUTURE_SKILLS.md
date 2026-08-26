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

## Standalone-role principle

Every reusable role skill must be operationally standalone. It may require task evidence or authoritative inputs, but it must not assume that another named skill ran or exists. References to other skills describe optional overlap or artifact ownership, never runtime prerequisites.

When a formal controlling artifact is absent, use the best available evidence, such as the user request, issue, accepted plan, relevant documentation, and current deliverable. Publish any inferred intent, scope, criteria, or assumptions in the output together with their evidence and material uncertainty; inference remains provisional and must not silently become approved authority. Withhold only a judgment that genuinely requires authority the available evidence cannot establish.

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

### Contract reviewer

- **Trigger boundary:** A proposed contract, specification, or other recorded task basis needs a separate review of whether another practitioner could implement and verify it without inventing requirements. It should not trigger for drafting, collaborative redlining, or review of a completed implementation.
- **Reusable invariant/workflow:** Evaluate intended outcome, scope and non-goals, internal consistency, feasibility, acceptance criteria, and material risk coverage; return prioritized findings, questions, and a clear readiness conclusion without silently rewriting the contract. If no formal contract exists, state the inferred review basis, requirements, evidence, and uncertainty without treating them as approved authority.
- **Must remain project-specific:** Approval authority, required sign-offs, severity labels, domain checklists, templates, record formats and locations, versioning conventions, deadlines, and escalation rules.
- **Dependencies and overlap:** `contract-author` may own a formal contract and `coordinator` may own assignment or routing when those skills are present; neither is a runtime prerequisite. A contract-reviewer skill would own only the review judgment and remain distinct from later review of the delivered result.
- **Evidence needed before authoring:** Develop independent cross-project scenarios showing recurring specification-review failures, useful reviewer decisions, and a stable boundary from editing and final review. Only afterward should project role documents be used as comparison material, not as design evidence.
- **Current disposition:** Exploratory candidate. Author only if independent evidence shows a repeatable gap beyond contract-author self-checks and ordinary document review.

### Final reviewer

- **Trigger boundary:** A completed deliverable needs an outcome-focused review against agreed requirements before it is represented as complete. It should not trigger for proposal or contract review, implementation work, remediation, or routine checks performed during development.
- **Reusable invariant/workflow:** Inspect the current deliverable and requirements, reproduce or examine proportionate verification, trace observable outcomes to acceptance criteria, assess material gaps and residual risks, and issue a clear conclusion. If no formal contract exists, enter a clearly labeled inferred-intent or general-review mode: publish the inferred intent and review basis in the report, invite human correction, report defects and risks normally, distinguish the result from verified conformance to an approved contract, and withhold only a formal acceptance or completion judgment that truly requires confirmed authority. The reviewer reports findings rather than editing the work under review.
- **Must remain project-specific:** Release gates, approval authority, environments, tools and commands, report templates, evidence storage, artifact identifiers, sign-off rules, and remediation or escalation policy.
- **Dependencies and overlap:** `coordinator` may provide routing or separation and `contract-author` may provide formal criteria when those skills are present; neither is a runtime prerequisite. Contract review judges whether the specification is ready, while final review judges the delivered result against the best supported review basis.
- **Evidence needed before authoring:** Develop independent cross-project examples where a distinct final review changes outcomes beyond ordinary testing or peer review, plus boundary tests separating it from contract review and implementation. Compare project role documents only later, after the portable concept stands on independent evidence.
- **Current disposition:** Unproven candidate. Keep it separate from general verification guidance only if independent evidence demonstrates a recurring final-judgment role with a stable portable core.

### Implementer

- **Trigger boundary:** An agreed contract or bounded work item needs an execution owner who will produce the scoped change and supporting verification. It should not trigger for planning, coordination, requirements authorship, independent review, or acceptance decisions.
- **Reusable invariant/workflow:** Clarify blocking ambiguity before changing work; translate criteria into the smallest coherent implementation; verify outcomes in proportion to risk; preserve unrelated work; surface assumptions, failures, and residual risks; and hand off the result and evidence without judging its own acceptance. If formal requirements are absent, state the inferred scope and criteria, supporting evidence, and material uncertainty before relying on them, and never convert inference into authority.
- **Must remain project-specific:** Technology stack, test strategy, commands, paths, allowed-file rules, branching and workspace conventions, evidence formats, deployment mechanics, approval gates, and team role arrangements.
- **Dependencies and overlap:** `coordinator` may provide scope or blocker routing and `contract-author` may provide formal requirements when those skills are present; neither is a runtime prerequisite. An implementer skill would own execution only, without absorbing orchestration, redefining requirements, or performing independent final review.
- **Evidence needed before authoring:** Develop independent cross-project cases showing failures that a role-scoped implementer skill prevents beyond existing coding, testing, planning, and workspace guidance. Use project role documents only for later comparison after that need and boundary are established independently.
- **Current disposition:** Tentative candidate because overlap risk is high. Author only if independent trials reveal a compact portable discipline that existing implementation skills do not already cover.

### Running discrete shell commands

- **Trigger boundary:** Command-line work is about to combine independently meaningful operations or obscure them behind shell convenience constructs. It should not burden a single direct command or a short readable pipeline whose stages form one data flow.
- **Reusable invariant/workflow:** Put one small coherent operation in each command tool call; run independently meaningful sequential operations as separate calls; allow short readable pipelines; prefer literal arguments and explicit paths; and do not hide operations in variables, substitutions, heredocs, generated scripts, or functions merely for convenience. Necessary shell complexity uses the smallest transparent form and is explained.
- **Must remain project-specific:** Sandbox permissions, approval configuration, command authorization, repository commands and paths, shell and tool interfaces, writable locations, and temporary-file policy. The skill changes none of those controls.
- **Dependencies and overlap:** The approved [design specification](docs/superpowers/specs/2026-08-25-running-discrete-shell-commands-design.md) defines the boundary, and the [implementation plan](docs/superpowers/plans/2026-08-25-running-discrete-shell-commands.md) defines the planned evaluation and delivery. The skill would shape command form only, without replacing authorization, safety, or workspace guidance and without requiring another named skill.
- **Evidence needed before authoring:** Execute the planned fresh-context controls and skill-guided pressure scenarios for chained Git operations, readable pipelines, and shell indirection; verify that the guidance separates independent work without producing awkward workarounds or broadening authority.
- **Current disposition:** Implementation-ready, pending execution and behavioral verification. Design and implementation planning are complete, but the actual skill has not yet been implemented.

## Project-policy boundary

The following are control-plane choices, not standalone reusable skills: exact retry counts, project status names, evidence paths, record schemas, backlog selection rules, and repository permissions. They may configure a reusable workflow but must remain in the applicable project's authoritative instructions.

Likewise, worktree creation, commit construction, merge strategy, and push mechanics overlap with dedicated Git/worktree workflows. Extend those workflows only for a demonstrated reusable gap; do not recreate them inside coordination, change-control, or review-loop skills.

Revisit this backlog when new project evidence changes a candidate's boundary, demonstrates a missing invariant, or shows that an existing skill already covers the need.
