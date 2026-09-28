---
name: solution-design
description: Use when choosing a technical approach, reviewing an existing plan's design, or reassessing architecture during implementation because of a material obstacle or a newly discovered opportunity to simplify the solution.
---

# Solution Design

Establish which approach best satisfies the authorized outcome and why. Own the design recommendation and its evidence.

Respect the user's decision-making authority. Distinguish mandatory constraints from revisable design choices, surface evidence-backed alternatives, and follow the governing workflow before changing an approved choice. Preserve any required separation between authorship, review, implementation, and approval.

## Enter at the decision

Use the mode that fits the request:

- **Planning:** Resolve consequential solution choices before a plan or contract commits to a mechanism. Feed the recommendation into the requested planning artifact; do not require a separate document for a small decision.
- **Existing-plan review:** Read the complete current plan and its supporting sources. Examine the selected approach and its assumptions as well as whether the steps are feasible. Return findings and suggested options without rewriting the plan unless revision is requested. A favorable design assessment does not substitute for contract review or authorize implementation.
- **Implementation consultation:** Inspect the relevant contract, implementation, and evidence of a problem or opportunity. Reconsider the affected decision when a prerequisite proves false, an adaptation grows into substantial custom machinery, or a newly discovered tool could substantially reduce development or maintenance effort through a different architecture. A working implementation does not rule out reassessment. Determine whether the evidence supports a local repair, continuing the current approach, or a design change. Preserve unaffected work and return a concrete continuation path.

The decision's consequences determine the need for design work, regardless of whether it appears in a formal plan, a focused fix, or an implementation task. Routine implementation details do not require a new design exercise. Reuse supported prior decisions unless new evidence materially changes their basis or tradeoffs.

## Establish the actual problem

Read the controlling requirements and existing project decisions directly. Separate the required outcome and mandatory constraints from inherited solution choices, preferences, and untested assumptions. Identify the source of constraints that materially exclude alternatives. Propose changes to protected constraints explicitly; never relax them to make a preferred option fit.

Treat a proposed mechanism in a task or plan as a candidate unless the user or controlling authority has actually selected it. An explicit selection remains binding until changed through the controlling authority. Surface material conflicts or substantial opportunities to revise that selection with supporting evidence; do not silently replace selected technology or reopen settled product scope.

## Compare credible approaches

Inspect existing project capabilities and relevant maintained tools before committing to custom machinery. Consult current authoritative documentation for the installed or explicitly targeted version; search for suitable tools when the credible options are not already established. A familiar tool name or a search result alone does not establish suitability.

Consider direct use, a supported extension or narrow adaptation, and custom implementation where each is credible. Compare the requirements and costs that could change the choice: behavioral fit, integration, security and licensing, operational failure and recovery, maintenance, and effort. Avoid exhaustive catalogs and artificial scoring when a short comparison settles the decision.

When a promising tool requires a different architecture, evaluate that architecture against the required outcomes and protected constraints. Do not reject the tool solely because it does not fit the current design. Compare continuing, adapting, and redesigning from the present decision point: remaining development, reusable assets, migration and revalidation, disruption, future operation, and maintenance. Past effort alone is not a reason to retain an inferior approach. If evidence supports a materially better solution after accounting for real switching costs and uncertainty, recommend it even when substantial prior work would be replaced. Surface the opportunity early enough to avoid further work that the proposed change would invalidate.

Keep documented support, observed behavior, inference, and unresolved compatibility distinct. An untested concern is not evidence that a tool is unsuitable; lack of a recorded comparison is not proof that nobody considered it. Explain decisive exclusions and recognize when custom code is the smaller or better-supported solution.

## Resolve decisive uncertainty

When documentation cannot settle a choice, identify the smallest safe feasibility check that could change the recommendation. State what it will establish, its scope, and its stopping condition. Run it when authorized and practical; otherwise specify the check and the decision that remains conditional. Use representative inputs and an isolated environment where needed. Do not turn a design experiment into production implementation or infer permission to install, purchase, deploy, or mutate external systems.

A partial experiment supports only the behavior it exercises. Report unavailable or inconclusive evidence honestly rather than declaring compatibility or rejecting an option without support. Keep research and experiments proportional to the consequence and uncertainty of the decision.

## Return a usable decision

Provide the outcome, controlling constraints, credible alternatives, decisive evidence, recommendation or review findings, and remaining uncertainty. Explain the tradeoff that determines the recommendation and what evidence would justify revisiting it. Use the existing plan or decision record when appropriate; a few paragraphs may suffice, and no fixed template or additional approval ceremony is required.

For review, distinguish a supported choice, a material design gap, and an optional improvement. Keep recommendations separate from authority to change the plan.

For implementation consultation, state whether work can continue within the current contract, which assumption needs a bounded check, or what design and contract changes need routing to their owners. Identify affected interfaces and work to retain or replace. An authorized local repair can proceed; a recommendation that changes approved semantics must receive the review or acceptance required by the controlling workflow before dependent implementation resumes. Keep unaffected work moving when safe.
