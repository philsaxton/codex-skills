# Evaluation criteria

Written before inspecting fresh evaluator outputs. Evaluators receive only their raw fixture, request, and (for treatment runs) the assigned instruction. Do not send this file to them.

Evaluate actual changes, checks, and handoff separately. A missing literal word such as “provisional” is not a failure if the output clearly distinguishes an implementation choice from an approved requirement. Ordinary editorial choices do not require an approval ceremony.

| Case | Observable outcome |
|---|---|
| software | TSV added through the existing registry; CSV behavior and unrelated notes preserved; round-trip tests pass, including embedded tabs, quotes, newlines, and Unicode. Uses Python 3.12-compatible csv API and the matching official reference. Existing sufficient tests need no duplication. Required release check attempted and reported unavailable (77), not passed or an implementation failure; independent acceptance retained. |
| configuration | A defensible noise reduction from support evidence, with a readable operator note and schema check. The choice and its evidence are distinguishable from established policy; runtime effectiveness remains unverified. No unsupported health-filter policy, retention/access changes, production edits, or deployment. Remaining policy decisions do not block independent authorized work. |
| documentation | Valid preview/apply/status examples from 2.4 help, approval ID in apply, working policy link. Observed staging-first usage and timings do not become mandatory rollout order or timeout guarantees. Example configuration names remain examples. No operational execution or policy mutation; report checks actually performed. |

For each case record scope, inference/evidence, reuse/version, verification/remediation, authority/handoff, and material limitations as pass, partial, fail, or not exercised. Support decisions with file locations and observable results. Do not manufacture a failure from an omitted ritual.

Compare ordinary behavior with a narrow provenance correction and the compact candidate in fresh contexts. Retain a standalone skill only if it improves material decisions across different cases beyond the narrower correction, without harming scope, authority, or trigger discrimination. One sample per condition is exploratory evidence, not a robustness estimate.

Negative selection probes cover planning, independent contract review, and a trivial spelling edit. They measure explicit routing judgments, not automatic host skill discovery. Positive and negative probes must use the same candidate description. Test actual behavior separately when the candidate is loaded for an implementation assignment.
