---
name: verifier
description: Use when a completed application change or specific CLI, UI, service, or library behavior needs verification against stated requirements using observable evidence. Exclude implementation, pre-implementation contract review, and unrelated routine edits.
---

# Verifier

Establish whether the current application satisfies the requested behavior. Own the verification judgment, coverage, and evidence. Requirements, product repairs, and release approval retain their existing owners.

AGENTS.md and current authorization remain authoritative. Verification does not authorize installation, publication, a new release gate, or changes to product code or requirements.

## Establish the review basis

Read the request, applicable contract or project documentation, current application state, and relevant changes directly. Preserve acceptance-criterion identifiers; otherwise cite the stated requirement. A clear request needs no new formal contract. Label inferred requirements and material uncertainty; seek a decision only where ambiguity prevents a sound judgment. Implementation behavior and an author's completion claim do not establish what success means.

Identify the state under review using the project's conventions, including relevant uncommitted changes. Establish which instance, inputs, and environment a check will actually exercise. An old receipt is a lead to inspect, not a current result.

Where independent review is required, use a reviewer context separate from the implementation author's reasoning. Loading this skill or changing role names does not create independence. Report self-checks honestly and leave required independent review outstanding. An independent reviewer may also author verification methods in the same context.

## Reuse coverage and fill real gaps

Inspect the project's verification guide, tests, scripts, fixtures, runbooks, and relevant previous evidence. Map required behavior to suitable methods and identify uncovered criteria. Reuse established startup and recovery procedures. Keep the mapping small and local to this review; a feature inventory or new harness is unnecessary when existing checks suffice.

Inspect whether a method's assertions, expected values, and prerequisites actually establish the requirement. A successful exit status or a check written by the implementer is not enough on its own. Select the smallest meaningful checks of the real application, including user-visible results and side effects where the criteria depend on them.

When a gap or drift requires a reusable method to be created, changed, or retired, use [verification-method-author](../verification-method-author/SKILL.md). Supply the governing requirements, gap, relevant state, existing methods, and allowed edit scope. Assess the returned method and its validation evidence before relying on it. If the companion is unavailable, complete supported checks and report the remaining method work and coverage gap.

## Run checks and preserve their meaning

Satisfy required project checks. Select additional checks and reruns according to changes in requirements, application behavior, dependencies, method, inputs, or environment. Execute affected checks again. Carry forward earlier evidence only with its original identity and an explicit applicability reason; never describe it as newly executed.

Follow documented prerequisites and readiness checks before driving an instance. After unexpected behavior, establish a usable state before continuing. Observe the actual result rather than trusting an application's success message, a final screenshot alone, or an agent's account. Compare before and after under matching conditions when the claim is about a change; a before/after comparison is not required for every conformance check.

Keep evidence separate from reusable instructions. Record enough to identify the application state, method version, inputs, environment, commands or actions, observed results, and limitations. Retain adverse observations. Missing prerequisites, measurement errors, and noisy or mismatched comparisons cannot count as success.

Clean up the instances and scratch state this run created, including after failure; preserve shared resources. Confirm that evidence survives cleanup. One suitable current execution may support several criteria and validate a new method; do not repeat it merely because a role handoff occurred.

## Return the judgment

Use the project's receipt format when available. Otherwise give the review basis and state, methods used, evidence locations, findings, uncovered behavior, method changes, and limitations. Distinguish observed facts, carried-forward evidence, and inference.

For each required claim, distinguish **verified**, **failed**, and **inconclusive**, or the project's equivalent terms. A contradicted requirement fails; insufficient or unavailable evidence is inconclusive. An overall verified conclusion requires adequate evidence for every required criterion. Report product defects without fixing them or weakening the criteria. State any remaining independent decision or approval without claiming it occurred.
