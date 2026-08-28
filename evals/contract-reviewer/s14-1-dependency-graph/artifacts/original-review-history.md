# FR-07 Contract Review

## Review identity

- **Decision:** **Changes required / Not approved**
- **Reviewed work:** E14 / S14.1 — Reconcile the S2.1 security boundary and dependent architecture
- **Reviewer role/context:** Fresh Independent FR-07 Contract Reviewer `/root/fr07_contract_reviewer`
- **Review date/timezone:** 2026-08-22T08:49:08-0400, America/New_York (EDT)
- **Reviewed contract:** `docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md`
- **Reviewed version:** 1.0.0
- **Reviewed SHA-256:** `021da09fc937958c84db8334662a6bb869d52f643d8e5476b26dcb87c2d5780d`
- **Contract-author checkpoint:** `e707602f75391eeed5605c0fd25de39bac9400c4` on `codex/s14-1-s2-1-security-boundary-correction`
- **Author-checkpoint inventory:** exactly `A docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md` relative to author baseline `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`
- **Change classification:** Governed documentation-only contract review

This decision binds only the exact contract path, version, and SHA-256 above. The contract hash and author-checkpoint blob were reproduced before substantive review. A semantic revision requires a new contract version/hash and complete fresh re-review preserving this finding.

## Independence, checkpoint, and preservation attestation

The Coordinator assigned this context only the fresh independent FR-07 Contract Reviewer role. This reviewer did not coordinate or author FR-07, did not participate in any S2.1 role, and will not implement or final-review FR-07. This record is the reviewer's only repository write.

The author checkpoint contains only the exact contract. The branch was clean at review start. Local `main`, the complete preserved S2.1 checkpoint, all FR-05/FR-06 history, S1.1/S1.2 artifacts, application code, tests, fixtures, proposal, and all other paths remained read-only and were not included, overwritten, reverted, deleted, or relabeled. The review checkpoint commit, final review-record SHA-256, stage-relative inventory, and clean-state result are supplied in the post-commit handoff to avoid a self-referential artifact identity.

Commit is provenance only. Contract approval, implementation, independent final `Verified`, completion application, merge, push, and deployment are all `N/A — not performed`; this decision is adverse and authorizes none of them.

## Direct-source inventory

The reviewer directly inspected the complete current governing and relevant architecture/evidence set, using original repository bytes rather than author or Coordinator summaries:

- `AGENTS.md` SHA-256 `bf79ef84a2b2ef71edfa04f09809d7a8d423dd8591145a233867ce88ff8d0e15`;
- `IMPLEMENTATION.md` SHA-256 `eefc35baa0e38e94560f45a5acb8e39043b685d69458a3d8370e60b7a8747075`;
- MVP proposal SHA-256 `570fd67e1854f0628eadb6a33ff9fbd1b984dec9b3fd1e74599856b9b0f859c3`;
- Contract-Reviewer Guide SHA-256 `f499d47d27bd3707c8d961ffe16f0e6e92fd51c42ecc809b739a7120180ce85e` and Evidence-Record Architecture SHA-256 `a37ac5915be99a69776b8c6d4fce6591446b35862dd99b83f12151d2b25390dc`;
- exact FR-07 contract and author checkpoint identified above;
- complete S1.1 contract, approval/adverse history, final-review history, verification, and handoff at SHA-256 `b6d3d72ace7d012a7c8b9b251198161fb850960be4797e9a910af25e965806c6`, `f57cca62dcb29e5f294a7a81d854da63aa539c06d67c5bb4e894712b729f6066`, `6ca2fd6f1cefa8b72b35063d8292b20ff79ca298599caa647d7c3cba950f840c`, `55fd5fb63ff41499355cc601f3a127a300b1200d2fa8626098da2ffb6adbf8d6`, and `20cbf08ffd0e2891574ed3e4fd5754e21edac01f442566dcc4d1a3e28836d44e`;
- complete S1.2 contract, approval/adverse history, final-review history, verification, and handoff at SHA-256 `fb7fe8d05f887a44bf401790e9a87dd26fd6333506f6f61a7f6d3e05a42d532b`, `86f3234d00e89ee046664fed480c952ee96360df1c3730f55b940788d0fffe46`, `7da50d511a80c2a920b19587143548092eb681466a11b7ef8dbe074604632bac`, `a9cacc8f51d431b099fc0bd4acc54d781bfb3b584c56fca3145bb0c5e267c5ec`, and `b3f6d277bbf5dd38e522f5b6ecaf63a3a46ff616989424db472e0569471b4283`;
- complete S1.2 threat model, negative-test plan, and evidence state at SHA-256 `df582f5f80075f1d4dd9fe8b61d3270d1f4083b45792e7be2d1e23fa767e6a8d`, `7b73f61d211e09decb7cdeee9c21d1493f02aa1d97e4c9ac4310a5d5f528dbfb`, and `d6e418ed526c136e7496974dbb78b081418d307c797985cda9fe5b891089a008`;
- complete FR-05 contract/review/verification/handoff/final adverse history and FR-06 contract/review/verification/handoff/final-review/completion-application history at their current exact identities, including FR-05 F-03 `same-root recurrence — stop` and FR-06 `Final — fidelity verified`;
- complete preserved S2.1 v1.5.0 contract, five adverse contract decisions plus exact approval, full implementation/final-review history through the terminal architecture decision, verification, handoff, rejected completion payload, source, focused test, and fixtures at checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`; and
- the complete 13-path checkpoint manifest and SHA-256 identities reproduced exactly as recorded by FR-06 and FR-07.

The terminal S2.1 evidence remains `Not verified`: ordinary same-process module/class/object behavior can change both stored in-memory audit history and its acceptance authority. The rejected S2.1 payload remains unapplied. No F-series continuation is permitted.

## Independent architecture and placement conclusions

### Corrected trust and responsibility boundaries

The contract correctly rejects ordinary in-process Python memory as an authoritative tamper-resistant boundary. Its protocol-neutral security kernel, profile-module ownership, defense-in-depth reconstruction non-claims, future restricted Supabase/Postgres enforcement, and MCP/REST peer-adapter model are consistent with the proposal and preserve S1.1/S1.2 authorization, tenant, audit, idempotency, atomicity, human-control, no-egress, no-silent-persistence, and no-send invariants.

The profile disposition framework is also sound: preserve useful profile/lifecycle behavior and regressions, extract reusable kernel behavior, relocate authoritative persistence controls, simplify machinery built only to simulate an impossible boundary, and retire or rewrite only tests whose asserted security claim is impossible. Historical tests/evidence remain preserved as adverse provenance.

### Proposal and owner authority

Proposal amendment is correctly `N/A`. The current proposal already selects a hosted Python service, Supabase/Postgres, server-derived tenant authority, API authorization, RLS as defense in depth, authenticated MCP plus supporting REST, immutable audit provenance, and centralized profile lifecycle. FR-07 changes layer ownership, not product direction.

No current Product/Operator Owner decision is required. The Authorized Project User authorized creation of this correction slice, and the contract introduces no new provider/model, pilot boundary, risk acceptance, live provisioning, scope expansion, or external action. Later provisioning, deployment, privileged-operation, retention/recovery, and provider/library decisions remain separately gated.

### Independent S14.3 placement decision

The earlier proposed S14.3 sequence was treated as provisional. Direct comparison supports a distinct S14.3 rather than folding authoritative persistence into an existing slice:

- S2.1 owns profile-specific content, validation, lifecycle, activation, rollback, archival, and business invariants; making it the reusable audit/idempotency/transaction authority would couple every domain to a profile slice and repeat the boundary error.
- S3.1 owns the hosted service and peer protocol adapters. Putting database authority there would mix adapter/service bootstrapping with reusable persistence enforcement and risk a second policy plane.
- S3.2 is deliberately a bounded read-side corpus adapter with no production create/import/seed or generic write authority.
- S4.1 owns the later explicit research-draft write and its feature-specific integration gate. It is too late and too domain-specific to establish the profile/service security foundation, although its existing S1.2 write-runtime obligations still consume and verify that foundation.
- S7.1 owns paid provisioning, deployment migrations, environment, TLS/DNS, and rollback. It currently depends on S3.1, so assigning the prerequisite application-persistence foundation there would be cyclic. S7.2 retains operational retention, recovery, and privileged-access evidence rather than initial application-persistence construction.

Separating S14.2 application-kernel extraction from S14.3 restricted-database enforcement is independently verifiable and keeps provider/library selection deferred. S14.2 before S14.3 is technically coherent because the latter implements the former's transaction and persistence interface. Requiring S14.3 before the rebased S2.1 and S3.1 is defensible: neither consumer may again claim authoritative lifecycle/audit integrity from its local in-memory reference or invent an adapter-specific persistence policy.

This placement conclusion does not cure the exact scheduling defect below.

## Criterion-level review

| Criterion | Result | Direct basis |
| --- | :---: | --- |
| AC-07-01 — State reconciliation | Pass | Current `main` and checkpoint `d91e680...` are accurately distinguished; terminal `Not verified`, rejected/unapplied payload, and no-F-series stop are preserved. |
| AC-07-02 — Correct trust model | Pass | Same-process memory/verifier non-authority and defense-in-depth non-claims are exact. |
| AC-07-03 — Kernel boundary | Pass | Authenticated context consumption, tenant/actor binding, authorization, audit intent/provenance, idempotency/concurrency, transaction interface, and integrity checks have one protocol-neutral owner. |
| AC-07-04 — Profile boundary | Pass | Profile-specific modules and lifecycle remain profile-owned and generic security/persistence/adapter duties are excluded. |
| AC-07-05 — Authoritative persistence | Pass | Restricted credentials, permissions/RLS, append-only enforcement, transactions, constraints, authenticated reads, and adverse integration evidence are assigned without present implementation/provisioning. |
| AC-07-06 — Peer adapters | Pass | MCP and REST adapt the same application service/kernel and may not duplicate authority or business policy. |
| AC-07-07 — S2.1 disposition | Pass | The exact five-way disposition framework covers every checkpoint path while preserving adverse provenance. |
| AC-07-08 — Exact backlog graph | **Changes required** | The new placement/order is defensible, but B-01 leaves actual E1/S1.1/S1.2 prerequisites only on E14 prose/epic state, which child slices do not inherit. |
| AC-07-09 — Proposal and authority fidelity | Pass | Proposal amendment and current owner decision are correctly `N/A`; no product/risk/live authority is inferred. |
| AC-07-10 — Documentation-only scope | Pass | The allowed implementation is Markdown-only and expressly excludes code, tests, persistence, endpoints, payload application, and external state. |
| AC-07-11 — Evidence and checkpoint integrity | Pass as specified | Baselines, hashes, full checkpoint manifest, objective checks, stage-relative checkpoints, preservation, and authority separation are required. |
| AC-07-12 — Completion projection | Pass | Only S14.1 completion and S14.2 readiness are projected; E14/S14.3 and S2.1/S2.2/S3.1 remain unearned. |

## Blocking finding

### B-01 — The slice dependency graph does not encode its actual E1/S1.1/S1.2 prerequisite

- **Affected rules and criteria:** `IMPLEMENTATION.md` executable-dependency semantics; exact backlog table and sequence; AC-07-03, AC-07-08, and AC-07-12.
- **Direct evidence:** The backlog rules state that a slice's own `Dependencies` field is the sole executable scheduling source, every prerequisite that must be complete before a slice starts must be listed there, and epic dependencies are coordination summaries that are never inherited. The proposed E14 card has `Dependencies: E1`, but S14.1 has `Dependencies: None` and S14.2 has only `Dependencies: S14.1`. The same contract says S14.2 must extract the **approved S1.1/S1.2 behavior**, preserve those exact invariants, and run S1.1/S1.2 regressions. Those completed contracts are therefore actual prerequisites, yet no child-slice dependency path reaches E1, S1.1, or S1.2.
- **Why blocking:** E14's dependency cannot gate S14.1 or S14.2 under the authoritative non-inheritance rule. The exact graph therefore contains an unencoded prerequisite while AC-07-08 requires no hidden gate. It can also make S14.2 appear executable solely from S14.1 even though the kernel specification it must preserve is not represented as a completed scheduling prerequisite. Current E1 happens to be `Done`, but current truth does not turn an epic-only coordination summary into a valid slice dependency or satisfy the rule that actual prerequisites be explicit.
- **Required disposition:** Revise the exact new-slice dependency table so the child path explicitly depends on the completed security-contract foundation without adding redundant edges. A minimal coherent repair is to give S14.1 a direct dependency on S1.2 (which transitively depends on S1.1) and keep S14.2 dependent on S14.1 and S14.3 dependent on S14.2; an equivalent exact non-circular graph is acceptable if it faithfully encodes the prerequisite. Update the prose sequence, parser expectations, completion projection preconditions, and affected AC text consistently. Preserve the independently supported distinct S14.3 placement unless the author supplies contrary direct evidence.
- **Approval effect:** Blocking.

## Advisory implementation-contract risk

The future S14.3 contract should explicitly map its foundation responsibilities to the still-current S1.2 executable obligation/gate ownership: S4.1 retains feature-specific write-runtime evidence, S7.1 retains provisioning/deployment migration evidence, and S7.2 retains operational retention/recovery/privileged-access evidence. If S14.3 changes any canonical S1.2 slice owner, evidence subject, gate, schema, test plan, or evaluator behavior, that change is governed application work and must update the exact S1.2 executable artifacts with failing-first evidence rather than relying on architecture prose. This is not a present product-owner decision and does not make distinct S14.3 placement incorrect; it is a required future contract boundary to prevent duplicated or missing gate ownership.

## Decision and re-review state

**Changes required / Not approved** for `docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md` version 1.0.0, SHA-256 `021da09fc937958c84db8334662a6bb869d52f643d8e5476b26dcb87c2d5780d`.

Implementation remains blocked. This decision authorizes no tracking-first insertion, `IMPLEMENTATION.md` edit, architecture record, code/test/database/service work, completion payload, application, merge, push, deployment, external action, or S2.1/S2.2/S3.1 continuation.

Re-review requires a semantically revised FR-07 version/hash, preserved B-01 history and disposition, a new scoped contract-author checkpoint, and complete review of the revised contract plus current authorities. The same reviewer may re-review only if it edits neither the contract nor remediation and remains independent.

## Re-review — contract version 1.1.0

### Review identity and independence

- **Decision:** **Approved**.
- **Reviewer context:** `/root/fr07_contract_reviewer`, the same independent reviewer that issued B-01. This reviewer edited neither the contract nor its remediation; the only prior authored artifact was this review record.
- **Review completed:** `2026-08-22T09:06:31-0400` (`EDT`).
- **Reviewed contract:** `docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md`, version 1.1.0, SHA-256 `a9cc6d730fcafd633bd13940b3631add72eae79aaf4c4d625d4125d0e5c60c51`.
- **Contract-author revision checkpoint:** commit `3bd6a1ef4e56cfd480688463b2f72a3c2fb91669` on `codex/s14-1-s2-1-security-boundary-correction`, containing only the revised contract relative to the prior review checkpoint.
- **Preserved prior review:** this file before re-review, SHA-256 `f8d2fd1d5b588ea2c0de94ad0527b60bb938ce3818eb4886fd1eaaf285e600d1`, checkpoint commit `0ef6a7a6d414cf1d6e43e8ea52700943a39a0351`.

The reviewer directly re-read the complete revised contract rather than relying on its diff, re-read the complete prior review and B-01, and rechecked the complete current governing and relevant source set inventoried above. Those source identities remain unchanged, including `AGENTS.md`, `IMPLEMENTATION.md`, the MVP proposal, the Contract-Reviewer Guide, the evidence architecture, the complete S1.1/S1.2 authority and evidence records, the complete S2.1 contract/adverse-review/evidence history through checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`, and the FR-05/FR-06 recurrence and checkpoint history. The terminal S2.1 `Not verified` decision, rejected completion payload, and no-F-series stop remain preserved.

### B-01 disposition and dependency-graph verification

**B-01 — Resolved.** Version 1.1.0 encodes the actual executable prerequisites on the child slices rather than relying on the non-inherited E14 epic summary:

- S14.1 has exact direct dependencies `{S1.2}`;
- S14.2 has exact direct dependencies `{S1.2, S14.1}`; and
- S14.3 has exact direct dependencies `{S1.2, S14.2}`.

S1.2 directly depends on S1.1, so all three new child slices reach the S1.1 foundation transitively. E14's E1 dependency remains an epic-level coordination summary only and is not treated as inherited authority. S14.2 explicitly consumes both the completed S1.2 security-contract foundation and the S14.1 architecture record; S14.3 explicitly consumes both S1.2's gate obligations and S14.2's reusable kernel interface. The completion projection correspondingly requires both S1.2 and S14.1 to be `Done` before S14.2 becomes `Ready`.

The graph is acyclic, contains no hidden prerequisite or executable epic inheritance, and creates no premature continuation path for S2.1, S2.2, or S3.1. Contract cross-references, parser expectations, completion rules, and dependency prose consistently use the corrected graph.

### Independent architecture and placement confirmation

The full revised contract continues to satisfy the corrected trust model, reusable security-kernel boundary, profile-module boundary, defense-in-depth non-claim, future authoritative Supabase/Postgres enforcement boundary, peer MCP/REST adapter rule, S2.1 disposition framework, preservation requirements, exact documentation-only allowed paths, objective evidence rules, and completion-authority separation described in the initial review.

The independent S14.3 conclusion also remains unchanged after re-review. A distinct persistence-enforcement slice is the smallest coherent placement because folding that authority into S2.1 would couple generic security persistence to profile lifecycle, folding it into S3.1 would mix reusable authority with adapter/service bootstrapping, S3.2 and S4.1 are read- or feature-specific, and S7.1/S7.2 own deployment and operational evidence rather than the application-persistence foundation. Ordering S14.2 before S14.3 is appropriate because database enforcement implements the kernel's transaction and persistence interface. This conclusion follows the source boundaries and dependency graph, not the earlier provisional coordinator/author suggestion.

The prior advisory implementation-contract risk is preserved and remains nonblocking: the future S14.3 contract must map foundation responsibilities to the current S1.2 executable gate ownership and use governed failing-first evidence if it changes canonical executable artifacts or ownership.

### Criterion-level re-review

| Criterion | Result | Re-review basis |
| --- | :---: | --- |
| AC-07-01 — State reconciliation | Pass | Main/checkpoint discrepancy, terminal adverse state, rejected payload, and recurrence stop remain exact. |
| AC-07-02 — Correct trust model | Pass | Ordinary same-process Python memory and its verifier are expressly non-authoritative. |
| AC-07-03 — Kernel boundary | Pass | Protocol-neutral authenticated context, tenant/actor binding, authorization, audit/provenance, idempotency, transaction interface, and integrity duties remain centralized. |
| AC-07-04 — Profile boundary | Pass | Profile lifecycle, validation, activation, rollback, and business policy remain profile-owned. |
| AC-07-05 — Authoritative persistence | Pass | Restricted credentials, permissions/RLS, transactions, constraints, append-only enforcement, and authenticated reads remain future persistence duties. |
| AC-07-06 — Peer adapters | Pass | MCP and REST remain peers into one hosted service/kernel without duplicated policy authority. |
| AC-07-07 — S2.1 disposition | Pass | Preservation, extraction, relocation, simplification, and test retirement/rewrite rules remain complete. |
| AC-07-08 — Exact backlog graph | Pass | B-01 is resolved by the exact explicit child dependencies above; reachability, acyclicity, and no-hidden-gate checks pass. |
| AC-07-09 — Proposal and authority fidelity | Pass | Proposal amendment is `N/A`; no product direction or owner authority is inferred. |
| AC-07-10 — Documentation-only scope | Pass | Code extraction, persistence, service/adapters, tests, payload application, and external actions remain excluded. |
| AC-07-11 — Evidence and checkpoint integrity | Pass | Exact identities, objective checks, scoped checkpoints, preservation, and authority distinctions are required. |
| AC-07-12 — Completion projection | Pass | Only S14.1 completion and correctly gated S14.2 readiness are projected; all downstream completion remains unearned. |

### Approval

**Approved** for the exact `docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md` version 1.1.0 bytes at SHA-256 `a9cc6d730fcafd633bd13940b3631add72eae79aaf4c4d625d4125d0e5c60c51`.

Proposal amendment: `N/A` — the correction changes architecture ownership and executable sequencing within the approved product direction. Current Product/Operator Owner decision: `N/A` — no new product scope, risk acceptance, provider selection, provisioning, deployment, or external action is requested.

This approval permits handoff only to the documentation/architecture implementer under the exact approved contract. It is not implementation, final `Verified`, completion authorization, completion-patch approval, merge, push, deployment, or permission for S2.1/S2.2/S3.1 to continue. All such events are `N/A — not performed` at this stage.

The re-review checkpoint commit and resulting review SHA-256 are supplied in the governed handoff after commit so this record does not self-reference mutable identity data.
