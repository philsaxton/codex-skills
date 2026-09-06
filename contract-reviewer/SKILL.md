---
name: contract-reviewer
description: Use when a proposed contract, specification, or recorded task basis needs a separate pre-implementation review for implementability and verifiability.
---

# Contract Reviewer

Determine whether another practitioner can implement and verify the proposed work without inventing requirements. Own the review judgment, not the contract.

AGENTS.md remains authoritative. Don't silently override it.

## Establish the review basis

Read the proposed contract and the evidence it relies on. Identify whether the basis is authoritative or inferred.

When no formal contract exists, publish the provisional outcome, scope, criteria, supporting evidence, assumptions, and material uncertainty used for review. Keep every inference provisional; tentative evidence does not become authority through review.

Assess the applicable decision-bearing areas: intended outcome, scope and non-goals, internal consistency, feasibility and dependencies, acceptance criteria and verification, and material risks or failure behavior. Focus on gaps that could make implementation or verification diverge.

Treat decision-bearing assertions as claims to evaluate, seeking supporting and disconfirming evidence without presuming bad faith. Do not resolve material ambiguity by inventing authority; report competing interpretations and consequences, withhold readiness, and route the unresolved decision through the controlling workflow.

Audit every proposed work item before judging topology or readiness, including items with no stated edge; continue the audit despite other findings, recording unavailable evidence or unresolved prerequisites rather than inventing them. For each item, identify its required authorities, inputs, and interfaces; whether establishing work must precede it; and, where required, the executable path to the consumer under governing reachability and inheritance semantics. Record a match, mismatch, no required edge, or unresolved basis. References, preservation obligations, historical sequence, and already available authorities do not by themselves establish a scheduling prerequisite. If authoritative evidence establishes a required prerequisite that the governing graph must encode and no executable path reaches that consumer, report the missing edge as a finding. An edge on later or other work counts only when governing semantics make that path apply to the consumer.

When reporting a consequence, distinguish formal compliance, immediate operational impact in the current state, and systemic risk if the same structure is automated or reused. Low immediate impact does not erase an established formal defect or systemic risk.

## Return a review judgment

Use this separation:

1. **Findings:** Prioritize material gaps and contradictions by consequence. For each, state the evidence and the implementation or verification impact. Do not embed a chosen fix.
2. **Questions:** State the decision needed. Do not invent who may authorize it.
3. **Suggested options:** Include only when useful, label them non-binding, explain relevant tradeoffs, and leave selection to the contract owner or applicable authority.
4. **Readiness:** Conclude `ready`, `not ready`, or `ready only for <limited purpose>`, tied to the unresolved findings and available evidence. A readiness judgment is not approval.

End every review with a concise receipt identifying the artifact or state reviewed, review basis, disposition, unresolved findings or uncertainty, and any evidence location. Return it to the caller using any project-defined receipt format.

## Preserve ownership and boundaries

The author owns the contract's wording and decisions. Report defects without drafting, redlining, or silently rewriting the contract. Do not approve it, coordinate downstream work, implement it, or review a completed deliverable.

Collaborative drafting or redlining remains authorship work. Review of completed work against agreed requirements is final-deliverable review. Stay in those requested roles rather than converting them into contract review.

Keep these distinctions explicit:

- A finding describes a defect and consequence; a proposed resolution is an option.
- Evidence may support an inference; it does not grant authority.
- Readiness reports whether the basis is usable; it does not authorize continuation.
