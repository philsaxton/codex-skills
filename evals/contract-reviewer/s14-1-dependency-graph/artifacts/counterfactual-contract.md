# EXPERIMENTAL — NON-AUTHORITATIVE RETROSPECTIVE BENCHMARK

# Counterfactual S14.1 / FR-07 Contract — Profile-Lifecycle Integrity Boundary Correction

## Benchmark control

- **Benchmark subject label:** S14.1 / FR-07. This is an experimental locator only, not a claim that these bytes, headings, paths, decisions, or identifiers were historically canonical.
- **Artifact class:** Focused governed documentation-only architecture correction.
- **Version:** Experimental 1.0.
- **Authority:** None. This benchmark is not a project contract, approval, implementation instruction, completion record, or historical artifact.
- **Executable behavior:** None. `pytest` is not applicable because the authorized correction changes architecture and backlog documentation only.
- **Semantic source boundary:** Project baseline commit `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`; preserved adverse S2.1 checkpoint commit `d91e68065aa99c7368eab21c8a93eeac6d7d3893`.
- **Blindness boundary:** No original FR-07 artifact, later S14.1 card, later architecture/completion record, or commit at or after `e707602f75391eeed5605c0fd25de39bac9400c4` was used.

Shared role separation, review, evidence, completion-patch, checkpoint, preservation, and authority-event mechanics remain governed by the historical `AGENTS.md`, role guides, and evidence architecture at the baseline commit. This focused contract states only the architecture delta and its necessary backlog effects.

## Authorized outcome

Correct the profile-lifecycle trust boundary after terminal S2.1 review demonstrated that ordinary same-process mutable Python module, class, object, and repository surfaces cannot provide authoritative tamper-resistant audit or lifecycle integrity.

The correction MUST:

1. preserve the terminal `Not verified` decision and every prior adverse finding;
2. preserve useful S2.1 profile-content, canonicalization, copy-on-write, lifecycle-rule, fixture, and test work as non-authoritative reference material subject to fresh contract review and re-verification;
3. place authoritative profile lifecycle state and immutable audit history behind a durable boundary outside ordinary application-process memory;
4. reconcile the E2/S2 execution graph so no runtime profile resolution, activation, rollback, outreach-profile use, or dependent feature can rely on an in-memory authority claim; and
5. change no application behavior, test, persistence implementation, endpoint, deployment, provisioning, provider selection, credential, client data, or external system.

## Scope

The hypothetical governed implementation of this correction is limited to:

- one human-readable architecture-decision record under `docs/architecture/`, with a slice-scoped name assigned only by an authoritative workflow;
- semantic backlog corrections in `IMPLEMENTATION.md` described below;
- the slice-scoped Markdown verification, handoff, review, and completion records required by the historical evidence architecture; and
- mechanical completion fields only after independent verification of the exact completion payload.

The architecture-record path is intentionally not asserted here: this benchmark is forbidden from claiming canonical historical placement. Path selection is mechanical and does not change the required semantics or acceptance predicates.

## Non-goals and forbidden effects

This correction MUST NOT:

- edit, replace, relabel, merge, or complete any S2.1 artifact from checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`;
- claim that the S2.1 checkpoint, its tests, or any green subset of its tests satisfies authoritative lifecycle or audit integrity;
- implement or modify Python source, tests, fixtures, schemas, migrations, databases, queues, caches, object storage, services, APIs, MCP/REST endpoints, authentication, deployment, monitoring, backup, or recovery;
- choose Supabase, PostgreSQL, an ORM, a transaction library, a service topology, an audit product, or any other persistence technology;
- change the S1.1 `Profile`, `ProfileVersion`, or `AuditEvent` wire schemas, or reopen the approved S1.1/S1.2 contracts;
- weaken S1.1 lifecycle, authorization, tenant, rollback, append-only, atomicity, minimization, no-approval, or no-send invariants;
- treat private naming, slots, immutable tuples, hashes, expected-history mirrors, verifier classes, defensive copies, or reconstructed values held in the same mutable interpreter as an authority boundary;
- authorize real profile activation, rollback, archival, runtime resolution, client research, persistence, approval, outreach, send, provisioning, merge, push, deployment, or external action; or
- erase, summarize away, or supersede the terminal architecture finding or earlier review history.

## Architecture and trust decisions

### AD-01 — Ordinary Python memory is not authoritative

The Python application process is a computation zone, not the integrity root for authoritative profile lifecycle or audit history. It may validate content, canonicalize bytes, evaluate deterministic eligibility, construct proposed events, and provide in-memory test doubles. It MUST NOT be the sole source that proves prior lifecycle state or prior audit bytes are immutable.

An integrity design fails this decision if changing ordinary module, class, object, repository, verifier, expected-history, or commitment state in the same interpreter can make changed stored history acceptable.

### AD-02 — Durable external authority boundary

The authoritative profile-lifecycle implementation belongs in a future executable slice and MUST use a durable transaction boundary outside ordinary application-process memory. The boundary may be a persistence layer or separately protected service, but the later contract must prove all of the following without depending on a second mutable in-process oracle:

- existing authoritative audit occurrences cannot be updated or deleted through the application's supported runtime authority;
- profile/version lifecycle state, content/evidence bindings, idempotency outcome, and required audit occurrence(s) commit or roll back as one atomic operation;
- the authoritative store, not an in-memory mirror, determines current state, global audit order, occurrence identity, and immediate predecessor topology;
- every allowed, denied, failed, and conflicted occurrence required by S1.1/S1.2 is reconstructible from authoritative command, actor, tenant, state, evidence, result, and audit records;
- verification detects omission, insertion, deletion, reorder, duplicate occurrence identity, changed immutable fields, wrong immediate predecessor, result/evidence mismatch, or lifecycle state without its required event;
- the application identity used for normal lifecycle work has no supported update/delete authority over committed history;
- unavailable or contradictory authority fails closed with no lifecycle mutation, idempotency commit, fabricated event, or fallback to memory; and
- recovery preserves or restores lifecycle/audit consistency before the capability becomes available again.

This decision establishes the minimum trust properties, not a vendor, schema, migration, or deployment design.

### AD-03 — Exact threat boundary

The required boundary resists ordinary application-process mutation, application bugs, and supported runtime interfaces that attempt to rewrite established lifecycle/audit authority. It does not claim resistance to a compromised database administrator, compromised infrastructure root, hostile interpreter/runtime, raw memory attack, or malicious storage operator. Those privileged, operational, alerting, retention, backup, and recovery risks remain governed by later S7.2 and pilot-security work.

### AD-04 — S1.1 and S1.2 remain controlling interfaces

The later implementation MUST preserve:

- the S1.1 profile/version states, copy-on-write immutability, at-most-one-active tuple invariant, explicit authorized rollback, first-transition timestamps, stable IDs, and closed `AuditEvent` shape;
- server-derived actor, tenant, membership, capability, object, field, state, version, evidence, and idempotency authority;
- S1.2's distinction between restricted canonical audit records and minimized operational logs, caller results, exports, and repository evidence;
- S1.2 TM-015/TC-12 fail-closed audit-integrity objective; and
- later-gate denial until the owning executable slice supplies current favorable runtime evidence.

No hash, prior-event link, or passing test alone proves tamper resistance. Identity, topology, atomicity, access control, and independent authority must all be established at the durable boundary.

### AD-05 — Useful S2.1 work is reference material, not authority

The checkpoint's closed profile modules, machine policy, canonicalization rules, content digests, separate content-record model, copy-on-write versioning, seven command shapes, lifecycle predicates, representative synthetic profile, mutation catalog, and deterministic tests may be reused only after a fresh contract identifies which exact bytes and behaviors remain applicable.

The following claims are not reusable: that the checkpoint is complete or verified; that its in-memory repository is authoritative; that its commitment/verifier mechanism is tamper-resistant; that its completion payload is approved; or that it unlocks S2.2 or any downstream work.

## Backlog and interface reconciliation

The hypothetical backlog correction MUST make the following executable scheduling facts explicit. The identifiers below are counterfactual benchmark choices, not assertions about later historical cards.

| Backlog subject | Required corrected state |
| --- | --- |
| E14 / S14.1 benchmark correction | One P0 documentation-only epic/slice records this architecture correction. Before completion S14.1 is `In progress`; the exact independently approved completion payload may set S14.1 and E14 to `Done`. |
| S2.1 | Retitle or rewrite only as needed to own the closed profile content model, deterministic lifecycle rules, and non-authoritative domain/reference implementation. It depends on S1.1 and the completed correction, remains not `Done`, and may become `Ready` only through the exact completion projection. Its verification must reject any production or tamper-resistant authority claim. |
| S2.3 | Add one P0 executable slice that owns authoritative durable profile lifecycle and audit integrity. It depends on S1.2 and the revised S2.1. Its acceptance criteria consume AD-02 through AD-04, require failing-first and regression tests, and require a fresh approved contract before implementation. |
| S2.2 | Keep deterministic workflow resolution and brief compilation out of this correction, but add S2.3 as a direct dependency alongside S1.2 and S2.1. It remains `Planned`; no readiness promotion occurs here. |
| E2 | Preserve the product outcome while stating that local domain/reference conformance and durable authoritative lifecycle integrity are separate required slices. E2 cannot complete until S2.1, S2.2, and S2.3 are complete or validly deferred under separate authority. |
| S3.3 and S6.1 | Their existing S2.2 dependency transitively carries the authoritative lifecycle gate; no additional direct dependency is required unless later design reveals an independent prerequisite. |
| S5.1 | Replace S2.1 as the runtime-profile prerequisite with S2.3, retaining S4.2. This prevents the sole S5.2 architecture gate from being completed on a non-authoritative outreach-profile lifecycle. |
| S5.2 and later pilot work | Remain locked by their existing direct dependencies and the corrected S5.1/S7 gates. No status promotion occurs. |

The backlog MUST contain no duplicate item ID, dangling dependency, self-dependency, dependency cycle, hidden prose-only gate, or contradiction between a slice's direct dependencies and status.

## Future S2.3 interface obligations

The future executable slice contract MUST decide implementation details while preserving these fixed interface invariants:

1. **Command boundary:** normal application code submits a closed lifecycle command with trusted server-derived authority; it does not submit authoritative prior history, actor, tenant, lifecycle result, or audit outcome.
2. **Transaction result:** the authority returns one canonical allowed or safe non-allowed result bound to the committed idempotency outcome and applicable audit reference; partial effects are impossible.
3. **Authoritative read:** current profile/version state and audit history are read from the durable authority at the decision point. Cached or in-memory projections are non-authoritative and must be invalidated or rejected when freshness cannot be established.
4. **History immutability:** committed event identity, actor/tenant/scope/time, operation/outcome, object/evidence/result bindings, and predecessor relation are immutable to the normal application role.
5. **Global ordering:** tenant filtering cannot redefine or invalidate the authoritative global predecessor chain; tenant-scoped views remain derived minimum-disclosure views.
6. **Failure behavior:** store unavailability, constraint failure, audit append failure, mismatched history, or incomplete reconstruction returns a safe failure and commits nothing.
7. **Security separation:** restricted audit identity remains accessible only through authorized audit/security operations; operational logs and caller responses remain minimized.
8. **Recovery:** restored state cannot resume mutation service until lifecycle and audit consistency have been verified from authoritative records.

## Acceptance criteria

- **AC-CF-01 — Source and blindness fidelity:** The artifact identifies both permitted commit boundaries and the direct-source inventory, uses no excluded hindsight source, and makes no canonical or historical-identity claim.
- **AC-CF-02 — Architecture correction:** The architecture record states AD-01 through AD-05 and unambiguously places authoritative lifecycle/audit integrity outside ordinary Python process memory.
- **AC-CF-03 — Durable authority predicates:** The record makes every AD-02 authority, transaction, immutability, ordering, verification, access-control, failure, and recovery predicate independently decidable without selecting a vendor.
- **AC-CF-04 — Preserved security/product invariants:** S1.1/S1.2 profile, authorization, audit, minimization, risk-gate, no-approval, no-send, and fail-closed boundaries remain unchanged; the MVP proposal requires no amendment.
- **AC-CF-05 — Adverse-history preservation:** The terminal `Not verified` decision, same-root architecture finding, unapproved S2.1 payload, checkpoint identity, and earlier findings remain visible and are neither completed nor weakened.
- **AC-CF-06 — Useful-work preservation:** The correction distinguishes reusable S2.1 reference material from non-reusable authority/completion claims and requires fresh contract review before reuse.
- **AC-CF-07 — Executable backlog topology:** E14/S14.1, S2.1, new S2.3, S2.2, E2, and S5.1 express the scheduling rules above; every dependency resolves, no cycle exists, and no downstream item is promoted.
- **AC-CF-08 — Documentation-only boundary:** The implementation changes only the allowed Markdown architecture/backlog/evidence records and performs no source, test, fixture, schema, persistence, endpoint, deployment, provider, credential, client, or external action.
- **AC-CF-09 — Objective evidence:** Verification proves content, topology, preservation, encoding, scope, and nonapplication with exact commands, results, hashes, and criterion mappings; `pytest` is recorded as not applicable for this correction rather than fabricated.
- **AC-CF-10 — Completion authority:** The proposed completion payload changes only the correction's permitted completion fields and conditional S2.1 readiness, preserves every other protected field, and remains unapplied until exact independent `Verified` approval.

## Documentation-only verification

The hypothetical documentation implementer MUST record the exact baseline and run objective checks that establish:

1. the only semantic inputs were direct `git show` reads from the two permitted commits;
2. the architecture record and `IMPLEMENTATION.md` contain every AD and AC identifier exactly once, with no placeholder, unresolved cross-reference, invalid local link, duplicate heading, or contradictory authority statement;
3. a card-aware backlog parser finds unique IDs, controlled statuses, resolved dependencies, no self-edge, no cycle, and exact agreement with the dependency/status table above;
4. an isolated projection shows S14.1/E14 completion and conditional S2.1 readiness are atomic while S2.2, S2.3, S5.1, S5.2, S6.1, and all pilot/runtime work remain unstarted;
5. the projected E2 card cannot be `Done` unless all required slices satisfy the historical epic rule;
6. exact blob hashes for every preserved S2.1 checkpoint artifact named in the source inventory still reproduce from `d91e68065aa99c7368eab21c8a93eeac6d7d3893`;
7. the MVP proposal, S1.1 contract/review/evidence, S1.2 contract/review/evidence, and FR-05/FR-06 history are byte-preserved relative to the implementation baseline;
8. baseline-relative scope contains only the allowed Markdown paths and no application, test, fixture, JSON security model, dependency, deployment, or user-owned byte;
9. all changed text is UTF-8 without BOM, LF-only, ends in exactly one newline, contains no trailing whitespace or unsafe/sensitive content, and passes `git diff --check`; and
10. the exact completion payload is hash-bound, applies cleanly only to the reviewed input in isolation, changes only permitted fields, and remains unapplied before independent review.

`pytest: N/A — this correction changes only Markdown architecture, backlog, and governed evidence records. It neither changes nor claims executable behavior. Future S2.1 and S2.3 implementation remain governed application work and require failing-first executable tests under fresh approved contracts.`

Any failed check, changed protected blob, ambiguous dependency, or non-documentation delta keeps the correction active and blocks completion.

## Risks, assumptions, and stop conditions

### Risks

- **Authority laundering:** a green in-memory test or hash chain may be misrepresented as durable tamper resistance. Mitigation: AD-01/AD-02 and explicit non-reusable claims.
- **Boundary theater:** a separate class, process-local service object, or database adapter with update/delete rights may be called an external authority without enforcing immutability. Mitigation: independently decidable AD-02 predicates and normal-application-role denial tests in S2.3.
- **Partial transaction:** lifecycle state may commit without its audit event or vice versa. Mitigation: one durable atomic operation and fail-closed recovery.
- **Hidden scheduling bypass:** S2.2 or S5 runtime work may proceed after reference-only S2.1. Mitigation: explicit S2.3 dependencies.
- **History loss:** salvage work may rewrite adverse review history or silently merge the unverified checkpoint. Mitigation: exact checkpoint preservation and fresh-contract reuse only.
- **Over-selection:** this documentation correction may prematurely choose a vendor, schema, retention duration, or deployment. Mitigation: technology-neutral boundary and a future executable contract.

### Assumptions

- The authorized outcome permits protected backlog-semantic correction but no product-direction change.
- S1.1 and S1.2 remain approved baselines; their current in-memory artifacts are executable specifications/test doubles, not production security claims.
- A durable authority boundary is required before runtime profile lifecycle or resolution can be truthfully enabled.
- S7.2 retains privileged-operation, monitoring, retention, backup, restore, incident, and operational-audit ownership beyond the minimum S2.3 consistency/recovery gate.

### Stop conditions

Stop and return to the applicable authority if:

- a required historical object cannot be read directly from its permitted commit;
- any excluded hindsight artifact is inspected;
- product direction, S1.1/S1.2 wire semantics, or an accepted human risk decision would need to change;
- the correction cannot preserve the adverse checkpoint and unrelated/user-owned work;
- the backlog cannot express the authority prerequisite without a dangling, cyclic, or hidden gate;
- satisfying the boundary requires selecting a vendor, provisioning infrastructure, using credentials/client data, or implementing behavior in this slice;
- a same-process mutable object remains the sole source that authenticates prior history; or
- objective documentation-only verification cannot decide every acceptance criterion.

No unresolved architecture question remains inside this benchmark's authorized outcome. Persistence technology, physical schema, migration strategy, service topology, operator roles, retention periods, and deployment details are intentionally owned by future governed implementation/operations contracts rather than left as ambiguities in this correction.

## Direct-source inventory

### Drafting method only

- Pinned portable Contract Author skill at Git object `c5585958ff2f80c53b0b82c40c14433041060c42:contract-author/SKILL.md` in the experiment skill repository. It supplied drafting method, not project semantics.

### Project baseline — exact commit `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`

Direct complete Git-object reads covered:

- `AGENTS.md`; `IMPLEMENTATION.md`; `docs/hosted-business-development-assistant-mvp-proposal.md`; `docs/roles/coordinator.md`; `docs/roles/contract-author.md`; `docs/governance/evidence-records.md`.
- S1.1: `docs/contracts/S1.1-domain-mcp-rest-contracts.md`; `docs/reviews/S1.1-contract-review.md`; `docs/reviews/S1.1-final-review.md`; `docs/evidence/S1.1-verification.md`; `docs/evidence/S1.1-implementer-handoff.md`.
- S1.2: `docs/contracts/S1.2-threat-model-and-authorization-test-plan.md`; `docs/reviews/S1.2-contract-review.md`; `docs/reviews/S1.2-final-review.md`; `docs/evidence/S1.2-verification.md`; `docs/evidence/S1.2-implementer-handoff.md`; `docs/security/S1.2-threat-model.json`; `docs/security/S1.2-negative-test-plan.json`; `docs/evidence/S1.2-security-evidence-state.json`.
- FR-05: `docs/contracts/FR-05-governance-checkpoint-and-recurrence-controls.md`; `docs/reviews/FR-05-final-review.md`.
- FR-06: `docs/contracts/FR-06-atomic-fr05-completion-state-reconciliation.md`; `docs/reviews/FR-06-final-review.md`; `docs/evidence/FR-06-completion-application.md`.

### Preserved adverse checkpoint — exact commit `d91e68065aa99c7368eab21c8a93eeac6d7d3893`

Direct complete Git-object reads covered:

- `docs/contracts/S2.1-profile-modules-and-lifecycle.md`;
- `docs/reviews/S2.1-contract-review.md`;
- `docs/reviews/S2.1-final-review.md`;
- `docs/evidence/S2.1-verification.md`;
- `docs/evidence/S2.1-implementer-handoff.md`;
- `docs/evidence/S2.1-completion-patch.md`;
- `src/client_agent_contracts/profile_modules.py`;
- `tests/test_s2_1_profile_modules.py`;
- `tests/fixtures/s2_1/internal_test_pilot_research_profile.json`; and
- `tests/fixtures/s2_1/profile_content_mutations.json`.

The complete permitted tree inventories were inspected only to locate and verify these historical objects. No checkout was performed.

## Experimental handoff

This benchmark is complete only as a counterfactual drafting artifact. It MUST NOT be sent to a project implementer as authority. If an Authorized Project User later chooses to adapt any decision, an authoritative coordinator must create or select the real work item, bind it to then-current direct sources, assign fresh governed roles, choose the actual artifact paths, obtain exact-version contract approval, and preserve this benchmark as external experimental material rather than project history.

There are no unresolved questions for the benchmark. The continuation gate is explicit new project authority; absent that authority, no repository action is permitted.
