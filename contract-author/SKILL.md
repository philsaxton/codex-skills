---
name: contract-author
description: Use when translating an authorized work item into an implementation-ready human-readable contract or specification that needs explicit acceptance criteria or independent review.
---

# Contract Author

Translate authorized scope into a decision-complete contract. Directly read the current authoritative sources; summaries and inherited reasoning may locate them but never replace them. Preserve product direction, protected priorities, dependencies, blockers, and external authority.

AGENTS.md remains authoritative. Don't silently override it.

When the controlling workflow requires independence, remain distinct from reviewing, implementing, approving, or finally verifying the governed contract.

## Classify the contract before drafting

- **Substantial domain contract:** Include the detail genuinely needed to decide domain behavior, interfaces, state, failure handling, security, recovery, and verification. Complexity may require extensive treatment.
- **Focused delta or correction:** The complete artifact is one compact pass through seven slots: changed semantic outcome; exact scope and non-goals; affected invariants or interfaces; acceptance criteria; verification; applicable risks, assumptions, and stop conditions; handoff. Put only delta-specific facts in those slots, consolidate repeated invariants, and use one precise source-reference statement for shared machinery.

For a focused delta, give each fact one semantic home: state the change once in the outcome; unchanged boundaries in scope; downstream effects only under invariants; decidable predicates in acceptance criteria; observations in verification; delta-specific uncertainty in risks; and artifacts, sources, and the continuation gate in handoff. Expand a slot only when a source conflict or affected interface creates a distinct implementation or review decision.

Reference shared governance, role procedures, lifecycle controls, evidence architecture, status rules, and repository mechanics from their authoritative sources. Include their content only when it changes an implementation, verification, authority, or review decision for this work item.

Apply this semantic compression test to every section: if removing it would not change implementation, verification, authority, or review, replace it with a precise source reference or omit it. This is a relevance test, not a numeric length limit.

## Make the contract implementation-ready

Include the applicable decision-bearing material:

- required behavior and explicit non-goals;
- relevant interfaces, inputs, outputs, state transitions, and failure behavior;
- independently decidable acceptance criteria with stable identifiers;
- objective, proportional verification tied to the criteria;
- implementation boundaries, dependencies, assumptions, and stop conditions;
- applicable security, confidentiality, integrity, availability, preservation, and recovery risks; and
- the downstream handoff and continuation condition.

Verification must prove observable outcomes at the risk warranted by the change. Select methods that fit the project and behavior. Do not turn a local example into a universal requirement for a test framework, command, hash, deterministic path, checkpoint ritual, evidence schema, role name, retry count, status vocabulary, or completion record.

Specify the smallest coherent solution that satisfies the current outcome. Exclude speculative capabilities, abstractions, and infrastructure unless they are necessary now or materially cheaper to include now; keep generalized machinery out of scope when a clean local boundary is sufficient.

When an established tool may materially affect implementation or verification, inspect existing project choices and current authoritative sources rather than relying on memory or specifying custom machinery by default. Select or mandate a low-risk dependency only within delegated authority; otherwise present the evidence-backed recommendation and route adoption or installation for decision.

## Preserve authority

Resolve implementation-relevant ambiguity only within the authorized outcome. Stop and route the decision when a required authoritative source is inaccessible, authoritative sources conflict, a dependency or prerequisite is unconfirmed, objective criteria cannot be written, safe preservation is uncertain, or completing the contract would require inventing authority or broadening scope.

A semantic contract change after approval requires refreshed acceptance or review under the controlling workflow. Mechanical metadata updates do not silently carry approval to changed semantics.

## Handoff

Provide the complete current artifact, its stable identity when the workflow uses one, the direct-source inventory, assumptions, risks, unresolved questions, and the exact condition for continuation. State the implementation boundary and any required independent decision. Where acceptance of the current artifact is required, downstream implementation remains blocked until the controlling authority accepts that artifact.
