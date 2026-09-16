# Implementer skill plan

Date: 2026-09-15
Status: Evaluation completed 2026-09-16; standalone skill remains on hold. The experimental candidate is retained under `evals/`, not shipped or activated.
Tracking: [GitHub issue #1](https://github.com/philsaxton/codex-skills/issues/1).

## Purpose

Evaluate and, if supported by evidence and subsequently authorized, build a compact standalone `implementer` skill for carrying an authorized work item through implementation, relevant verification, remediation, and handoff. Optimize for Astra while keeping substantive requirements binding on every consumer.

The original planning request authorized this plan, a backlog issue, and the agreed contract-author refinements. The 2026-09-16 request to implement the plan authorized the evaluation below. Installation, permissions, review policy, and dependency-adoption authority remain unchanged.

## Why the earlier candidate was held

The [Implementer backlog entry](../../FUTURE_SKILLS.md#implementer) records an evidence-tested hold from 2026-08-25, introduced by commit `62a2cc3aeda59e1d3f5a761ff04492197880caab`. Baseline trials across software, configuration, operational, and documentation work reportedly preserved scope, unrelated work, proportional checks, and review ownership using existing guidance. A broad implementer role appeared duplicative.

The record also reports a narrower recurring problem: three no-contract controls converted reasonable inferences into settled execution criteria without identifying their evidence, provisional status, or uncertainty. Subsequent commits `e5f85dfd7c10fa5990d941b5409696469923c070` and `b4603cadd0f551c3d06ad8a63541352ffeb4d81b` added dependency escalation and smallest-coherent-scope expectations to the candidate, without implementing it.

These are findings recorded in repository history. The original trial transcripts and executed model identities have not been revalidated for this plan. They do not establish present Astra behavior. The requesting workspace has since removed its Superpowers activation links, so the old combination of planning, TDD, and verification guidance must not be assumed to remain loaded. This workspace change is motivation to retest, not a universal installation assumption.

The [Astra guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) favors focused instructions, contextual source reading, and explicit completion boundaries. A useful implementer skill must add an execution-specific discipline rather than restating ordinary coding advice.

## Proposed role boundary

- **Trigger:** An authorized, bounded work item needs implementation and supporting verification. Include work based on a user request or issue without requiring a formal contract.
- **Own:** Scoped changes, relevant checks, fixing failures caused by the change, truthful progress, and an evidence-backed handoff through the authorized completion boundary.
- **Do not absorb:** Requirements authorship, backlog selection, coordination, independent final review, or acceptance authority reserved by the project.
- **Standalone use:** Require the evidence needed for the task, never proof that another named skill ran. Formal contracts, coordinators, and reviewers are optional workflow inputs unless the project requires them.
- **Completion:** Continue through authorized implementation and verification instead of stopping at the first draft. Identify any remaining required review or release step; do not invent a new approval gate or claim an independent acceptance decision.

## Candidate guidance to evaluate

1. Ground implementation in current authoritative requirements and preserve unaffected invariants. Without a formal contract, state material inferred scope, criteria, evidence, and uncertainty; keep inference provisional. Resolve consequential ambiguity with its owner while continuing independent authorized work.
2. Deliver the simplest coherent solution meeting the current requirements. Avoid speculative abstractions and unrelated changes.
3. Prefer suitable existing project capabilities and maintained open-source libraries, using supported extension points. Evaluate custom implementation against security, licensing, integration, and maintenance costs. Adopt dependencies only within existing authority; route a meaningful dependency or contract change to the controlling owner.
4. When selecting or changing API or library usage, consult official documentation for the installed or explicitly targeted version. An upgrade is a separate scope decision, not an incidental consequence of reading newer documentation.
5. Add or adapt tests that demonstrate required behavior and cover material regression risks. Reuse equivalent coverage, satisfy required checks, and propose changes to established criteria or gates explicitly. Retain adverse results and distinguish a failure from an unavailable check.
6. Hand off the actual changes, relevant check results, limitations, unresolved decisions, and the next continuation condition. Use project-required identities or formats where applicable, without imposing a universal evidence schema.

These are design inputs, not six mandatory sections or a fixed execution itinerary. Consolidate or omit guidance that does not improve observed decisions. Concrete stacks, commands, paths, retry counts, storage formats, and permissions remain project-specific.

## Work sequence

1. **Re-establish the baseline.** Inspect current author/reviewer/coordinator handoffs and the actual host-loaded instructions. Recover the earlier evidence where available and distinguish historical claims from newly observed results. Use materially different software and configuration/documentation tasks, including no-contract cases.
2. **Test the need.** Run fresh Astra baseline tasks without an implementer skill. Inspect actual deliverables and verification, not only written intentions. Compare the narrow provisional-requirements correction with a compact execution-owner candidate if failures justify it. Use project role documents later as comparison material rather than copying their controls into a portable skill.
3. **Draft the smallest supported candidate.** If the role has a distinct benefit, create `implementer/SKILL.md` with a narrow description and a self-contained body. Add UI metadata or resources only when they support a concrete use. Do not add generic helper scripts, checklists, or mandatory companion skills.
4. **Validate handoffs and behavior.** Use equivalent fresh contexts and raw fixtures for baseline/candidate comparisons. Keep expected findings out of evaluator prompts. Inspect final artifacts, relevant test outcomes, unintended work, and stopping behavior. Correct demonstrated failures and rerun affected cases.
5. **Record the disposition.** Retain the candidate only with evidence of a distinct useful contribution. Otherwise recommend the narrower existing-skill correction or continued hold, explaining what evidence is missing. Update this plan, the issue, and the candidate backlog consistently. Installation and publishing follow their own authorized scope.

## Evaluation and acceptance

| Case | Required observation |
|---|---|
| Accepted bounded change | Implements the agreed outcome, preserves unrelated work, checks relevant behavior, fixes attributable failures, and reaches the authorized handoff. |
| No formal contract | Makes material inferred criteria and their basis visible without presenting them as approved requirements or demanding a formal contract unnecessarily. |
| Existing extension point versus custom code | Uses the suitable supported mechanism; accepts a justified custom solution when a dependency would impose disproportionate cost. |
| Version mismatch | Uses documentation matching the actual target; does not silently upgrade or promise unavailable APIs. |
| Dependency or scope boundary | Continues within existing authorization and routes only the affected unresolved adoption or semantic decision. |
| Existing adequate tests | Reuses meaningful evidence without inventing duplicate tests or gates; preserves required checks even when they appear redundant. |
| Broken implementation or unavailable check | Distinguishes actual failure from missing evidence, remediates authorized defects, and reports remaining limits accurately. |
| Planning, contract review, or trivial unrelated edit | Does not hijack another role or impose an implementation ceremony. |
| Required independent acceptance | Supplies the current result and evidence without self-accepting or bypassing the required review. |

Record exact candidate identity, inputs, host-selected model and reasoning settings, observed output, and limits. Do not infer model identity from self-description. Astra is the primary evaluation target; Sol is optional and Terra/Luna compatibility is not a release gate. Switching models must not be assumed to load different instructions. No model-specific routing or configuration change is proposed.

Acceptance requires a demonstrated non-duplicative benefit across materially different cases, preservation of substantive requirements and authority, and a discriminating trigger. A single favorable sample is not a robustness claim. Run the installed Skill Creator validator on any future candidate; check role handoffs and relative links. Run the existing link-installation test if adding the skill changes the installation inventory. Other suites apply only to affected helpers or interfaces; do not add wording-matching tests.

## Decisions kept separate

Any proposal to relax confirmation, dependency-adoption authority, mandatory checks, independent acceptance, or release gates must identify the exact old and new rule, impact, and evidence for user decision before application. This plan proposes no such relaxation. A rule against unnecessary new verification is not permission to remove existing requirements.

## Original planning deliverables

This planning pass produces the backlog issue, this document, an updated candidate disposition, and focused contract-author wording for reuse, version-compatible documentation, and meaningful verification. The author already covers simplicity; no duplicate simplicity rule is needed.

At the planning handoff, baseline/candidate runs, automatic-selection evidence, and new implementer artifacts remained future work. The historical hold was reopened for evaluation rather than relabeled as an Astra result.

## Execution receipt — 2026-09-16

Completed the work sequence with nine fresh implementation trials: three materially different cases (software, configuration, documentation), each under ordinary behavior, a narrow provenance correction, and the compact candidate. Host dispatch selected `gpt-6-astra` at medium reasoning with no inherited conversation. Actual edits and verification were inspected; the parent independently reran relevant checks and compared preserved files. Three additional fresh boundary cases excluded planning, independent review, and a trivial edit from candidate use.

The cases showed no distinct material benefit for the standalone candidate. Baseline behavior already preserved scope, provisional evidence, supported reuse, the target API version, required checks, and independent acceptance. The narrow correction increased explicitness without changing substantive decisions. Keep the standalone skill on hold, retaining the candidate only as an experimental input. Do not add an existing-role correction without a demonstrated gap.

See the [evaluation bundle](../../evals/implementer/2026-09-16/README.md) and [disposition](../../evals/implementer/2026-09-16/DISPOSITION.md) for exact prompts, candidate identity, host settings, raw fixtures, actual changed files, verification results, and limitations. Skill Creator validation and the existing installation-link test pass. Existing role edits and active support pins were preserved; no installation or publishing occurred.

The older final report was recovered and identifies Terra/read-only scenarios; it remains historical evidence. These new small synthetic Astra trials do not establish robustness or real dependency-adoption tradeoffs. Automatic host selection is untested; the boundary trials test explicit catalog selection only. Reopen skill implementation when new realistic failures establish a portable benefit beyond ordinary behavior and the narrow correction. Issue #1 remains the open backlog for that evidence.

The user subsequently approved the prepared issue update, merge, and push on 2026-09-16, resolving the initial automatic approval review block. Publication includes the evaluation evidence and the original contract-author refinements; the candidate remains experimental and uninstalled.
