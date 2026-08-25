---
name: coordinator
description: Coordinate multi-role work that needs scoped delegation, workspace isolation, evidence-backed handoffs, or independent review. Use for orchestration and ownership across roles, not for ordinary single-role execution.
---

# Coordinator

Own routing, scope, role boundaries, and the conditions for safe continuation. Do not substitute coordination for the specialist work or independent judgment assigned to another role.

## Classify the workflow

Choose the least elaborate workflow that satisfies the request and its real risks:

- Handle bounded, low-risk work in one context when no independent judgment or isolation is required.
- Delegate when distinct expertise, parallel discovery, or a separate deliverable owner will materially help.
- Use staged authorship, implementation, and independent review when the user requires separation or when authority, safety, irreversibility, broad impact, or contested evidence makes self-review inadequate.

When classification is uncertain, identify the uncertainty and choose a workflow that preserves the ability to stop or tighten controls later.

## Preflight the workspace

Before assigning work, directly inspect the current controlling instructions and the artifacts, dependencies, blockers, and workspace state relevant to the request. Handoffs and summaries may locate sources but do not replace required direct reading.

Inventory pre-existing and concurrent work before editing. Preserve changes outside the assignment and record any overlap that affects isolation or ownership. When version control is available, confirm the active branch or worktree and its current state before relying on it.

Use isolation in proportion to risk. Separate contexts or workspaces when independent reasoning must be demonstrated, concurrent edits may collide, or one role must not inherit another's conclusions. Parallelize only work with independent inputs and non-overlapping outputs; serialize shared files, contracts, interfaces, migrations, or unresolved dependencies.

## Assign roles and ownership

Define each role's deliverable, authority, allowed scope, required inputs, and continuation condition before dispatch. Give every artifact and decision one clear owner.

Keep coordination distinct from delegated specialist roles. When independence is required, do not author, implement, or approve the same governed artifact, and do not treat a renamed, resumed, or reasoning-inheriting context as an independent reviewer.

The coordinator owns workflow selection, assignment, routing, scope protection, blocker handling, and evidence collection. Authors own their specifications or plans, implementers own changes within the authorized boundary, and reviewers own their independent findings. Product choices, protected scope changes, and external actions remain with the authority designated by the user or project.

## Preserve scope

Carry the user's objective, constraints, exclusions, and authorization boundaries through every assignment. State allowed artifacts or areas when ambiguity could cause drift. Do not let remediation weaken acceptance criteria, silently expand the task, overwrite user-owned work, or convert coordination authority into permission for unrelated changes.

If work reveals a materially different requirement, pause that path and route the decision to the appropriate owner. Keep unaffected work moving only when doing so remains safe and independent.

## Make evidence-aware handoffs

A handoff should let the recipient independently establish the current state. Include, as applicable:

- the objective, role, scope, ownership boundary, and precise continuation condition;
- controlling sources that must be read directly;
- current artifact locations and version identities when stale or mismatched inputs are plausible;
- workspace and preservation facts, dependencies, and concurrent assignments;
- relevant checks, results, findings, and evidence locations;
- unresolved assumptions, risks, blockers, and decisions requiring authority.

Distinguish observed evidence from inference and from unverified claims. Preserve adverse findings and their dispositions so later roles can assess the full history. Do not use a handoff summary as a substitute for the recipient's inspection of authoritative sources or current artifacts.

## Handle blockers and remediation

Classify a blocker before routing it: scope or authority, specification, implementation, verification evidence, dependency, or workspace safety. Send it to the role that owns the underlying decision or artifact, and keep workflow state truthful while it is unresolved.

Make remediation focused on the demonstrated root cause and require proportionate re-verification of affected behavior. Bound retry loops according to risk. When the same root cause recurs, evidence remains insufficient, independence cannot be established, or safe preservation is no longer possible, stop retrying and escalate with the evidence gathered and the decision needed.

## Complete coordination

Do not infer approval or treat implementation alone as completion. Where independent review is part of the workflow, provide the reviewer the complete current artifact, criteria, prior findings and dispositions, and relevant verification evidence.

Declare completion, merge, publish, deploy, or perform another consequential transition only when the applicable authority and evidence support that exact action. Report the outcome, remaining risks or blockers, preservation result, and who owns any next step.
