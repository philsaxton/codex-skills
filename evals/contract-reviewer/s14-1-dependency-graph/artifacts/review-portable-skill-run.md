# Independent Blinded Contract Review — Counterfactual S14.1 / FR-07

## Review control

- **Artifact reviewed:** `/Users/phil-mac/.codex/visualizations/2026/08/27/01a044a9-be3c-7721-8042-02afc031f78a/S14.1-counterfactual-contract.md`
- **Artifact label/version:** `EXPERIMENTAL — NON-AUTHORITATIVE RETROSPECTIVE BENCHMARK`, Experimental 1.0
- **Artifact SHA-256:** `6a750764c946134ede1cf405f07b83b77f806f87fddb86b5cae3933c4b8a9c2a`
- **Artifact line count:** 231
- **Review method:** complete portable Contract Reviewer skill at `/Users/phil-mac/.codex/worktrees/experiments/client-agent-workspace/.agents/skills/contract-reviewer/SKILL.md`
- **Reviewer context:** fresh independent blinded reviewer `/root/reviewer_skill_blind_rerun`
- **Recorded:** `2026-08-28T11:00:53-0400` (`EDT`, America/New_York)
- **Review basis:** historical project baseline commit `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1` and preserved adverse S2.1 checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`, repository `/Users/phil-mac/Projects/client-agent-workspace`
- **Authority:** this is a readiness review of a non-authoritative benchmark. It is not project contract approval, implementation authority, completion authorization, or a final-deliverable review.

## Executive judgment

The central architecture conclusion is supported by the permitted evidence: the terminal S2.1 review established that ordinary same-interpreter module, class, object, repository, and verifier surfaces did not create an integrity root independent of the history they checked. Moving authoritative profile lifecycle state and audit history behind a durable boundary outside ordinary application-process memory is a coherent response and remains consistent with the MVP's hosted-service direction, S1.1 lifecycle invariants, and S1.2's statement that current in-memory artifacts are executable specifications/test doubles rather than production security claims.

The artifact is nevertheless **not ready for authoritative project implementation**. Two unresolved contract defects would force an implementer or later contract author to invent decision-bearing requirements: the implementation baseline/backlog transition is not selected, and the new S2.3 authority is not integrated into the closed S1.2 gate/evidence model. A third intentional limitation—counterfactual IDs and no stable repository-relative contract/architecture identity—also prevents exact project approval. The artifact is **ready only for use as a retrospective architecture benchmark and as input to a new authoritative contract-authority decision**.

## Findings

### B-01 — The contract does not select the implementation baseline or exact S2.1 state transition

**Affected areas:** backlog and interface reconciliation; AC-CF-01, AC-CF-07, AC-CF-09, AC-CF-10; completion projection.

**Evidence:** the benchmark names both permitted commits as its semantic boundary but never states which `IMPLEMENTATION.md` blob is the implementation input. At `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`, S2.1 is `Ready`, depends only on S1.1, and has blocker `None`. At `d91e68065aa99c7368eab21c8a93eeac6d7d3893`, S2.1 is `In progress`, still depends only on S1.1, and carries the approved-contract/role record. The benchmark instead says revised S2.1 depends on S1.1 and the completed correction, “remains not `Done`,” and may become `Ready` only through the exact completion projection. It does not say whether the governed correction starts from the baseline's `Ready` card, the checkpoint's `In progress` card, or a newly reconstructed projection, nor does it specify S2.1's exact pre-completion status.

**Impact:** the required tracking diff, protected baseline hash, completion-patch preimage, preservation proof, and atomic status projection differ materially between those states. One implementer could demote baseline S2.1 `Ready -> Planned` while another could preserve checkpoint S2.1 `In progress`; both could claim to satisfy “not Done.” The completion payload therefore cannot be uniquely constructed or objectively applied, and the card-aware parser cannot have one expected result.

**Required disposition:** the authoritative adaptation must name one exact `IMPLEMENTATION.md` Git object as the correction's semantic/pre-patch input and specify every interim and completion status transition. It must also state that the other commit is evidence-only and define how its S2.1 bytes/history remain preserved outside the correction branch.

**Blocking:** yes, for project implementation or approval.

### B-02 — S2.3 is not represented in the controlling S1.2 runtime gate and evidence model

**Affected areas:** AD-04; backlog S2.3; future S2.3 interface obligations; AC-CF-03, AC-CF-04, AC-CF-07, AC-CF-09.

**Evidence:** the benchmark adds an executable S2.3 that owns authoritative durable profile lifecycle and audit integrity and says S1.2 remains controlling, including later-gate denial until the owning executable slice supplies favorable runtime evidence. The baseline S1.2 contract defines exactly five gate identities and an evidence model whose minimum TM-015 audit-integrity obligations are `current_contract`/S1.2, `write_runtime`/S4.1, and `pilot_operations`/S7.2. Its enabled-feature set has no profile-lifecycle-authority feature, and its minimum required read-only gate evidence names S3.1–S3.4 rather than S2.3. Although the structured model can potentially be extended with additional narrowing obligations, the benchmark does not require the S2.3 contract to add an exact S2.3 obligation, owner, evidence subjects, phase, gate, feature/inventory rule, or evaluator mutation.

**Impact:** backlog dependencies prevent S2.2/S3.3 from proceeding before S2.3, but the claimed controlling S1.2 security gate cannot itself consume or deny on S2.3's durable-authority evidence. A future implementer would have to decide whether to alter the S1.2 catalog/test plan/evaluator, create a separate gate, attach S2.3 evidence to an existing gate, or rely on backlog status alone. Those choices change executable security behavior and evidence ownership; they are not a vendor-neutral persistence detail.

**Required disposition:** the authoritative adaptation must choose the gate integration. One viable direction is to require the future S2.3 contract to extend the S1.2 threat catalog/test plan/evaluator with exact profile-lifecycle authority obligations and evidence subjects at `before_read_only_external_research_validation`, while retaining S7.2's pilot-operations ownership. A separately scoped security-gate reconciliation slice is also possible. Whichever route is selected must be an explicit dependency and acceptance predicate, not an inference from AD-04.

**Blocking:** yes, for project implementation or approval.

### B-03 — Intentional counterfactual identities prevent the required exact-version project review boundary

**Affected areas:** benchmark control; scope; architecture-record path; E14/S14.1/S2.3 identifiers; review/checkpoint/completion lifecycle.

**Evidence:** the artifact expressly has no authority, treats E14/S14.1/S2.3 as counterfactual choices, leaves the architecture-record path to a future authoritative workflow, and resides outside the repository. The baseline Contract-Reviewer Guide requires a stable repository-relative contract path, exact version/hash, identifiable selected slice, and scoped checkpoint boundary before an ordinary approval or governed handoff.

**Impact:** there is no exact project slice identity, repository contract path, architecture-record path, checkpoint commit, or hash-bound project handoff to approve. Link, path, changed-file, checkpoint, and completion-record checks cannot be instantiated from these bytes alone.

**Required disposition:** no change is needed for retrospective benchmark use. Before project use, an authoritative coordinator/author workflow must assign the actual slice/epic IDs, repository-relative contract and architecture-record paths, exact source baseline, branch/worktree, and checkpoint identity, then obtain fresh review of those exact project bytes.

**Blocking:** yes for project use; intentional and non-blocking for the limited benchmark purpose.

### A-01 — The AD/AC identifier cardinality check is ambiguous

**Affected areas:** documentation-only verification item 2; AC-CF-02, AC-CF-07, AC-CF-09.

**Evidence:** verification requires that “the architecture record and `IMPLEMENTATION.md` contain every AD and AC identifier exactly once.” It is not decidable whether each identifier must occur once in each file, or once across the union of the two files. The acceptance criteria explicitly require the architecture record to state AD-01 through AD-05, but do not define where AC-CF-01 through AC-CF-10 must be reproduced. Other governed records will necessarily use the same identifiers for criterion mappings, although the stated check names only two files.

**Impact:** two reasonable implementations and parsers can disagree while each follows the prose. This weakens the claimed objective evidence and can force redundant acceptance text into an architecture record or backlog card.

**Required disposition:** define the exact files and per-file cardinality for AD definitions, AC definitions, and AC references. Prefer semantic parser rules—for example, each AD definition exactly once in the architecture record, each backlog item ID exactly once in `IMPLEMENTATION.md`, and each AC definition exactly once in the authoritative contract—while allowing mapped references in evidence records.

**Blocking:** advisory for benchmark interpretation; blocking if retained unchanged in an authoritative implementation contract.

## Questions for the applicable authority

1. Which exact `IMPLEMENTATION.md` blob is the correction's implementation input: `a3f3...:IMPLEMENTATION.md`, `d91e...:IMPLEMENTATION.md`, or a separately authorized reconciled preimage? What is S2.1's exact status before and after tracking, before final review, and after the atomic completion payload?
2. Must S2.3 extend the existing S1.2 structured threat/gate artifacts, or will a separate executable security-gate slice own that integration? Which exact gate denies when S2.3 authority evidence is absent or stale?
3. What canonical project IDs and repository-relative paths replace the experimental E14/S14.1/S2.3 and unspecified architecture-record path?

## Non-binding suggested options

### Option 1 — Baseline-first reconciliation

Use `a3f3...:IMPLEMENTATION.md` as the authoritative correction input and treat `d91e...` solely as preserved adverse evidence. Explicitly project S2.1 from baseline `Ready` to `Planned` when the new correction dependency is added, keep it `Planned` while the correction is active, then atomically complete the correction and promote revised S2.1 to `Ready`. This gives one clean mainline preimage and preserves the adverse checkpoint without importing its unverified implementation state.

**Tradeoff:** the authoritative S2.1 revision must separately specify which checkpoint bytes are reusable; none are silently merged.

### Option 2 — Add S2.3 obligations to the existing S1.2 gate model

Require S2.3's future approved contract to add exact profile-lifecycle authority obligations, tests/inspections, evidence subjects, ownership, and denial behavior to the S1.2 structured artifacts before S2.3 can complete. Bind the runtime obligation to the read-only external-research gate because S2.2/S3.3 must consume authoritative profile state before S3.4, and retain S7.2 for operational/pilot recovery and privileged controls.

**Tradeoff:** this makes S2.3 a cross-boundary application/security change rather than a persistence-only slice, so its allowed files and regressions must include the S1.2 evaluator/artifacts.

### Option 3 — Separate security-gate reconciliation

Create a small explicit executable security-gate slice between the architecture correction and S2.3. It updates the S1.2 model/evaluator contract surface first; S2.3 then implements against that approved gate.

**Tradeoff:** clearer role/scope separation, but adds another P0 dependency and contract cycle.

## Readiness

**Ready only for retrospective benchmark use and for informing a new architecture/contract-authority decision.**

**Not ready for authoritative project implementation, contract approval, or downstream handoff** until B-01 through B-03 are resolved in exact project bytes. A-01 must also be made decidable if its verification wording is retained.

This readiness judgment is not approval and authorizes no repository action, implementation, completion transition, merge, push, deployment, or external action.

## Blindness, exclusions, independence, and preservation

- I did not author or edit the counterfactual contract, inspect any prior review of it, infer an expected finding, or participate in an earlier review of these bytes.
- I did not open, read, hash, diff, or use any original FR-07 artifact, later S14.1 artifact, or commit at or after `e707602f75391eeed5605c0fd25de39bac9400c4`. One current-worktree path name containing `FR-07-test.md` appeared incidentally in a non-mutating `git status --short` preservation read; its contents and metadata were not investigated or used.
- I did not query or use conversation-history artifacts as review evidence.
- Project semantics came only from direct Git-object reads at the two permitted commits. Current working-tree files were not opened for review.
- The repository was not modified. Pre-existing current-worktree state observed before and after review remained `M .codex/config.toml` and `?? docs/contracts/FR-07-test.md`; neither path was touched.
- The only created artifact is this review outside the repository.

## Direct evidence inventory

### Method only

- Complete portable Contract Reviewer skill: `/Users/phil-mac/.codex/worktrees/experiments/client-agent-workspace/.agents/skills/contract-reviewer/SKILL.md`.

### Frozen reviewed artifact

- `/Users/phil-mac/.codex/visualizations/2026/08/27/01a044a9-be3c-7721-8042-02afc031f78a/S14.1-counterfactual-contract.md`, SHA-256 `6a750764c946134ede1cf405f07b83b77f806f87fddb86b5cae3933c4b8a9c2a`, 231 lines.

### Baseline commit `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1`

- `AGENTS.md`; `IMPLEMENTATION.md`; `docs/hosted-business-development-assistant-mvp-proposal.md`; `docs/roles/coordinator.md`; `docs/roles/contract-reviewer.md`; `docs/governance/evidence-records.md`.
- `docs/contracts/S1.1-domain-mcp-rest-contracts.md`; `docs/contracts/S1.2-threat-model-and-authorization-test-plan.md`.
- Relevant FR-05/FR-06 governance, final-review, and completion-history Git objects used only to confirm the separately governed post-stop authority route and preservation model.

### Adverse checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`

- `IMPLEMENTATION.md`; complete `docs/contracts/S2.1-profile-modules-and-lifecycle.md`; complete terminal section and preserved finding history in `docs/reviews/S2.1-final-review.md`.
- Identity checks reproduced the checkpoint hashes for the S2.1 contract, reviews, verification, handoff, completion patch, implementation module, focused test, and both fixtures. No checkpoint file was checked out or modified.

## Receipt

- **Reviewed:** frozen non-authoritative Counterfactual S14.1 / FR-07 Contract, Experimental 1.0, SHA-256 `6a750764c946134ede1cf405f07b83b77f806f87fddb86b5cae3933c4b8a9c2a`.
- **Basis:** only baseline `a3f3a1dd6a3e17a79e7bdfccb4909c24682dc6b1` and adverse checkpoint `d91e68065aa99c7368eab21c8a93eeac6d7d3893`, read as Git objects.
- **Disposition:** ready only for retrospective benchmark/architecture-decision input; not ready for project implementation or approval.
- **Unresolved:** B-01 implementation baseline/state projection; B-02 S1.2/S2.3 gate integration; B-03 canonical project identity/path; A-01 identifier-check cardinality.
- **Evidence location:** this review file and the exact Git objects named above.
- **Repository changes:** none.
