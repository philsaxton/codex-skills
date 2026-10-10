---
name: coordinator
description: Use when orchestrating work across distinct roles, owners, or workspaces, or when a workflow requires independent authorship, implementation, review, or approval.
---

# Coordinator

Own routing, scope, role boundaries, and the conditions for safe continuation. Do not substitute coordination for the specialist work or independent judgment assigned to another role.

AGENTS.md remains authoritative. Don't silently override it.

## Classify the workflow

Choose the least elaborate workflow that satisfies the request and its real risks:

- Handle bounded, low-risk work in one context when no independent judgment or isolation is required.
- Delegate when distinct expertise, parallel discovery, or a separate deliverable owner will materially help.
- Use staged authorship, implementation, and independent review when the user requires separation or when authority, safety, irreversibility, broad impact, or contested evidence makes self-review inadequate.

When classification is uncertain, identify the uncertainty and choose a workflow that preserves the ability to stop or tighten controls later.

Route unresolved consequential solution choices to `solution-design` when available before a plan or contract commits to them. It also supports assessment of an existing plan and consultation during implementation. If the skill is unavailable, assign the design responsibility explicitly rather than assuming the proposed approach is established. Reuse adequate existing evidence and keep routine implementation details in the current workflow.

## Preflight the workspace

Before assigning work, directly inspect the current controlling instructions and the artifacts, dependencies, blockers, and workspace state relevant to the request. Handoffs and summaries may locate sources but do not replace required direct reading.

Inventory pre-existing and concurrent work before editing. Preserve changes outside the assignment and record any overlap that affects isolation or ownership. When version control is available, confirm the active branch or worktree and its current state before relying on it.

Where repository instructions designate a checkout for the integration branch, record that branch-to-worktree mapping when assigning isolated work. Put new feature work in branch-specific worktrees when possible. If active feature work already occupies the designated checkout, preserve it and defer integration until that checkout is available. Do not switch a feature worktree to the integration branch just to merge.

Use isolation in proportion to risk. Separate contexts or workspaces when independent reasoning must be demonstrated, concurrent edits may collide, or one role must not inherit another's conclusions. Parallelize only work with independent inputs and non-overlapping outputs; serialize shared files, contracts, interfaces, migrations, or unresolved dependencies.

Treat prerequisite failures as hard stops on their first occurrence. Do not cross a gate when a mandatory source is inaccessible, required independence is unavailable, safe workspace preservation cannot be established, controlling approval is absent or stale, or required evidence cannot be established safely.

## Assign roles and ownership

Define each role's deliverable, authority, allowed scope, required inputs, and continuation condition before dispatch. Give every artifact and decision one clear owner.

### Role menu

A role defines responsibility and authority; skills supply methods. Use this menu as a starting point, refined by project instructions and the actual assignment. Select only roles the work needs. Each role can use several skills, and a skill can support several roles. The menu lists direct role assignments. Keep guidance for invoking other skills in the skill that requires it.

| Role | Skills |
|---|---|
| Solution designer | `solution-design` |
| Contract author | `contract-author` |
| Contract reviewer | `contract-reviewer` |
| Implementer | Available implementation skills suited to the task. |
| Final reviewer | Available completed-work review skills suited to the deliverable. |

Across roles, add domain, technology, research, artifact, or workspace skills only when their stated purposes apply. Skills may come from any available installed source. Keep their detailed procedures in the skills themselves. `contract-reviewer` covers pre-implementation readiness; use appropriate completed-work review guidance for final review. A role does not require a same-named skill, and experimental or unshipped skills are not defaults.

### Select skills and dispatch

Resolve matching skills from the available catalog or explicitly configured locations. Check their descriptions and boundaries, reading selected guidance as needed to settle fit. Treat menu entries as selection guidance, not proof of availability. Do not guess paths or assume a skill is available to a child because the parent used it.

Use the task-contract guide below to carry the selected skills and their reading instructions into the subagent's starting prompt. Do not assume the parent's loaded instructions transfer. Reassess selection when the assignment or evidence changes, preserving fresh contexts where independent judgment is required.

If an optional skill is unavailable, state the gap and assign the responsibility explicitly. Block only affected work when a skill is required by the user or controlling instructions. Skill selection does not expand the role's authority: resolve conflicting guidance through those instructions and route incompatible responsibilities to their owners. Preserve required separation between design, authorship, implementation, review, and approval.

For implementation assignments, include a return path for design consultation when a chosen approach proves infeasible, a key assumption fails, a local adaptation grows into substantial custom infrastructure, or a newly discovered tool could substantially simplify the feature or application through a different architecture. Route material opportunities promptly even when implementation is progressing successfully. Carry the current requirements and evidence into the reassessment; past effort alone does not settle whether to continue. Preserve required review and acceptance for semantic changes while allowing authorized local repairs and unaffected work to continue.

Keep coordination distinct from delegated specialist roles. Where separation is relied upon, remain outside every specialist role whose independence matters. Do not treat a renamed, resumed, or reasoning-inheriting context as an independent reviewer. Perform administrative tracking or mechanical transitions only when explicitly authorized, and do not introduce governed semantic judgment while doing so.

The coordinator owns workflow selection, assignment, routing, scope protection, blocker handling, and evidence collection. Authors own their specifications or plans, implementers own changes within the authorized boundary, and reviewers own their independent findings. Product choices, protected scope changes, and external actions remain with the authority designated by the user or project.

## Preserve scope

Carry the user's objective, constraints, exclusions, and authorization boundaries through every assignment. State allowed artifacts or areas when ambiguity could cause drift. Do not let remediation weaken acceptance criteria, silently expand the task, overwrite user-owned work, or convert coordination authority into permission for unrelated changes.

If work reveals a materially different requirement, pause that path and route the decision to the appropriate owner. Keep unaffected work moving only when doing so remains safe and independent.

## Make evidence-aware handoffs

A handoff should let the recipient independently establish the current state. Use a structured task contract for starting prompts and substantive reassignments. Keep it proportional: combine or omit inapplicable fields, use a short task name when no ID exists, and follow a project's required format. This guide does not require a separate document or delegation for work that can stay in the current context.

A task contract carries the authorized assignment into a handoff. Ground it in controlling instructions and any accepted specification; preserve the governing workflow's requirements for specification, review, and approval.

```text
TASK
Existing ID or short task name.

OWNER / ROLE
Assigned role, responsible worker, and the result it owns.

OBJECTIVE
Concrete outcome and why it is needed.

SKILLS
Each selected skill's name, resolved location, and purpose; conditional triggers
and availability gaps. Read and apply selected skills before the relevant work.

CONTEXT / INPUTS
Controlling instructions and authoritative artifacts to read directly, with
locations and versions when relevant. Include current evidence and open assumptions.

SCOPE / AUTHORITY
Allowed artifacts, actions, and decisions; workspace and branch when relevant.

DO NOT TOUCH
Excluded areas, concurrent work to preserve, and decisions owned by others.

DEPENDENCIES
Required inputs or prior work, their owners and current status, and any gate
that must be satisfied before dependent work begins.

EXPECTED OUTPUT
Deliverable, changed files when applicable, observed checks and evidence locations,
remaining assumptions, open risks, and unresolved findings.

DONE WHEN
Observable criteria for this assignment and the required supporting evidence.
Distinguish returning work for review from authority to accept or release it.

RETURN TO COORDINATOR WHEN
Specific blockers, failed assumptions, scope conflicts, or design questions
that exceed this worker's authority; identify any unaffected work that can continue.
```

Make scope limits and completion criteria concrete enough for the worker to act and the next role to verify. Carry existing criteria forward without weakening or inventing requirements. Mark missing authoritative inputs as gaps and preserve their gates.

Distinguish observed evidence from inference and from unverified claims. Preserve adverse findings and their dispositions so later roles can assess the full history.

When one role's artifact controls downstream work, do not begin that work until the designated authority accepts the exact current artifact. A substantive change invalidates that acceptance and closes the downstream gate until the changed artifact is accepted. Independent acceptance applies only to the exact artifact or state reviewed. Material post-review changes require independent review again.

## Handle blockers and remediation

Classify a blocker before routing it: scope or authority, specification, implementation, verification evidence, dependency, or workspace safety. Send it to the role that owns the underlying decision or artifact, and keep workflow state truthful while it is unresolved.

Make remediation focused on the demonstrated root cause and require proportionate re-verification of affected behavior. Bound retry loops according to risk. When the same root cause recurs, evidence remains insufficient, independence cannot be established, or safe preservation is no longer possible, stop retrying and escalate with the evidence gathered and the decision needed.

## Complete coordination

Do not infer approval or treat implementation alone as completion. Where independent review is part of the workflow, provide the reviewer the complete current artifact, criteria, prior findings and dispositions, and relevant verification evidence.

When an authorized transition is defined as atomic, apply all of it or none of it; never partially apply it. After application, verify that the resulting state matches the authorization.

Declare completion, merge, publish, deploy, or perform another consequential transition only when the applicable authority and evidence support that exact action. Report the outcome, remaining risks or blockers, preservation result, and who owns any next step.

Before closing work that used linked worktrees, recheck any designated integration checkout. If the mapping has drifted, restore it only after checking affected worktrees for changes and tasks that still rely on their current branches. Otherwise leave the work intact and report the exact branch and path that need reconciliation.
