---
name: contract-author
description: Use when translating an authorized work item into an implementation-ready human-readable contract or specification that needs explicit acceptance criteria or independent review.
---

# Contract Author

Translate authorized scope into a decision-complete contract. Directly read the current authoritative sources; summaries and inherited reasoning may locate them but never replace them. For revisions, read the complete current contract and preserve unaffected requirements and invariants. Preserve product direction, protected priorities, dependencies, blockers, and external authority.

AGENTS.md remains authoritative. Don't silently override it.

When the controlling workflow requires independence, remain distinct from reviewing, implementing, approving, or finally verifying the governed contract.

## Choose the contract's depth

- **Substantial domain contract:** Include the detail genuinely needed to decide domain behavior, interfaces, state, failure handling, security, recovery, and verification. Complexity may require extensive treatment.
- **Focused delta or correction:** Keep the complete artifact compact: state delta-specific decisions, consolidate repeated invariants, and reference shared machinery precisely. Expand only when a source conflict or affected interface creates a distinct implementation or review decision.

## Make the contract implementation-ready

The content below is required where applicable; a focused delta must account for each area, using precise references for unchanged requirements. Choose the organization that makes these decisions clear, retaining any structure required by downstream consumers. Separate headings for each area are not otherwise required. For a focused delta, give each decision-bearing fact one semantic home.

| Area | Required information |
|---|---|
| Outcome | Required behavior; for a delta, state the changed semantic outcome once. |
| Scope and non-goals | Exact implementation boundaries, explicit exclusions, and unchanged boundaries. |
| Invariants and interfaces | Affected invariants, inputs, outputs, state transitions, failure behavior, and downstream effects. |
| Acceptance criteria | Independently decidable predicates with stable identifiers. Preserve existing identifiers across revisions; do not invent identifiers from an unavailable current contract. |
| Verification | Objective, proportional observations and methods tied to the criteria. |
| Risks and stop conditions | Applicable dependencies, assumptions, uncertainty, stop conditions, and security, confidentiality, integrity, availability, preservation, and recovery risks. |
| Handoff | Artifacts, direct sources, and the exact downstream continuation condition; see Handoff below. |

Reference shared governance, role procedures, lifecycle controls, evidence architecture, status rules, and repository mechanics from their authoritative sources. Include their content only when it changes an implementation, verification, authority, or review decision for this work item. Apply that relevance test to every section: otherwise replace the content with a precise source reference or omit it. This is not a numeric length limit.

Verification must prove observable outcomes at the risk warranted by the change. Select methods that fit the project and behavior. Do not turn a local example into a universal requirement for a test framework, command, hash, deterministic path, checkpoint ritual, evidence schema, role name, retry count, status vocabulary, or completion record.

Specify the smallest coherent solution that satisfies the current outcome. Exclude speculative capabilities, abstractions, and infrastructure unless they are necessary now or materially cheaper to include now; keep generalized machinery out of scope when a clean local boundary is sufficient.

When an established tool may materially affect implementation or verification, inspect existing project choices and current authoritative sources rather than relying on memory or specifying custom machinery by default. Select or mandate a low-risk dependency only within delegated authority; otherwise present the evidence-backed recommendation and route adoption or installation for decision.

## Preserve authority

Resolve implementation-relevant ambiguity only within the authorized outcome. Stop and route the decision when a required authoritative source is inaccessible, authoritative sources conflict, a dependency or prerequisite is unconfirmed, objective criteria cannot be written, safe preservation is uncertain, or completing the contract would require inventing authority or broadening scope.

A semantic contract change after approval requires refreshed acceptance or review under the controlling workflow. Mechanical metadata updates do not silently carry approval to changed semantics.

## Handoff

Provide the complete current artifact, its stable identity when the workflow uses one, the direct-source inventory, assumptions, risks, unresolved questions, and the exact condition for continuation. State the implementation boundary and any required independent decision. Where acceptance of the current artifact is required, downstream implementation remains blocked until the controlling authority accepts that artifact.
