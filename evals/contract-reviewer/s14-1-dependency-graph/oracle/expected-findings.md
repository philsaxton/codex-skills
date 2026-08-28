# Oracle — reveal only after review

## Required target finding

The counterfactual contract relies on S1.1 and S1.2 as controlling approved foundations, but its backlog table does not assign the correction slice S14.1 an explicit dependency on S1.2. Under the historical backlog semantics, a slice's own `Dependencies` field is the executable scheduling source; epic relationships and prose are not inherited.

Giving the later hypothetical S2.3 slice a direct S1.2 dependency does not encode S14.1's prerequisite. Requiring a future parser to find no hidden gate also does not supply the missing edge. The reviewer must reconstruct prerequisites from the contract's consumed authorities and compare them with the proposed executable edges rather than trust the table's assurances.

## Expected consequence classification

- **Formal contract compliance:** blocking. The contract promises an exact executable graph with no hidden prerequisites, and that deliverable is incorrect.
- **Immediate operational consequence:** low in the historical state because S1.1 and S1.2 were already complete; the omitted edge would not have unlocked premature work then.
- **Systemic automation risk:** potentially high. Repeating the pattern with an incomplete prerequisite can cause automated selection to start work too early.

## Baseline outcomes

- Historical FR-07 v1.0.0: the project reviewer detected the defect and returned changes required. Version 1.1.0 repaired the graph and was approved.
- First counterfactual review: missed the target and approved with three advisories.
- Portable-skill counterfactual rerun: missed the target while reporting other blockers.

The evaluation is intended to motivate a narrow reviewer-skill improvement: independently derive and validate executable dependency edges and report severity dimensions separately. It does not establish that every referenced artifact is a scheduling prerequisite.
