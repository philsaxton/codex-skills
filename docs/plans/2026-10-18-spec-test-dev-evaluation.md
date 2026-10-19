# Spec-test-dev evaluation plan

Status: experimental candidate prepared, 2026-10-18; adoption evaluation and
activation remain pending. The initial planning change recorded this design
only. The candidate now lives at
[evals/spec-test-dev/2026-10-18/treatments/spec-test-dev/SKILL.md](../../evals/spec-test-dev/2026-10-18/treatments/spec-test-dev/SKILL.md),
outside active discovery. Preparation does not execute the comparison or change
an active installation. See the [candidate backlog](../../FUTURE_SKILLS.md#spec-test-dev).

## Decision and scope

Evaluate a narrow, language-neutral development skill with the working name
`spec-test-dev`: specification → tests → implementation for one authorized
behavior change. Python is the first trial environment, chosen to test transfer
beyond ACKS's OCaml interfaces. It is not part of the skill's trigger, required
toolchain, documentation format, or testing policy. A Python result alone cannot
establish effectiveness across languages.

The candidate may replace Superpowers `test-driven-development`; normal use
should not require loading both. This decision includes retaining useful test
design guidance from its `writing-good-tests.md` reference. It does not replace
`systematic-debugging`, completion guidance, contract authorship, application
verification, or the implementer role. The broad
[implementer proposal remains on hold](../../FUTURE_SKILLS.md#implementer).

ACKS motivates the hypothesis, not a causal conclusion. Its July 21 specification,
test, and implementation commits (`0346032`, `4479904`, `491b218`) and July 22
test-expectation repair (`2271d08`) precede its August 29 project activation of
Superpowers (`0545961`). Existing project requirements and independent review
are plausible contributors. The earlier
[implementer evaluation](../../evals/implementer/2026-09-16/DISPOSITION.md)
did not test this ordered method. The
[completion comparison](../../evals/verification-completion/2026-10-10/results.md)
does not establish its value either.

## Candidate prepared for evaluation

Keep the experimental entry point self-contained and focused on these decisions:

1. Read the authorized requirements and current public contract. Establish or
   update the affected behavior, including relevant inputs, outputs, errors,
   side effects, invariants and exclusions, before implementing it. Reuse an
   adequate specification in its existing home. Label material assumptions and
   route unresolved product decisions without inventing authority.
2. Derive tests from those requirements with independently checked expectations.
   Name the realistic defect each test detects. Observe the intended behavioral
   failure before implementing new behavior or a fix. Minimal runnable scaffolding
   is allowed; import, syntax and environment failures are not behavioral RED.
3. Implement the smallest coherent change and refactor with the tests protecting
   the specified behavior. Keep meaningful behavior real when using doubles.
   Run affected and project-required checks; preserve adverse results and report
   coverage limits and remaining work.

Use each project's conventions: interface documentation, signatures and
docstrings, API schemas, or acceptance scenarios. No mandatory `.mli`, `.pyi`,
`Protocol`, framework, separate specification file, test-per-function rule, or
spec/test/code commit choreography. A small change may need only an existing
contract and a docstring correction. A larger change may need shared API or
feature documentation; do not duplicate its authority across documents.

A behavior-preserving refactor establishes adequate passing coverage against
the existing contract. It need not manufacture a failure. A bounded exploratory
probe may settle uncertainty before the specification; it is not verified
delivery. Tests added to existing implementation should demonstrate detection
through a safe isolated faulty case when useful, without destroying useful work.
The method neither rewrites requirements to match output nor requires permission
for ordinary choices already within the assignment.

Use the candidate for substantive behavior implementation and regression fixes.
Planning-only, diagnosis-only, independent review and routine prose edits should
not activate it. Requirements and scope stay with their existing owner; the skill
may elaborate an implementation-facing contract only within that authority.

## Comparison and setup

Compare complete working configurations. Freeze source revisions, candidate and
reference bytes, task inputs, starting repositories, required commands, host,
model/settings as observable, tools, permissions, and per-run limits before
dispatch. Use the same host-selected model and settings throughout a comparison;
record unavailable identity details rather than inferring them from self-reports.

| Arm | Development guidance | Question |
| --- | --- | --- |
| A: ordinary development | Common project/host guidance; neither target skill | Does the candidate add useful behavior beyond the normal setup? |
| B: Superpowers TDD | A plus a pinned TDD skill and its test-design reference | How well does the existing alternative perform? |
| C: spec-test-dev | A plus the frozen experimental candidate; no Superpowers TDD | Does the narrower replacement preserve or improve outcomes? |

Hold completion, review and debugging guidance constant. Keep any required
companions readable, and inventory direct references that would load TDD into
A or C. Use explicit, recorded routing for those references without changing
vendor files. If equivalent functioning setups cannot be established, report
that limitation before interpreting differences. Do not combine this trial with
the proposed completion-rule migration or count unexpected skill loading as a
clean result. Preserve contaminated runs and their cause.

Initial trials explicitly load B or C to assess the method. Their task requests
are otherwise identical and contain complete behavioral requirements without
instructing every arm to follow the candidate sequence. Workers receive neither
this plan, other treatments, private checker answers, nor prior run conclusions.
Use fresh contexts and isolated copies; preserve the real ACKS installation.

## First pilot: Python fixtures

Prepare three small realistic tasks with existing project conventions, using
the available pinned Python/test environment. These are proposed fixtures, not
claims of observed defects. Freeze exact requirements and checkers before runs.
Freeze the scoring rubric, quality dimensions and cost measures before the
pilot as well; changing them requires a new comparison version.

| Case | Assignment and pressure | Observable result |
| --- | --- | --- |
| P1: new stateful behavior | Add a bounded batch import to a small SQLite-backed application. Requirements specify ordering, duplicate handling and no writes when a later row is invalid; existing interface documentation needs the extension. | Specification resolves the public boundary; tests exercise actual stored state, including late failure; implementation preserves the transaction requirement and unrelated data. |
| P2: regression with an adequate specification | Repair expiry handling at an exact boundary in a library with an explicit clock input and an existing documented contract. | Reuses the contract, reproduces the boundary failure, checks adjacent values and invalid inputs, then repairs it without introducing real-time flakiness or unnecessary interface machinery. |
| P3: misleading green tests | Extend a small CLI export within stated file/output and error contracts. Starting tests over-mock the writer or derive expectations from production helpers. | Tests independently check actual output, exit behavior and relevant side effects; realistic wrong-branch, missing-write or incorrect-output mutations are detected. |

Run one fresh instance per arm per case first: nine implementation runs. This
pilot diagnoses setup and method problems and is not an adoption result. If
comparative benefit is plausible and there is no unresolved critical problem,
extend the frozen comparison to three runs per arm per case, for 27 total.
Record all outcomes, including blocked and unsuccessful runs. A treatment or
fixture change starts a new version and fresh matched comparisons; never retain
only favorable runs. Fix runtime/token caps and an infrastructure-retry policy
before dispatch, and retain any intervention and original failed attempt.

## Independent assessment

Author acceptance checks from the public requirements before examining candidate
outputs. Withheld cases must vary those requirements, not introduce secret ones.
Calibrate checks against a known correct implementation and representative
incorrect implementations. An assessor separate from candidate authorship
examines artifacts and raw execution evidence; conceal arm labels where practical
and disclose exposure. Do not score an agent's declaration of compliance as proof.

| Dimension | Evidence |
| --- | --- |
| Correctness and preservation | Independent behavioral checks, existing required checks, allowed changes and preservation of unrelated state. |
| Test quality | Worker tests detect predeclared realistic mutations on isolated copies; expectations do not reuse the implementation's answer; actual behavior and side effects remain exercised. |
| Specification and sequence | Recorded file versions and tool events show an adequate behavioral contract before the corresponding implementation and meaningful red/green where applicable. Existing adequate contracts count; number of documents or commits does not. |
| Maintainability and scope | Uses project conventions and existing boundaries; avoids speculative abstractions, duplicate contracts and language-specific scaffolding without a need. |
| Reporting and cost | Claims match actual runs and limits. Record failures, unavailable checks, interruptions, test reruns, elapsed time and tokens when exposed, separately from quality. |

For each criterion record pass, fail, blocked or inconclusive with evidence.
Missing sequence evidence is inconclusive, not reconstructed TDD history. Keep
quality and cost separate; lower cost cannot compensate for incorrect behavior,
weakened requirements, lost work or unsupported completion claims.

## Selection boundaries and language transfer

After a promising explicit-use comparison, test ordinary selection in the
intended host. Verify actual availability and reads, not just link presence.
Include a bounded feature, a bug fix, a behavior-preserving refactor with adequate
tests, a prose-only edit, a diagnosis-only request and an independent review.
The refactor may use the method's preservation guidance without inventing RED;
the last three should not become implementation tasks. Record real startup
evidence separately from simulated skill-catalog probes.

Before general-purpose activation, run a small transfer check in a second
language, selected from an intended consuming project with an available
toolchain. Keep the candidate text unchanged and use that project's natural
specification and testing conventions. Compare the candidate with the retained
alternative on a behavior change and an adequate-coverage refactor, with three
fresh runs each. Look for forced Python idioms, unnecessary interface files,
duplicated specifications and weaker failure detection. Python pilot success
does not waive this check or prove universal language support.

## Decision and later activation

- **Adopt candidate for a bounded rollout:** All deciding C runs satisfy the
  published behavior, preservation, required-check and truthful-reporting
  criteria. Across at least two different Python cases, C improves a predeclared
  quality dimension over A in at least two of its three runs and either improves
  on B or preserves B's quality with a repeatable reduction in unnecessary work.
  Apply the frozen rubric and report every run in each arm; strict sequence
  adherence alone is not an outcome benefit. Resolve material adverse findings and pass
  selection and second-language checks before a general-purpose activation.
- **Revise:** A concrete correctable failure justifies a narrower treatment;
  retain the original results and rerun affected matched cases under a new
  version. Do not weaken requirements to secure a favorable result.
- **Hold:** No distinct benefit, unclear evidence, an unresolved quality or
  delivery regression, or unavailable transfer evidence supports continued use
  of the existing setup. Small samples support only scoped conclusions.

Replacement is permitted in principle, not applied by this plan. A later
activation changes selected links and direct TDD references together, validates
the intended host in a fresh session, and retains the previous configuration for
rollback. Check references from systematic debugging, coordinator assignments
and project handoffs; keep debugging and completion guidance available. Do not
ship two competing default instructions for the same development loop or edit
shared vendor contents as a workaround. Review the coordinator's affected skill
selection and handoffs in the same implementation change; no new role is needed.

## Ownership and retained outputs

This repository owns the portable candidate and this adoption plan. Prepare any
experimental candidate outside active discovery until a disposition is reached.
The independent `agent-evals` application owns reusable evaluation fixtures,
checkers, runner tooling and evaluation-specific helper skills under its own
instructions. Use explicit subject, fixture and output paths; no sibling checkout
or new general evaluation framework is a prerequisite of the skill.

Retain raw runs, snapshots, commands and output, treatment identities, actual
skill reads, independent findings, interventions and the final disposition in the
configured ignored evidence location. Keep private project material out of
portable fixtures. Publish only appropriate source-safe summaries with the
candidate's recorded identity and limits. Comparative evaluation, installation
and changes to ACKS remain future work; candidate preparation does not authorize
those steps.
