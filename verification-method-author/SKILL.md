---
name: verification-method-author
description: Use when a demonstrated coverage gap or method drift requires creating, updating, validating, or retiring a reusable application verification script, fixture, or manual procedure. Also supports direct method-maintenance requests.
---

# Verification Method Author

Preserve the smallest useful way to check a stated requirement so another reviewer can run it without the original conversation. Own the method and its validation evidence. The caller retains the implementation verdict; the requirement owner retains the definition of success.

AGENTS.md and current authorization remain authoritative. Work within the permitted verification artifacts. Do not repair product code, change requirements, install tools, or publish as an incidental part of authoring a method. A read-only assignment permits findings and a proposal, not file edits.

## Establish the gap

Read the governing request or contract, relevant application state, existing verification methods, and the caller's coverage gap. Preserve acceptance-criterion identifiers; otherwise reference the stated requirement directly. Use the requirements to determine expected behavior. Code helps locate behavior but cannot silently turn current output into the acceptance criterion.

Distinguish an outdated method from a product regression or an unresolved requirement. Repair method drift within scope; report a product defect or route a requirement decision. Do not rewrite documentation to make broken behavior acceptable.

Prefer extending an adequate existing test, script, fixture, or runbook. Choose a focused executable check when repeatable actions and assertions help, or a manual procedure when meaningful judgment or unavailable automation makes that appropriate. Reuse project tools and startup/recovery procedures. Avoid a shared runner, extra dependency, or broad feature inventory for a local gap.

## Make the method discoverable and runnable

Follow the project's locations and documentation conventions. If no suitable discovery point exists, add a small `docs/verification/README.md` index linking to methods in their natural test, script, or documentation locations. Add entries as needed. Link existing coverage instead of duplicating it or installing a project-specific skill.

Record the following information, referencing existing authoritative material where it remains sufficient:

- Purpose, requirement references, covered behavior, and limits of the check.
- Prerequisites, inputs or fixtures, and exact commands or manual actions, including readiness and instance identification when applicable.
- Expected observations and assertions, evidence to collect and its retained location, and how to distinguish a product failure from an unavailable or failed measurement.
- Cleanup of resources created by the method, including failed attempts, without removing evidence or disturbing shared instances.

Use repository-relative instructions and explicit parameters rather than another checkout's absolute paths. Keep helpers small and composable; document their actual invocation and required tools. Do not assume a command is harmless because it is named dry-run. Confirm that the chosen test path and its side effects fit the authorized environment.

## Validate the method itself

Execute the documented procedure against a known acceptable case and a representative known failure. The expected result must come from the requirement or an independently established control, not from the output being checked. Use isolated fixtures or copies for negative controls, preserving the application under review. For a manual procedure, exercise its observations and decision rule on corresponding examples.

Show that the method detects the failure it is meant to catch. Exercise relevant unavailable-prerequisite or measurement-error behavior so an unsuccessful check cannot appear to pass. Test cleanup after failed attempts and verify that collected evidence still exists. Re-run the affected validation after changing the method.

Record what was actually exercised. An unrun procedure is a draft. If a required control cannot be exercised, return that validation gap explicitly; do not claim the method fully validated or use its existence to declare the application verified. Suitable current validation results may also serve the caller's application check without another identical run.

## Maintain and hand off

Keep method sources with the project and use its existing version control; no separate version scheme is required. Identify the evaluated method and application state, including relevant uncommitted changes, inputs, and environment in the run evidence. Keep that evidence separate from the reusable instructions.

Review affected methods when requirements, application behavior, tools, or prerequisites change. Retire an obsolete method by updating active references and recording its replacement or the remaining coverage gap. Preserve needed historical evidence and the project's history; removal of a method does not remove its requirement.

Return the method and discovery locations, requirement coverage, changes made, validation commands or actions and results, evidence locations, cleanup result, and limitations. Keep the handoff concise and use any project-defined format. The verifier assesses this material before relying on it; authoring or maintaining a method is not implementation acceptance.
