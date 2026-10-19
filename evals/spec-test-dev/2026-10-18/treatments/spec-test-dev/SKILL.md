---
name: spec-test-dev
description: Implement bounded behavior changes and regression fixes through specification, tests, and implementation; preserve covered behavior during refactoring. Excludes planning-only work, diagnosis-only work, independent review, and routine prose edits.
---

# Spec-test-dev

Make the affected behavior explicit, demonstrate that tests detect the relevant defect, then implement the smallest coherent change. This is a development method, not requirements, acceptance, or release authority. Follow the project's conventions and controlling instructions; no companion skill or separate role is required.

## Establish the behavioral contract

Read the authorized request, current public contract, relevant tests, and affected implementation. Before implementing changed behavior, establish its relevant inputs, outputs, errors, side effects, invariants, and exclusions. Reuse an adequate specification in its existing home; extend only the affected contract. A signature alone is insufficient when behavior remains unspecified.

Use the project's natural form: interface documentation, docstrings, API schemas, or acceptance scenarios. A small change may need only an existing contract and a clarification. Do not impose a separate specification file, interface format, language, framework, or spec/test/code commit sequence.

Distinguish authorized requirements from material assumptions. State the evidence and uncertainty behind an inferred behavior; resolve consequential product ambiguity with its owner while continuing independent authorized work. Ordinary implementation choices within scope need no new approval. Do not redefine requirements to match an implementation or a convenient test result.

A bounded exploratory probe may answer a specific uncertainty before the specification is settled. Keep its effects isolated and its purpose explicit. Preserve useful work, but treat the probe as investigation until the behavior and supporting tests are established; it is not verified delivery.

## Derive tests from the contract

Reuse adequate tests and add coverage for meaningful gaps. Before writing an assertion, identify the realistic defect it should catch: a wrong branch, incorrect result, missed boundary, missing validation, or lost side effect. Choose tests by behavioral risk, not by a quota per function.

Derive expectations independently from the requirements, using hand-checked fixtures, explicit expected values, or independently justified properties. Do not calculate the expected answer with the implementation under test or its answer-producing helpers, or copy its algorithm into the test oracle.

Exercise observable behavior and the relevant real effects, such as emitted output, persisted state, or absence of a prohibited write. Source-text matching, incidental wording, private structure, and the presence of a mock do not establish that behavior. Exact text, arguments, counts, or ordering are useful assertions when the public contract depends on them.

When a double is needed, understand the real dependency's effects and replace the external or costly boundary without hiding the behavior being checked. Give it realistic inputs and responses; distinguish success, failure, and malformed cases where relevant. Check required boundary interactions without merely confirming that the double returns its configured answer. Keep test-only helpers in test code; prefer a real component when mock machinery obscures the contract.

## Observe failure, then implement

For new behavior or a regression repair, run the focused test before implementing the change and inspect its intended behavioral failure. A missing import, syntax error, unavailable environment, or missing symbol is a setup failure, not this evidence. Minimal runnable scaffolding is allowed to reach the behavioral assertion; repair setup problems and rerun before implementing the behavior.

If a test passes unexpectedly, determine whether the behavior already exists or the test misses the defect. Strengthen an inadequate test to expose the specified gap; preserve an adequate passing test rather than weakening expectations or manufacturing a failure. Select the applicable path:

- **Behavior-preserving refactor:** Establish adequate passing coverage against the existing contract before changing the implementation. Fill meaningful coverage gaps first; no artificial failing test is required.
- **Tests added to existing implementation:** Preserve useful code and tests. When detection evidence is missing, demonstrate it with a representative faulty case or mutation in an isolated disposable copy or controlled test state. Confirm the test fails for the intended reason, remove the injected fault, and check the intended implementation again. Never destroy useful work to recreate a test-first history. If a safe demonstration is unavailable, disclose that limit rather than claiming an observed failure.

Implement the smallest coherent solution satisfying the contract, rather than special-casing only the visible test inputs. Refactor within scope while keeping the specified behavior protected. Repeat this loop for the next bounded behavior; preserve unrelated work and avoid speculative capabilities.

## Check and report the result

Run affected checks and all project-required checks, including required suite or build commands. A focused passing test does not replace a failing or unrun required check. Follow the existing completion and review rules without adding a separate completion process.

Fix attributable failures within scope and retain adverse evidence, including unrelated failures and unavailable checks. Report the behavior changed, actual checks and outcomes, meaningful failure evidence or applicable exception, coverage limits, and remaining work. Distinguish readiness for review from any acceptance or release decision owned elsewhere.
