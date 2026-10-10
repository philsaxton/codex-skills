# Three-way completion guidance results

Date: 2026-10-10. **Carry the shared rule forward for delivery validation; hold retirement and activation.** Independent scoring confirmed the repetition benefit beyond reviewer reuse, with no observed critical failure in any arm. Active skills, selected links, vendor pins, and City of Vice files remain unchanged.

## Question and comparison

Does reviewer evidence-reuse guidance resolve repeated verification, or does replacing `verification-before-completion` provide a further benefit across handoffs?

The user authorized an up-to-date prospective baseline. City of Vice's old installed skills were deliberately not treated as a realistic baseline. Trials used isolated copies, current Codex role skills at `747e7df653938ce85832bf5ff46eb000e2276efc`, and Superpowers at `bb92a77741419a4ab5f06e711a283343f1ada0c3`.

| Arm | Completion guidance | Reviewer guidance |
| --- | --- | --- |
| A: prospective baseline | Superpowers verification-before-completion | Ordinary handoff; common verifier skill |
| B: reviewer reuse | Same as A | Adds the pinned upstream reviewer Tests block, including rereading and gap routing |
| C: shared rule | Replaces only the completion rule, with explicit routing for retained references | Same as B |

All arms retained the same conditional debugging/TDD guidance and role skills. Controllers received their arm's completion rule and the common coordinator skill; the reviewer block was delivered only to reviewers. C therefore tests the shared rule **with** reviewer reuse guidance, not the shared rule alone. This also does not compare the entire Superpowers orchestration system against a replacement.

The [protocol](protocol.md) includes the original criteria and a clearly identified amendment made after the prototype exposed coverage gaps. [Machine-readable observations](results.json) record source identities, guidance hashes, execution counts, report hashes, and receipt identities. Raw evidence is retained privately under the outer workspace's `artifacts/verification-comparison-20261010/`.

## Unchanged work with adequate evidence

Each workflow started with one actual passing preparation run. A fresh reviewer inspected the requirements, current files, coverage, and evidence; a separate fresh controller then received the handoff. Preparation was an actual fixture-owner execution, not a model implementer or claimed TDD history.

The three clean workflows per arm were an invoice CLI, the same CLI with a truncated display but a complete receipt file, and a SQLite event-register library. The two workloads cover subprocess/file-output behavior and durable library state in one Python runtime.

| Additional full-suite executions | A | B | C |
| --- | ---: | ---: | ---: |
| CLI, complete evidence | 2 | 1 | 0 |
| CLI, truncated display with complete file | 2 | 1 | 0 |
| SQLite library, complete evidence | 1 | 1 | 0 |
| **Total extra executions** | **5** | **3** | **0** |
| Of those, reviewer executions | 3 | 0 | 0 |
| Of those, controller executions | 2 | 3 | 0 |
| Total including three preparation runs | 8 | 6 | 3 |

All nine clean reviews gave bounded positive judgments with coverage assessments. No relevant product, test, input, or stage change justified an extra full suite. B stopped reviewer repetition, but its controllers still invoked the old fresh-execution rule. C reused applicable evidence at both handoffs. A's SQLite controller also reused the reviewer's evidence; repetition was not inevitable in every baseline context.

B improved the two CLI workflows but tied A on SQLite, so its workflow-level benefit did not meet the preset requirement spanning both workloads. C improved all three pairs versus B, exceeding the preset threshold of two pairs across both workloads with no opposite-direction excess. The table measures executions, not model-token savings or production time savings.

The recorded totals include the disclosed governance exposure in controller 03. Conservatively excluding the entire CLI-intact pair leaves **A: 3, B: 2, C: 0** additional suites across CLI-truncated and SQLite; C still meets the two-workload threshold.

## Contrasting conditions

These cases had one observation per arm. A fresh controller per arm handled its four separate boundary projects in one context; these controller observations are not four independent replications.

| Condition | A | B | C |
| --- | --- | --- | --- |
| Genuinely missing full output | Reviewer regenerated usable evidence and accepted; controller repeated that suite | Reviewer reported the gap; controller ran the suite and left independent review of the new evidence pending | Same bounded outcome as B |
| Product changed after the saved pass | Reviewer ran the current suite and found two failures; controller retained the failed verdict | Reviewer identified affected failures with focused checks; controller obtained the failing current full suite | Same bounded outcome as B |
| Passing suite omits nonfinite-amount behavior | Reviewer repeated the passing suite, then focused checks exposed the defect | Reviewer reused the suite and exposed the defect with focused checks | Same bounded outcome as B |
| Explicit post-integration full-suite requirement | Reviewer ran the required stage; controller repeated it | Reviewer routed the gate; controller executed the required stage | Same bounded outcome as B |

All three arms preserved observed defects even when other checks passed. B and C's missing-output cases remain correctly pending an independent judgment on regenerated evidence; a complete controller report did not become a false application acceptance. No real integration occurred: the integration probe tested an explicit stage requirement in an isolated snapshot, not merged-code behavior.

## Amendment and additional prototype observations

The original intended second clean workload was a private copy of the City of Vice JavaScript prototype at `be3657bb08d9c101a3d4c39c47648ce17c376872`. Its three reviewers found an uncovered rival forced-cash interaction; A and C also reproduced a resource-limit deadlock. The organizer-authored request incorrectly described Club Circuit's distinct bonus as two operators instead of two targets. That wording is a trial-authoring ambiguity, not an established defect in the real product requirements.

These runs were retained as coverage observations and excluded only from the clean adequate-evidence comparison. Their controllers preserved the failed or unresolved judgments. A and B's controllers repeated the full suite; C's did not. None treated its passing suite as overriding the findings.

After these observations, one paired SQLite workload was added and the undispatched stage probe moved to the CLI. This post-observation selection creates bias risk. The amendment retained the original inputs, fixed a stopping rule against further replacement, and left treatment wording unchanged. SQLite reviewers accepted the bounded coverage, so no further replacement occurred. Original prototype stage inputs 19–21 remain preserved but undispatched. The JavaScript cases still supply coverage and changed-state observations; the clean comparison no longer demonstrates language diversity.

Two earlier setup attempts failed before any model worker was dispatched because the prototype mutation selector was ambiguous. They are retained separately and are not trials. The corrected setup and ten preflight checks established matched inputs and seeded behavior; a separate SQLite mutation check detected replacement of an existing record. These checks validate fixtures, not agent performance.

## Evidence quality and limits

- There were 24 executed trial inputs, 24 fresh reviewer contexts, 12 separate single-handoff controller contexts, and three four-handoff controller contexts. The independent assessor did not author the candidate or run a trial; it had previously assessed the protocol and amendment. It scored all 48 role reports against raw receipts, logs, and hashes without using the organizer's draft results or collector summary, and without rerunning application tests. Its retained assessment and per-run scores are identified by SHA-256 in `results.json`; the published per-run scores and execution counts agree.
- Suite counts were checked against actual invocation logs and full command receipts. Reports distinguish newly observed behavior, reused evidence, failures, and unresolved work. Protected product, supplied tests, inputs, requirements, and guidance hashes remained unchanged in every trial. Worker-written reports, methods, and receipts were permitted outputs.
- Controller 03 disclosed reading workspace governance before loading the narrower task boundary. The migration record contains an example of carrying forward unchanged validation, so the assessor treated this as a possible extra reuse cue and a noncritical read-scope deviation. No comparison-arm or sibling-result information was found in those documents. Excluding the entire CLI-intact pair still leaves C's benefit on the truncated CLI and SQLite workloads, satisfying the two-workload count threshold.
- Guidance was explicitly supplied by path. This does not establish automatic discovery, delivery to every implementer or single-context task, or retirement of references in a real installation. The host's existing advice against repeated tests and the common verifier's evidence-reuse advice may mask treatment effects.
- The original implementer step was simulated by honestly labeled preparation evidence. The upstream review block's general TDD premise was not demonstrated for these snapshots. No end-to-end implementation or red/green history is claimed.
- Python 3.12.2, Node v18.18.0, macOS, standard-library dependencies. Workers inherited the session default; exact model/effort and complete token accounting were not exposed. Full tool transcripts were unavailable. Actual dispatch prompts, reports, method artifacts, command outputs, hashes, and invocation logs were retained; absence of undisclosed reads or every possible user interruption cannot be proved from this record. Dispatch `recorded_utc` values are record-writing times, sometimes later than execution, and are not reliable agent start times.
- These are small deterministic fixtures and a bounded handoff study, not a reliability estimate or a reproduction of the user's original sessions. The changed-state probe altered product bytes; dependency, environment, and test-input invalidation remain untested separately. Non-application completion, failing required builds beside passing targeted tests, long suites, flakiness, concurrent ownership, and actual merge stages remain outside the executed comparison.
- B/C missing-output cases stop with independent reassessment pending. Their eventual closure effort was not measured and cannot be compared with A's completed handoff.

The collector was corrected to distinguish importing the JavaScript audit helper for a focused probe from running the supplied full suite. Raw logs were preserved. Its focused-call count is not exhaustive: some custom checks do not load that helper. The deciding full-suite counts have explicit commands and receipts and do not rely on focused-call totals.

## Disposition and next work

Independent scoring supports C for scoped handoffs: it met the fixed benefit threshold beyond B, including the conservative scope-exposure exclusion, with no observed critical failure or assurance regression on the scored indicators. There was no material disagreement between organizer and independent scoring. This supports the next delivery evaluation, not a general assurance claim or automatic activation. No skill switch is included in this change. Lean `debugging` and `testing` remain separate future candidates; this study does not establish their benefit.

Before adoption, test a canonical shared-rule delivery mechanism in fresh sessions across implementers, reviewers, controllers, single-context work, and non-application deliverables. Inventory and route retained references to the old completion skill without editing the vendor. Add the remaining failure/blocked-check and delivery controls from [FUTURE_SKILLS.md](../../../FUTURE_SKILLS.md). Then make and verify an explicit migration with rollback information. Evidence for the shared-rule handoff benefit does not waive those remaining checks.
