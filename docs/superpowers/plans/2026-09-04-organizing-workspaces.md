# Set Up the Garage — Skill Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking. This document plans skill authoring; it does not execute workspace setup or migrate live projects.

**Goal:** Create a concise skill that establishes a garage around independent application repositories, then validate an existing-workspace mode against separate migration evidence.

**Architecture:** One portable skill owns the separation of application code, generated work, and workspace support. The garage is the agent workspace and has a thin Git repository; contained applications remain independently tracked and portable. Workspace-specific choices belong in local documentation.

**Tech Stack:** Markdown skill instructions, Git, disposable filesystem fixtures, and verified Codex documentation.

**Spec:** [Agreed design](../specs/2026-09-04-organizing-workspaces-design.md).

**Naming and loading decision:** Implement as `workspace-setup`, with display name “Set up the garage,” following the recommendation accepted for implementation. Keep one discoverable entry point that selects new setup or existing-workspace restructuring, loading `references/refactoring.md` only for the latter. This is conditional reference loading, not a dependency on nested-skill discovery.

## Global constraints

- Leave application space empty unless the user requests a starter repository.
- Keep application histories and origins independent of the garage index.
- Keep directory names, tool selections, installation mechanisms, and retention policies local to each workspace.
- Do not create supporting scripts, references, or assets without demonstrated need.
- Preserve existing user work and authorization boundaries.
- Do not claim instruction discovery or sandbox behavior without verification.
- Do not migrate live projects as part of skill validation.

## Task 1: Establish behavioral evidence and platform facts

**Files:** Create `docs/evidence/2026-09-04-organizing-workspaces-validation.md` during execution.

**Consumes:** The design and the two source examples it identifies.
**Produces:** A scenario ledger with observed baseline decisions, verified platform facts, and remaining uncertainty.

- [x] Read the design, repository instructions, skill-creator guidance, and current openai-docs guidance.
- [x] Verify workspace startup, ancestor instructions, skill discovery and session refresh, and sandbox permissions. Record source locations and separate verified behavior from assumptions.
- [x] Prepare disposable scenarios described below; keep generated fixture files outside this repository.
- [ ] Run baseline attempts without the proposed skill. Record actual outcomes against the criteria, including cases where ordinary behavior already succeeds.
- [ ] Identify the smallest useful guidance supported by observed gaps. If there is no distinct benefit, record that finding before expanding the skill.

| Scenario prompt and fixture | Observable criteria |
| --- | --- |
| “Prepare this empty directory as my agent workspace; I will clone apps later.” Empty temporary directory. | Minimal garage, explicit root tracking policy, no invented application or remote, local domain map. |
| “Set up a garage for these two independent tools.” Two tiny repositories with different output configuration conventions. | Both retain independent histories; root index excludes their files and output; no forced universal output schema. |
| “Organize this application workspace.” An app includes a documented, supported MCP endpoint and local development-agent instructions. | Product interface stays with app; local development governance is classified separately. |
| “Add a small feature to this existing app.” An otherwise ordinary app fixture. | Does not initiate workspace restructuring. |

## Task 2: Author and validate new-workspace setup

**Files:** Create `workspace-setup/SKILL.md`, `workspace-setup/agents/openai.yaml`, `workspace-setup/scripts/init_workspace.py`, and `tests/test_workspace_setup.py`; update the validation ledger.

**Consumes:** Task 1 evidence and verified platform constraints.
**Produces:** A skill supporting new-workspace setup with demonstrated Git and portability behavior.

- [x] Write frontmatter with the working name and a narrow setup trigger. Structure the body around domain classification, minimal setup, ownership verification, and the completion receipt from the design.
- [ ] Implement the user-requested deterministic scaffold with tests first. `python3 workspace-setup/scripts/init_workspace.py TARGET` previews without writing; `--apply` creates the default empty garage described in the design. Exercise real Git behavior, collision/refusal preservation, ancestor repository ownership, symlink refusal, reruns, and paths with spaces. Do not stage, commit, add remotes, or create applications. Use `python3 -m unittest discover -s tests -p test_workspace_setup.py` to verify.
- [ ] Apply the naming decision consistently. Front-load workspace setup and domain separation in the description; retain “garage” as the metaphor. If a distinct display name is chosen, add `agents/openai.yaml` using the skill-creator metadata guidance. Test natural requests such as “prepare an agent workspace” and “set up the garage” against actual selection behavior.
- [x] Describe default-deny root tracking without copying vending-specific allowlists. Explain that existing tracked files require separate inspection and that ignore rules do not grant or restrict filesystem permission.
- [x] Encode the empty-application default, configurable artifact destinations, application documentation handoff, and distinction between product interfaces and local agent support.
- [ ] Exercise the skill on fresh versions of the setup fixtures. Inspect `git ls-files`, `git status --short`, and `git check-ignore -v` for representative application, artifact, and governance paths. Expect only selected garage files in the root index.
- [x] Verify each sample application in a separate checkout outside the garage using its documented invocation. Expect no dependence on garage-only files or absolute paths.
- [x] Run `python3 /Users/phil-mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py workspace-setup` from this repository. This is the current authoring environment's validator path, not a requirement to embed in the skill.
- [x] Record observed results and correct only demonstrated gaps. Do not substitute prose matching for behavioral validation.

## Task 3: Qualify the existing-workspace mode

**Files:** Modify `workspace-setup/SKILL.md` and create `workspace-setup/references/refactoring.md` only if validation supports this mode; update the validation ledger. Apply the final identifier to both paths if renamed.

**Consumes:** Validated setup behavior and a new migration fixture.
**Produces:** Either a validated restructuring mode or a documented deferral with setup-only discovery text.

- [x] Create a temporary workspace containing an independent app, tracked and ignored reports, a report consumer referencing the old location, development instructions, and an unrelated dirty file. Record initial content hashes and Git state.
- [x] Test a planning-only request. Expect a domain inventory and migration map without moving files, changing the index, or modifying the unrelated dirty file.
- [x] Test an explicitly authorized migration in a fresh copy. Require preserved report contents, an updated producer output setting and consumer reference, unchanged application history/origin, and successful producer-to-consumer execution.
- [x] Exercise a tracked-artifact case: confirm adding ignore rules alone is not reported as removing artifacts from the index. Any index changes must match the authorized migration.
- [x] Add only migration guidance supported by the exercise: inspect before moving, trace path consumers, retain recovery information, and verify the resulting boundaries. If these outcomes cannot be verified, leave this mode out of the trigger and record the limitation.
- [ ] Put the migration procedure in `references/refactoring.md` and link it from an explicit mode-selection instruction in `SKILL.md`. Keep common domain boundaries in the entry point. Verify that a new-workspace run needs no migration reference, while an authorized restructuring run reads it. An existing project must not trigger unrequested moves merely because it is detected.

## Task 4: Integrate and review

**Files:** Modify `FUTURE_SKILLS.md`; finalize the skill and validation ledger.

**Consumes:** The actual support and validation status from Tasks 2–3.
**Produces:** A consistent skill and backlog entry with accurate scope and evidence.

- [x] Update the workspace integrity and hygiene candidate to distinguish workspace organization from the separate trust-hygiene idea. Link the new skill only after it exists and describe only verified modes.
- [x] Check the skill remains standalone and does not turn specific directory names, repository manifests, or tool installations into mandatory cross-project policy.
- [x] Run the skill validator again if instructions changed, then `git diff --check`. Review the complete diff and confirm no unrelated files were changed.
- [x] Deliver the skill link, observed validation results, and any remaining limitations. Installation, live migration, publishing, and remote changes are separate actions requiring applicable user authorization.

## Plan review

The design's garage boundary, independent applications, empty-start default, domain classification, configurable outputs, and local policy are covered in Task 2. Platform uncertainty and cross-project evidence are covered in Task 1. Migration and recovery are covered in Task 3. Discovery scope and backlog consistency are covered in Task 4. Implementation is complete with the validation limits recorded below.


## Execution outcome

Implemented as `workspace-setup`. Nine real CLI/Git tests and the existing skill-linking checks pass; metadata validates. A direct migration smoke check verifies the documented data and repository preservation pattern. Independent baseline, implicit-selection/reference-loading exercises, and independent review did not return reviewable reports within the bounded run and are not claimed complete. The scaffold test file was written before its implementation by the worker, but no worker RED report was returned, so a witnessed RED cycle is not claimed. Unchecked items that include those assertions remain open; they do not imply the script or reference is missing. See the [validation record](../../evidence/2026-09-04-organizing-workspaces-validation.md) for observed commands and limitations.

## Existing-project follow-up

The user authorized the next stage in a fork and requested a separate worktree. The refactoring task moved with its uncommitted state to the Codex worktree at `/Users/phil-mac/.codex/worktrees/8733/skills`. The user clarified that an application-root launch must establish an enclosing garage containing the intact repository, with the required access and restart/handoff accounted for.

- [x] Exercise the existing reference independently on application-root, interrupted-migration, and shared-suite planning cases; verify no mutations.
- [x] Clarify local-support transfer, shared-repository ownership, staged-content preservation, and retry reconciliation in the reference.
- [x] Specify the enclosing-garage transition: exact paths, preservation evidence, permission for both paths, a stable relocation context, handoff state, and post-relocation verification.
- [x] Mechanically verify ordinary repository relocation into a scaffolded enclosing garage while preserving identity, index, dirty state, and files.
- [x] Execute a fresh independent two-application migration and verify its resulting artifacts against pre-migration evidence, including current standalone application snapshots.
- [x] Recheck the original application-root planning case with a fresh independent agent and the revised reference.
- [x] Validate the skill and confirm the setup script, its tests, UI metadata, and entry point remain unchanged.

See [existing-workspace validation](../../evidence/2026-09-04-workspace-refactoring-validation.md) for outcomes and limits. Fresh-host implicit selection, active-writer cutover, linked-worktree/submodule relocation, and live application-root handoff are not claimed tested. Earlier setup-stage unchecked assertions remain historical limitations rather than being silently marked complete by different tests.

## Final follow-up decisions

- [x] Record Workspace trust review as a narrow future standalone candidate; do not implement it or make refactoring depend on it.
- [x] Keep the current trust check limited to migration changes affecting trusted executable inputs or editability, distinguishing sandboxed execution from standing outside-sandbox command approval.
- [x] Preserve mixed instruction requirements by purpose and save a durable migration contract before moving an active directory, with optional `contract-author` assistance and a direct standalone fallback.
- [x] Require stable session context and effective access to both paths before relocation; avoid a redundant scaffold approval gate within already authorized setup scope.

Validation for these final instruction changes is recorded in the refactoring evidence record. No live migration, new trust-review implementation, merge, or push is included.

## Standalone pilot completion

- [x] Commit the validated implementation (`ee11615`) and pilot preparation record (`fdab8d3`).
- [x] Execute the disposable migration in a stable enclosing-project session, preserving application identity, staged/working data, recovery evidence, and standalone product behavior.
- [x] Relocate the completed pilot to a standalone project and verify a fresh garage-root session received the root instructions and workspace-setup metadata at startup.
- [x] Reconcile completed migration state without repeating it; verify the receiving session's ordinary write access and retain its protected-control/sibling access limits.
- [x] Review all 43 recorded assertions and independently match the current Git index hashes against receiving-session evidence.

The standalone pilot now lives at `/Users/phil-mac/Projects/garage-handoff-pilot/garage`. Its `STARTUP-RESULT.md` and the [repository validation record](../../evidence/2026-09-04-workspace-refactoring-validation.md) document the completed startup check. The user explicitly invoked the skill; automatic selection without that invocation remains untested. Earlier no-skill comparison, witnessed RED-cycle, broader routing, linked-worktree/submodule, active-writer and narrower-permission relocation assertions remain limitations. Implementation and the authorized pilot are complete; these results do not claim those additional tests passed.
