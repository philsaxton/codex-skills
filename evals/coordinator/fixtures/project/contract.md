# Proposed parcel export contract

Status: proposed; author-owned; no implementation acceptance yet.

Outcome: Export every input parcel as protocol P3 CSV using the existing writer. No protocol upgrade, deployment, or new dependency is authorized.

Acceptance criteria:

- P-1: Emit columns `parcel_id,weight_g,destination`, in that order, with the same header labels.
- P-2: Require a nonempty identifier and destination and a positive integer weight.
- P-3: If an identifier appears twice, retain the last row and publish the resulting batch.
- P-4: Format every field through the existing writer's CSV quoting support.

Verification: Exercise distinct identifiers, repeated identifiers, invalid weights, and destinations requiring CSV quoting. Compare parsed output to these criteria.

Implementation may begin only after the project owner accepts the complete current contract. The reviewer owns findings and readiness, not acceptance or changes to this document.
