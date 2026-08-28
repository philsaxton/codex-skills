# FR-07 — S2.1 Security-Boundary Architecture Correction

## Contract metadata

- **Epic / slice:** E14 / S14.1 — Reconcile the S2.1 security boundary and dependent architecture
- **Contract ID:** FR-07
- **Contract version:** 1.0.0
- **Change classification:** Governed documentation-only
- **Status:** Draft — implementation is blocked until a fresh independent Contract Reviewer approves these exact bytes
- **Authoring role/context:** Fresh FR-07 Contract Author, distinct from the Coordinator, Contract Reviewer, Documentation/Architecture Implementer, Final Reviewer, and every S2.1 role
- **Branch:** `codex/s14-1-s2-1-security-boundary-correction`
- **Contract-author baseline:** commit `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`
- **Canonical artifact:** `docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md`
- **Executable behavior:** None. `pytest: N/A — FR-07/S14.1 changes only Markdown architecture, backlog, verification, handoff, and unapplied completion records; it changes no application source, test, fixture, schema, migration, service, database, runtime, or external system.`
- **Proposal amendment:** N/A. The complete current proposal already selects a hosted Python service, Supabase/Postgres, server-derived tenant selection, API authorization on every operation, RLS as defense in depth, immutable audit provenance, and authenticated MCP plus supporting REST. This correction assigns those existing obligations to defensible layers; it does not change product direction, scope, milestones, client-led research, no-send behavior, or provider/model decisions.
- **Product/Operator Owner decision:** N/A. No product choice, pilot boundary, risk acceptance, provider/model selection, live provisioning, or scope expansion is required. The Authorized Project User expressly authorized creation of the smallest governed architecture-correction slice. Ordinary exact-contract approval remains the only pre-implementation decision for S14.1.

The contract identity is its repository path, version, and exact SHA-256 reported after the scoped author checkpoint. A hash identifies bytes but does not approve them. Any semantic byte change requires a new version and fresh exact-version review.

## Authority, bootstrap, and current-state reconciliation

The current `main` backlog says S2.1 is `Ready`. That is not the actual work state. The preserved branch `codex/s2-1-profile-modules-lifecycle` at checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893` records S2.1 as `In progress`, contains the implementation and evidence, ends in terminal independent `Not verified`, leaves its completion payload unapproved and unapplied, and requires an architecture decision. FR-05/FR-06 governance correction is complete on local `main`. S2.2 remains `Planned`; S3.1 is incorrectly `Ready` despite the now-established missing architecture boundary.

The terminal S2.1 finding is classified as preserved `same-root recurrence — stop`: ordinary same-process Python module/class/object behavior can modify both live in-memory audit history and the verifier or acceptance authority used to judge that history. No F-series continuation or further attempt to make ordinary mutable Python memory authoritative and tamper-resistant is authorized. This separately authorized architecture slice is the permitted post-stop disposition; it does not relabel or erase any S2.1 finding and grants no S2.1 completion authority.

E14 and S14.1 do not yet exist in `IMPLEMENTATION.md`. The Authorized Project User's explicit request is authority to create the smallest governed correction slice, so contract drafting and exact review may bootstrap from that authorization. After approval and before any other implementation edit, the Documentation/Architecture Implementer MUST add the exact E14/S14.1–S14.3 cards specified below with S14.1 `In progress`. That tracking-first insertion is part of S14.1's approved implementation, not an informal status edit, retrospective selection, or authority for S14.2/S14.3. The evidence must bind the pre-insertion backlog and the immediate tracking-first backlog separately.

## Direct-source inventory

The author directly read the complete current governing sources and the complete relevant dependency, adverse-history, checkpoint, and architecture sources. Exact identities used at authoring are:

| Source | Exact identity / relevance |
| --- | --- |
| `AGENTS.md` | SHA-256 `bf79ef84a2b2ef71edfa04f09809d7a8d423dd8591145a233867ce88ff8d0e15`; control plane, stage gates, checkpoints, recurrence, completion authority |
| `IMPLEMENTATION.md` | SHA-256 `eefc35baa0e38e94560f45a5acb8e39043b685d69458a3d8370e60b7a8747075`; complete current operational state and discrepancy |
| `docs/hosted-business-development-assistant-mvp-proposal.md` | SHA-256 `570fd67e1854f0628eadb6a33ff9fbd1b984dec9b3fd1e74599856b9b0f859c3`; hosted-service, Supabase/Postgres, client-led, safety, and scope authority |
| `docs/roles/coordinator.md` | SHA-256 `2629807312042d7cbee4b5f37f7497fdda693457ee93a408dc4c26722b8e6aed`; selection and reconciliation boundary |
| `docs/roles/contract-author.md` | SHA-256 `f1c21f1cc41b43913124aad57ab885e07d924baadc9262a040cc55b58fee235e`; author role |
| `docs/governance/evidence-records.md` | SHA-256 `a37ac5915be99a69776b8c6d4fce6591446b35862dd99b83f12151d2b25390dc`; record, hashing, preservation, and completion lifecycle |
| S1.1 contract / contract review / final review / verification / handoff | SHA-256 `b6d3d72ace7d012a7c8b9b251198161fb850960be4797e9a910af25e965806c6` / `f57cca62dcb29e5f294a7a81d854da63aa539c06d67c5bb4e894712b729f6066` / `6ca2fd6f1cefa8b72b35063d8292b20ff79ca298599caa647d7c3cba950f840c` / `55fd5fb63ff41499355cc601f3a127a300b1200d2fa8626098da2ffb6adbf8d6` / `20cbf08ffd0e2891574ed3e4fd5754e21edac01f442566dcc4d1a3e28836d44e`; domain, server authority, audit, idempotency, lifecycle, MCP/REST invariants |
| S1.2 contract / contract review / final review / verification / handoff | SHA-256 `fb7fe8d05f887a44bf401790e9a87dd26fd6333506f6f61a7f6d3e05a42d532b` / `86f3234d00e89ee046664fed480c952ee96360df1c3730f55b940788d0fffe46` / `7da50d511a80c2a920b19587143548092eb681466a11b7ef8dbe074604632bac` / `a9cacc8f51d431b099fc0bd4acc54d781bfb3b584c56fca3145bb0c5e267c5ec` / `b3f6d277bbf5dd38e522f5b6ecaf63a3a46ff616989424db472e0569471b4283`; threat, authorization, audit-integrity, and adverse-history boundaries |
| S1.2 threat model / negative-test plan / evidence state | SHA-256 `df582f5f80075f1d4dd9fe8b61d3270d1f4083b45792e7be2d1e23fa767e6a8d` / `7b73f61d211e09decb7cdeee9c21d1493f02aa1d97e4c9ac4310a5d5f528dbfb` / `d6e418ed526c136e7496974dbb78b081418d307c797985cda9fe5b891089a008`; auth, audit, idempotency, integrity, and gate obligations |
| FR-05 contract / terminal final review | SHA-256 `fb4fba8590d0616026622e6ee84460291611a0ed7607b4eba4795569e2a002e7` / `c380522e6e3137f713b0391aeea87c576a8dc82775ed1d90ee12f4ae4c44dcfc`; checkpoint and same-root stop controls/history |
| FR-06 contract / final review / completion application | SHA-256 `22324efbf6209515c9e34de52b011e6acc8ca7528875c8f870e10d1814ada85f` / `8db375e0805dddeb92835868c62fa69219d2a173775346fab3fe55d22c94c12f` / `8f37efb51eddae481fdea870a68cb1d97c448fe5dbee3fb43ccf12d1d978a586`; atomic governance correction and completed local-main state |
| Preserved S2.1 checkpoint | Commit `d91e68065aa99c7368eab21c8a93eeac6d7d3893` on `codex/s2-1-profile-modules-lifecycle`; exact paused/unverified tree |
| Preserved S2.1 contract / contract review / final review | SHA-256 `8aaa47c668117849cffe6437d6ee54eed6b3fbd5d1e875347fedaf1e049dfe15` / `5ee0ca7f26c274ee3047a6b64af7f6ca72624eb9666d6d819c325c8d5484b433` / `b3d9b807f525ad2dd9d4c2ad52a9c21aebff6bc8944cf216bf947af706d82cfc`; complete v1.5.0 specification, five adverse contract decisions plus approval, eleven remediation findings, and terminal architecture stop |
| Preserved S2.1 verification / handoff / completion patch | SHA-256 `5197fb55d31cb24fe1bec5e96797b41a2df28738c9ceea7ee203165107007419` / `6f052efaffa6a8120e54862df0298d3ae44d194299a7f777bef86fd70de98903` / `642146312e4393a68a8d7768191ca526496311e0b6b2e1acbce4eac91ee3fea1`; complete implementation chronology and rejected, unapplied payload |
| Preserved S2.1 source / focused test / valid fixture / mutation catalog | SHA-256 `4ee94c2edb5e1d10e518dd16513be8992e02ac2f24de12c9fbe2a091ff1d8864` / `bcd38a71bf5c4c263a3667a3db41221a576b335252b31b72f82fd6b742d777d1` / `b32e4675cf5f12f4e42e29f964975c1939f61dcaa0a7055f774be1f4d3c5a4d5` / `36fc48f977a201d922f8234b2827e72c517a8514148bec39ce51d8f3c3eec2e0`; disposition inputs, not approved implementation |

The preserved S2.1 manifest comprises all 13 paths recorded by FR-06 and MUST be reproduced in full in FR-07 evidence. The contract author directly inspected the complete S2.1 contract and adverse-review history and the checkpoint tree; summaries and this inventory did not replace those reads.

## Purpose and required outcome

S14.1 must replace an indefensible in-memory authority claim with a layered architecture and an executable backlog sequence while preserving useful S2.1 work and all adverse history. The result is one architecture record and one reconciled backlog in which:

1. ordinary in-process Python memory is explicitly non-authoritative for tamper-resistant audit or lifecycle integrity;
2. reusable server security-kernel responsibilities are separated from profile-specific business behavior;
3. local reconstruction and consistency checks remain defense in depth without being represented as proof against same-process modification;
4. authoritative append-only enforcement is assigned to a future hosted-service Supabase/Postgres persistence boundary;
5. MCP and REST are peer adapters into the same hosted application service and kernel;
6. preserved S2.1 code/tests receive a reviewable keep/extract/relocate/simplify/retire-or-rewrite disposition;
7. S14.2, S14.3, S2.1, S2.2, and S3.1 have exact non-circular dependencies and truthful statuses; and
8. no S2.1 code, persistence, MCP service, completion payload, external system, or downstream slice is implemented by S14.1.

## Corrected trust model

The architecture record MUST state all of the following as normative:

- Ordinary objects, mappings, lists, class attributes, module globals, closures, methods, slots, frozen dataclasses, tuples, hashes stored beside data, and verifier code in one Python interpreter share one mutable administrative trust domain. They may support correctness and accidental-corruption detection, but none is an authoritative tamper-resistant boundary from ordinary code executing in that process.
- Python naming conventions, hidden/private members, defensive copies, `__slots__`, read-only wrappers, capability singletons, and verifier indirection do not create an independent security authority. No current or future test may describe them as proving append-only persistence or resistance to same-process modification.
- The hosted service process is trusted application code. Its local validation and reconstruction checks are still required to fail closed when they observe inconsistency, but compromise or arbitrary ordinary-code modification inside that process is outside what an in-memory reference can prevent.
- Authoritative append-only and transactional integrity must be enforced outside ordinary mutable application memory at the persistence/service boundary described below. Application checks and persistence controls are complementary; neither permits the application to trust client/model-supplied actor, tenant, role, state, evidence, or audit claims.
- The terminal S2.1 counterexample is architecture evidence. It is not an authorization to weaken authorization, audit provenance, idempotency, lifecycle atomicity, tenant isolation, or integrity requirements.

## Reusable security-kernel boundary

The architecture record MUST define a protocol-neutral kernel used by every business module and every adapter. It owns these responsibilities:

1. **Authenticated context:** accept only authentication-adapter output whose token signature, issuer, audience, expiry, and required claims have been verified; resolve the subject, tenant, active membership, roles/capabilities, and applicable scope from server-controlled records. Caller/model tenant, actor, membership, role, capability, profile, workflow, object, or approval values are never authority.
2. **Tenant and actor binding:** bind every authorized read, mutation, idempotency record, audit occurrence, and returned object reference to the server-derived tenant and actor/membership or to the existing minimized restricted non-human/pre-auth representation. Cross-tenant and unknown-object failures remain non-enumerating.
3. **Authorization primitives:** expose reusable operation-, object-, field-, state-, and capability-level authorization decisions; distinguish protocol authentication from application authorization; fail closed before protected disclosure or mutation; and retain human-only controls where S1.1/S1.2 require them.
4. **Audit construction and provenance:** construct canonical, minimized allowed/denied/failed/conflict audit intents from trusted context, operation, correlation, outcome, reason, safe object references, request/effect/evidence bindings, and predecessor/order facts. Business modules supply typed business facts, not actor/tenant authority or prebuilt authoritative audit events.
5. **Idempotency and concurrency:** define server-scoped idempotency identity at least by derived tenant, derived actor, operation, and key digest; bind the canonical request/effect; provide exact replay, same-key convergence, changed-body conflict, and serialization/compare-and-swap semantics without trusting client result/state claims.
6. **Applicable integrity checks:** validate schemas, canonical bindings, state/evidence relationships, audit/event cardinality and order, idempotency consistency, and expected transition facts. In-process implementations are defense-in-depth reference behavior; authoritative enforcement is supplied by the hosted persistence boundary.
7. **Transaction contract:** give the application service one operation boundary in which authorization recheck, idempotency acquisition, business state transition, evidence write, audit append, and canonical result commit either succeed together or leave no partial committed state. The kernel interface must be usable by profile modules and later draft/review/outreach modules without duplicating policy in adapters.

S14.1 specifies this boundary only. S14.2 later extracts/implements the protocol-neutral kernel and tests its local correctness claims. S14.3 later implements the authoritative hosted persistence side of the boundary.

## Profile-module boundary

The architecture record MUST retain S2.1 ownership of profile-specific behavior and exclude reusable security infrastructure from it. The profile module owns:

- closed human-readable research/outreach profile content, machine-enforced profile policy, deterministic local validation, representative fixtures, and inert prompt/content treatment;
- immutable version content and copy-on-write revision behavior;
- profile-specific lifecycle eligibility and state transitions for draft, validated, tested, active, superseded, authorized rollback, and profile archival;
- profile-specific validation/test evidence, activation/rollback predicates, tuple-wide active-version business invariant, failure behavior, and historical reproducibility; and
- business facts supplied to the kernel for authorization, idempotency, audit construction, and transactional persistence.

The profile module MUST NOT authenticate tokens, derive tenant/actor authority, implement a parallel authorization system, own generic audit/idempotency infrastructure, claim in-memory tamper resistance, implement adapter-specific policy, or independently decide persistence credentials/permissions. Its local repositories and reconstruction checks are test/reference mechanisms until bound to S14.3's authoritative persistence implementation.

S2.2 continues to own deterministic authenticated user -> tenant -> active profile -> allowed workflow resolution and minimum brief compilation. S14.1, S14.2, and S14.3 do not compile a brief or start S2.2.

## Defense-in-depth reconstruction and consistency

The architecture record MUST preserve useful application checks while stating their limit precisely:

- Reconstruct expected events and bindings from independently supplied governed operation inputs and compare cardinality, byte identity, predecessor topology, evidence, lifecycle state, and idempotency relations.
- Reject malformed, missing, duplicated, reordered, mismatched, stale, or inconsistent application-visible state and emit only safe failure information.
- Use deterministic fixtures, fixed vectors, mutation tests, and fault injection to prove application logic detects the modeled corruptions and preserves atomic behavior under its stated repository abstraction.
- Never call those checks tamper-proof, independently immutable, authoritative append-only enforcement, or protection from ordinary code able to modify both checked data and checking code in the same process.
- Rewrite test names, assertions, evidence, and documentation that currently imply that stronger claim. Green defense-in-depth tests prove only the specific mutation and boundary exercised.

## Future authoritative hosted persistence boundary

S14.3's future contract and implementation MUST make the Supabase/Postgres persistence boundary authoritative for append-only history and transactionally coupled security state. The S14.1 architecture record must require at least:

- distinct restricted runtime, migration/owner, and operator/break-glass credential roles; the ordinary application runtime receives only the least privileges needed for approved operations and cannot use owner/migration authority;
- database permissions and RLS where applicable as defense in depth, with API/kernel authorization still mandatory; no client, MCP adapter, REST adapter, model, or caller can select a tenant or bypass server authorization through a database credential;
- append-only audit enforcement using database privileges and/or database-enforced mechanisms that deny ordinary runtime `UPDATE`, `DELETE`, truncate, history replacement, or predecessor rewrite, with any exceptional administrative path separately controlled and audited;
- transactions that atomically couple idempotency acquisition/result, governed business transition, evidence/provenance, and audit append, with rollback on any required failure;
- database constraints/indexes sufficient for tenant/actor/object bindings, referential integrity, unique event/idempotency identities, profile-version uniqueness, applicable one-active invariants, ordering/predecessor rules, and non-null/closed-state requirements;
- authenticated reads and verification that do not treat application-provided expected history, hashes, or verifier state as the persistence authority;
- migration, backup/restore, deletion/retention, privileged-access, and failure/recovery evidence at the owning later gates without pretending Supabase backups cover object-storage recovery; and
- negative integration tests using restricted credentials to prove forbidden update/delete/cross-tenant/bypass/partial-commit behavior and favorable transaction tests for legitimate kernel operations.

S14.1 does not choose the final Python database library, provision Supabase/Render/domain resources, create a migration, or process a live credential. Those remain later governed implementation decisions within the already approved product direction.

## Hosted service and peer adapter model

MCP and REST MUST be peer adapters into one hosted application service and the same kernel:

```text
authenticated MCP adapter ─┐
                           ├─> application service -> security kernel -> domain module -> authoritative persistence
authenticated REST adapter ┘
```

Each adapter may perform protocol parsing, transport authentication integration, closed input/output mapping, and protocol-safe error translation. Neither adapter may own divergent tenant selection, authorization, lifecycle, audit, idempotency, transaction, persistence, or business policy. Equivalent authorized operations must reach the same service command and produce equivalent security decisions and committed effects, subject only to protocol representation. Tool annotations or client confirmations remain defense in depth and cannot replace server authorization or human business approval.

S3.1 later establishes the hosted service and authenticated MCP/REST adapter boundary after S14.3. It does not reimplement the kernel. Provider-owned URLs remain outside the public client contract.

## Preserved S2.1 disposition framework

The S14.1 architecture record MUST contain a path- and behavior-level disposition table for every one of the 13 preserved S2.1 checkpoint paths. It must use exactly one or more of these dispositions with a reason and destination owner:

- **Preserve:** retain profile content schema/canonicalization, lifecycle business rules, deterministic fixtures, useful safety regressions, and adverse history where they remain truthful.
- **Extract:** move reusable authenticated-context, tenant/actor binding, authorization, generic audit construction/provenance, generic idempotency/concurrency, transaction interface, and applicable integrity-check behavior into S14.2's kernel without merging the preserved branch wholesale.
- **Relocate:** assign authoritative append-only enforcement, restricted credentials, permission/RLS policy, transactions, and database constraints to S14.3; remove any claim that the in-memory carrier supplies that authority.
- **Simplify:** remove or reduce carriers, capability singletons, module/class mutation defenses, duplicated reconstruction machinery, and fixture complexity whose sole purpose was to simulate a security boundary that Python memory cannot provide. Simplification must not discard profile business rules or valuable regression coverage.
- **Retire or rewrite:** preserve the historical tests/evidence as adverse provenance, but retire or rewrite executable tests whose only pass condition is impossible same-process tamper resistance. Replacement tests must state whether they prove pure-function correctness, defense-in-depth inconsistency detection, adapter parity, restricted-database enforcement, or end-to-end transaction behavior.

The record MUST state that the checkpoint is an input inventory, not approved code and not a merge source. No file is copied, cherry-picked, edited, deleted, or applied by S14.1. S2.1's full contract/review/final-review/evidence history remains preserved at the checkpoint even where future contracts supersede its architecture claims.

## Exact backlog and dependency correction

### Evidence-based placement decision

The author considered the provisional alternatives rather than treating an S14.2/S14.3 sequence as prior authority:

- Folding authoritative persistence into S2.1 would repeat the defect by mixing reusable security infrastructure with profile business policy and would make other domain modules depend on a profile slice.
- Folding it into S3.1 would mix protocol/hosting adapters with the kernel's persistence authority and make REST/MCP parity depend on adapter implementation details.
- S3.2 owns a restricted read-side corpus adapter, not generic security writes. S4.1 owns later research-draft persistence after S3.4, so it is both too late and too domain-specific to secure earlier profile/service work. S7.1 owns paid provisioning, environment, and deployment migrations and currently depends on S3.1, so moving the application persistence foundation there would create an execution cycle and defer basic security until deployment.
- S14.2 can extract the protocol-neutral kernel contract and local defense-in-depth behavior without a database. The authoritative persistence adapter can then implement that stable contract before profile and hosted-adapter slices consume it.

The smallest non-circular correction is therefore two separate later implementation slices: S14.2 for kernel extraction, followed by S14.3 for authoritative hosted persistence. This is the Contract Author's evidence-based specification and remains an author claim until a fresh independent Contract Reviewer approves the exact FR-07 bytes. It is not derived from coordinator preference, chat summary, or prior approval.

The Documentation/Architecture Implementer MUST make the following semantic corrections in `IMPLEMENTATION.md`. No other item may change except mechanically necessary cross-references in the named cards.

### New E14 cards

Insert E14 in the P0 active backlog before E2 and add exactly these items and scheduling fields:

| ID | Title | Type | Priority | Implementation status | Completion-projected status | Dependencies | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E14 | Correct the hosted security and persistence boundary | Epic | P0 | Planned | Planned | E1 | None |
| S14.1 | Reconcile the S2.1 security boundary and dependent architecture | Slice | P0 | In progress | Done | None | None |
| S14.2 | Extract the reusable application security kernel | Slice | P0 | Planned | Ready | S14.1 | None |
| S14.3 | Implement authoritative hosted security persistence | Slice | P0 | Planned | Planned | S14.2 | None |

E14 purpose: establish one reusable server security kernel and one authoritative hosted persistence boundary before profile lifecycle or hosted endpoint work continues. E14 acceptance requires S14.1, S14.2, and S14.3 `Done` with their independent evidence; its verification cites each owning contract/evidence/final review. E14 remains `Planned` after S14.1 because two required children remain outstanding.

S14.1 purpose, acceptance, verification, and notes MUST faithfully describe this documentation-only contract, exact approved identities, preservation, no proposal amendment, no owner decision, serialization, and downstream non-authorization. Its implementation state is `In progress`; only the final-review-approved completion patch may change it to `Done`.

S14.2 purpose: extract a protocol-neutral kernel from the approved S1.1/S1.2 behavior and useful preserved S2.1 work, including authenticated context consumption, tenant/actor binding, authorization primitives, audit intent/provenance construction, idempotency/concurrency, transaction interface, and defense-in-depth integrity checks. Its acceptance/verification MUST explicitly disclaim in-memory tamper resistance and require failing-first application tests plus S1.1/S1.2 regressions. It performs no database migration, endpoint build, profile completion, merge of the preserved branch, or external action.

S14.3 purpose: implement the authoritative hosted Supabase/Postgres security persistence boundary for the kernel, including restricted credentials, permissions/RLS as applicable, atomic transactions, append-only enforcement, constraints/indexes, and adverse integration tests. It does not provision production infrastructure, build MCP/REST endpoints, complete profile behavior, or perform deployment. It remains `Planned` until S14.2 is `Done`.

### Corrections to existing cards

- **E2:** keep title/type/priority/blocker and product purpose; set `Dependencies: E1 and E14`. Amend its acceptance/verification/notes only enough to state that profile lifecycle consumes the shared kernel and authoritative persistence rather than implementing those boundaries itself. Keep `Status: Planned`.
- **S2.1:** keep ID/title/type/priority and the profile-specific product outcome; change `Status: Ready` to `Status: Planned`; set `Dependencies: S1.1, S14.2, and S14.3`; keep `Blockers: None`. Rewrite purpose/acceptance/verification/notes narrowly so S2.1 owns profile modules, validation/test, lifecycle, activation, rollback, archival, fixtures, and profile business policy on the shared kernel/persistence boundary; requires a fresh focused contract superseding only the architecture-incompatible claims; uses failing-first tests for the rebased implementation; and preserves the checkpoint plus all adverse history. It MUST explicitly state that checkpoint `d91e680...` is unverified, its payload is rejected/unapplied, no F-series continuation is authorized, and useful code/tests require the disposition process above.
- **S2.2:** keep `Status: Planned`, `Dependencies: S1.2 and S2.1`, and `Blockers: None`. Amend notes only to clarify that S2.1 completion transitively supplies the corrected kernel/persistence-backed profile lifecycle; do not add a redundant direct S14 dependency or start compilation.
- **E3:** keep `Status: Planned` and product scope; set `Dependencies: E0, E1, E2, and E14` as coordination summary. State that MCP/REST are peer adapters into the same service/kernel and do not own parallel policy.
- **S3.1:** change `Status: Ready` to `Status: Planned`; set `Dependencies: S0.3, S1.2, and S14.3`; keep `Blockers: None`. Amend purpose/acceptance/verification/notes narrowly so it establishes the hosted service plus authenticated MCP and REST peer adapters over the shared kernel/persistence boundary, tests adapter parity and safe authentication failures, and does not duplicate authorization/audit/idempotency/profile policy or claim deployment. S14.3 transitively requires S14.2, so no redundant direct S14.2 dependency is added.

No status, dependency, blocker, priority, purpose, acceptance, verification, or notes field outside E14/S14.1–S14.3, E2/S2.1/S2.2, and E3/S3.1 may change. In particular, S2.1 is not `Done` or `Blocked`; S2.2 and S3.1 do not become `Ready`; the rejected S2.1 completion payload is not applied; and no downstream completion is implied.

### Resulting executable sequence

The required sequence is:

```text
S14.1 documentation reconciliation
  -> S14.2 reusable kernel extraction
  -> S14.3 authoritative hosted persistence
       -> S2.1 rebased profile lifecycle -> S2.2 workflow resolution/brief compilation
       -> S3.1 hosted service and MCP/REST peer adapters
```

After S14.3, S2.1 and S3.1 are independent only if their approved contracts and exact file boundaries do not overlap. Any shared kernel/persistence interface, migration, service configuration, or unresolved dependency requires serialization. S2.2 cannot begin until the rebased S2.1 is `Done`.

## Architecture record requirements

The implementer MUST create `docs/architecture/S14.1-s2-1-security-boundary-correction.md` containing:

1. document control and exact approved FR-07 contract/review identities;
2. reconciled current state and terminal recurrence classification;
3. the corrected trust model;
4. kernel responsibility/interface matrix;
5. profile responsibility/interface matrix;
6. defense-in-depth claims and explicit non-claims;
7. authoritative hosted persistence controls and ownership;
8. MCP/REST peer-adapter flow and parity rules;
9. the complete 13-path S2.1 disposition table;
10. exact E14/S14.1–S14.3 and E2/S2.1/S2.2/E3/S3.1 dependency/status sequence;
11. proposal-amendment decision `N/A` and its direct evidence;
12. owner-decision result `N/A` and later separate authority boundaries;
13. risks, assumptions, open questions, and stop conditions; and
14. explicit no-code/no-test/no-database/no-endpoint/no-payload-application/no-external-action attestation.

The record may use diagrams/tables but cannot replace exact prose requirements or cite chat history as authority.

## Explicit non-goals and prohibited effects

S14.1 MUST NOT:

- edit, copy, cherry-pick, merge, run as implementation, delete, or otherwise modify any preserved S2.1 code, test, fixture, contract, review, evidence, handoff, or completion artifact;
- apply or reproduce as current authority the rejected S2.1 completion payload;
- implement or extract the S14.2 kernel;
- create a database schema/migration, implement Supabase/Postgres persistence, choose the final Python database/MCP library, or provision infrastructure;
- build the hosted service, MCP endpoint, REST endpoint, adapter, token verifier, deployment, monitoring, or live connection;
- implement or complete S2.1, S2.2, S3.1, or any later slice;
- weaken S1.1/S1.2 authorization, tenant isolation, audit provenance, idempotency, lifecycle, human-approval, no-egress, no-silent-persistence, or no-send requirements;
- broaden product scope, add hosted lead-research egress, change provider/model direction, amend the pilot decision, or infer a Product/Operator Owner approval;
- mark E14 `Done`, S14.2/S14.3/S2.1/S2.2/S3.1 `Done`, or S2.2/S3.1 `Ready`;
- merge, push, deploy, provision, contact an external party, use a live credential, or perform any external mutation.

## Acceptance criteria

- **AC-07-01 — State reconciliation:** The architecture record and backlog accurately reconcile current `main` with preserved checkpoint `d91e680...`, retain terminal `Not verified` and rejected/unapplied payload history, and prohibit any F-series continuation.
- **AC-07-02 — Correct trust model:** Ordinary same-process Python memory and its verifier are explicitly non-authoritative for tamper resistance; application reconstruction is defense in depth with exact non-claims.
- **AC-07-03 — Kernel boundary:** Server-derived authenticated context, tenant/actor binding, reusable authorization, audit construction/provenance, idempotency/concurrency, transaction interface, and applicable integrity checks have one protocol-neutral owner and preserve S1.1/S1.2.
- **AC-07-04 — Profile boundary:** Profile content, validation/testing, lifecycle, activation, rollback, archival, fixtures, and business policy remain profile-owned without duplicating kernel, persistence, or adapter responsibilities.
- **AC-07-05 — Authoritative persistence:** Future Supabase/Postgres enforcement includes restricted credentials, permissions/RLS as applicable, transactions, append-only controls, database constraints/indexes, authenticated reads, and adverse integration evidence, without present implementation or provisioning.
- **AC-07-06 — Peer adapters:** MCP and REST are peer adapters into one hosted application service and kernel, with parity and no duplicated authorization/business logic.
- **AC-07-07 — S2.1 disposition:** Every preserved checkpoint path has a reasoned preserve/extract/relocate/simplify/retire-or-rewrite disposition; useful lifecycle/security regressions remain, while impossible same-process tamper-resistance tests are retired or rewritten without erasing history.
- **AC-07-08 — Exact backlog graph:** E14/S14.1–S14.3 and affected E2/S2.1/S2.2/E3/S3.1 fields equal this contract; dependency references resolve, no cycle or hidden gate exists, and no unearned item becomes active or complete.
- **AC-07-09 — Proposal and authority fidelity:** Proposal amendment and current Product/Operator Owner decision are both `N/A` with evidence; no product direction, risk acceptance, live action, or scope is silently changed.
- **AC-07-10 — Documentation-only scope:** Only approved Markdown paths change; application/test/fixture/database/service/deployment/external state is preserved; `pytest` is truthfully N/A.
- **AC-07-11 — Evidence and checkpoint integrity:** Tracking-first and semantic baselines, exact hashes, commands/results, changed-file inventory, preservation manifest, role independence, checkpoint commits, and distinct approval/verification/application/merge/push/deployment states are complete and sanitized.
- **AC-07-12 — Completion projection:** The exact completion payload changes only permitted completion fields for E14/S14.1/S14.2, moves S14.1 to `Done` and S14.2 to `Ready`, leaves E14 and S14.3 `Planned`, and does not alter or complete S2.1/S2.2/S3.1.

## Allowed files and preservation boundary

After exact contract approval, the Documentation/Architecture Implementer may create or edit only:

- `IMPLEMENTATION.md` for the exact tracking-first, architecture, dependency, and later completion-payload changes defined here;
- `docs/architecture/S14.1-s2-1-security-boundary-correction.md`;
- `docs/evidence/FR-07-verification.md`;
- `docs/evidence/FR-07-implementer-handoff.md`; and
- `docs/evidence/FR-07-completion-patch.md`.

The ordinary governed review artifacts are separately role-owned at `docs/reviews/FR-07-contract-review.md` and `docs/reviews/FR-07-final-review.md`; they are not implementer files. A later completion application record may be created at `docs/evidence/FR-07-completion-application.md` only after an independent `Verified` decision and actual coordinator application.

Every other path is read-only. The implementer must reproduce the complete preserved S2.1 13-path checkpoint manifest from `d91e680...`, compare the current proposal/S1.1/S1.2/FR-05/FR-06 identities, inventory pre-existing work, and prove nothing outside the allowed boundary was included, overwritten, reverted, deleted, or relabeled.

## Objective documentation-only verification

Because S14.1 introduces no executable behavior, no failing-first or passing `pytest` phase applies. The implementer MUST record `pytest: N/A` with the approved reason and run exact objective checks from the repository root:

1. pre-edit branch/HEAD/status, current backlog hash, allowed-path inventory, and full preserved S2.1 checkpoint hashes;
2. immediate post-insertion readback proving E14/S14.1–S14.3 exist, S14.1 alone is `In progress`, and no other semantic edit preceded tracking-first state;
3. a deterministic backlog parser proving unique IDs, controlled fields/statuses, exact dependencies/blockers, all references resolved, no self-dependency/cycle, exact E14 children, and exact S2.1/S2.2/S3.1 gates;
4. deterministic required-heading/required-term and responsibility-matrix checks for the architecture record, including every kernel, profile, persistence, peer-adapter, disposition, non-claim, proposal, authority, and non-goal obligation;
5. a 13-path disposition/manifest equality check against `git ls-tree`/`git show` at `d91e680...`, including exact full SHA-256 values;
6. baseline-relative and tracking-first-relative changed-file/diff checks proving only allowed Markdown paths changed and protected nonallowlisted backlog bytes remain identical;
7. contradiction review against complete current AGENTS, proposal, S1.1/S1.2, FR-05/FR-06, S2.1 terminal review, and evidence architecture;
8. UTF-8/LF, local-link, trailing-whitespace, sensitive-content, secret/private-identifier, and `git diff --check` checks;
9. exact SHA-256 for every final artifact and the approved contract/review; and
10. isolated extraction, hashing, `git apply --check`, ordinary whole-payload application, status/dependency readback, protected-byte comparison, and nonapplication proof for the proposed completion payload.

Every command, working directory, exit status, concise sanitized output, expected/unexpected classification, criterion mapping, and preserved-state result must be recorded. A failed or contradictory check keeps S14.1 active.

## Evidence, checkpoints, handoffs, and recurrence

Every governed handoff uses one small scoped checkpoint commit containing only the sender's authorized artifacts. The handoff records exact full commit SHA, branch/worktree, stage-relative baseline and changed-file inventory, SHA-256 for every claimed artifact, stage-relative clean result, and pre-existing/out-of-scope inventory with confirmation of preservation. Checkpoint, contract approval, independent `Verified`, completion application, merge, push, and deployment are distinct; absent events are `N/A — not performed` with reason.

The implementer handoff must bind both the pre-tracking baseline and tracking-first checkpoint, approved contract and review, architecture/backlog artifacts, complete checks, preservation manifest, completion patch path/payload hash, and residual risks. It is a locator, not review.

FR-07 begins as a separate architecture disposition after the terminal S2.1 same-root stop. It does not reset S2.1's F-series or erase that recurrence. If FR-07 receives a first `Not verified`, only one coordinator-routed focused remediation may proceed. A second or materially equivalent recurrence follows the exact FR-05 classification/stop rule and records compared findings, protected criterion/control, causal mechanism, evidence, classification, and allowed disposition.

## Exact completion-patch lifecycle

Before final review, the implementer MUST store one exact unified Git diff at `docs/evidence/FR-07-completion-patch.md`. The first and only `diff` fence is the canonical payload; its bytes begin after the LF ending the opening fence and include the final LF before the closing fence. It must use UTF-8 without BOM and LF endings and record a payload-only SHA-256 reproducible with:

```sh
awk 'found && /^```$/ {exit} found {print} /^```diff$/ {found=1}' docs/evidence/FR-07-completion-patch.md | shasum -a 256
```

The payload may change only:

1. E14 existing `Verification` and `Notes` fields to accurate completion-gate references while leaving `Status: Planned`;
2. S14.1 existing `Status: In progress` to `Status: Done` and its existing `Verification`/`Notes` to exact evidence/review identities;
3. S14.2 existing `Status: Planned` to `Status: Ready` and its existing `Verification`/`Notes` only enough to record that S14.1 is verified and S14.2 itself is unstarted; and
4. no S14.3, E2, S2.1, S2.2, E3, S3.1, other item, protected field, architecture record, adverse-history record, code, test, fixture, proposal, or external state.

Only an evidence-backed independent `Verified` final review explicitly approving the exact payload path/hash authorizes the Coordinator to apply it mechanically. `Not verified` authorizes none. Application is whole-payload only. After application, the Coordinator creates a provisional completion-application record with exact actual payload/readback identities, and a fresh qualified independent auditor records fidelity. Merge remains unauthorized until `Final — fidelity verified`; push and deployment are not authorized by this contract.

## Risks, assumptions, and stop conditions

- **Risk — authority overstatement:** Mitigated by exact trust non-claims and persistence ownership. Stop if any wording suggests in-memory tamper resistance.
- **Risk — security weakening:** Mitigated by preserving S1.1/S1.2 invariants and relocating, not removing, authoritative enforcement. Stop if authorization, provenance, idempotency, atomicity, or tenant isolation is reduced.
- **Risk — circular dependency:** Mitigated by S14.1 -> S14.2 -> S14.3, then independent S2.1/S3.1 branches. Stop on unresolved or cyclic dependency output.
- **Risk — history erasure:** Mitigated by immutable checkpoint references and explicit rejected-payload/noncompletion language. Stop if adverse S2.1/FR-05/FR-06 history is rewritten or omitted.
- **Assumption:** Supabase/Postgres remains the approved pilot persistence direction and final Python libraries remain intentionally deferred. This contract does not select a library.
- **Assumption:** S14.2 can expose a protocol-neutral kernel interface before S14.3 implements its authoritative persistence adapter; S14.3 then supplies the required transaction/enforcement semantics before dependent profile/service work.
- **Stop:** required source inaccessible; preserved hash mismatch without authoritative explanation; unsafe/unpreservable workspace; product direction change; owner decision becomes necessary; implementation requires code/test/database/endpoint/external work; exact backlog graph cannot be made non-circular; role independence is uncertain; objective checks cannot decide a criterion; or any edit exceeds the allowed boundary.

## Contract-author checkpoint and review handoff

The author checkpoint contains only this contract. The exact full checkpoint SHA and final contract SHA-256 are supplied in the handoff after commit to avoid self-reference. Stage-relative inventory must be exactly `A docs/contracts/FR-07-s2-1-security-boundary-architecture-correction.md`; stage-relative state must be clean after commit. All pre-existing and out-of-scope paths, including the current local-main governance state and preserved S2.1 branch/checkpoint, remain outside the commit and are neither included, overwritten, reverted, nor deleted.

Commit is provenance only. Contract approval, implementation, final `Verified`, completion application, merge, push, and deployment are all `N/A — not performed` at author handoff. The fresh Contract Reviewer must directly read the complete exact contract and governing/relevant sources and issue `Approved` or `Changes required / Not approved` bound to path/version/full SHA-256. Implementation remains blocked until exact approval.
