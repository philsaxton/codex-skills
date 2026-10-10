# Coordinator role-menu validation

Date: 2026-10-09, America/New_York. Source base: `5526d2473e32e412b79f0bbca778f8b7e60691e6`. Implementation branch: `codex/coordinator-role-menu`.

The initially evaluated candidate adds a five-role menu, skill selection and explicit child-loading instructions, and a skill-aware handoff field. Contributor guidance now describes one directory per skill and requires reviewing affected menu entries and handoffs as skills change. Existing contract-author, contract-reviewer, and solution-design entrypoints are byte-identical to the base. No new shipped skill or runtime registry was added. The later review revision is recorded below; the original runs and hashes describe the earlier snapshots.

## Initial inputs and execution

The original [procedure and criteria](README.md) and [fixtures](fixtures/catalog.md) were written before evaluation. Four fresh evaluator contexts received separate copies of the same fixture package and supplied role skills, with the selected coordinator version. They received no parent conversation, scoring criteria, expected findings, or prior outcomes. The comparison request differed only in its package location; both evaluators later received the same permission to retain their response outside scratch. Current fixture files include later explanatory labels; the frozen inputs retain the exact evaluated bytes.

| Run | Coordinator SHA-256 | Execution |
|---|---|---|
| Original | `5decde59adc329585fcdfc9c15a9f0102a7716875d974c58fbe037117bb76859` | One coordinator and one fresh independent review child. |
| Initial candidate | `138c00091e00aea8fb2c1889734e756d7751b6a7743ea5aeef132d3b6697c8a4` | Same request, with its own fresh review child. |
| Routing | Same initial candidate | Four role assignments, an accepted-choice variation, and five boundary cases; proposed prompts only. |
| Extension | `110ef8e01e3f9de562470df63bc79fb97a13ff49e8a3f63422e725a689de5b48` | One added menu row and one fresh catalog-audit child. |

All evaluator and child calls used `fork_turns: none`, with model and reasoning settings inherited and no overrides. The routing cases shared one evaluator context and were treated as independent situations; they are not independent samples. The extension copy differs from the candidate by exactly its one catalog-auditor row, with identical dispatch instructions.

The 18 non-coordinator input files match across all four packages. Their aggregate SHA-256 is `f901cc3901cbc9fc07e2f3bb16e2fac2091ddba0f953f18c6ef6ebb56eb6347f`, calculated from compact, key-sorted JSON mapping package-relative paths to file SHA-256 values. Frozen copies, full manifests, exact child prompts, complete responses, and source-review receipts are retained under the caller workspace's ignored `artifacts/coordinator-role-menu-20261009/`. The retained-input map records the original scratch locations used in the transcripts.

## Initial observations

| Check | Observed result |
|---|---|
| Original multi-skill review | Selected `contract-reviewer` and `parcel-export`, instructed the fresh child to read both, and retained the child's `not ready` judgment. The child reported both reads, applied the review method, and found both positional-column and duplicate-publication contradictions. |
| Candidate multi-skill review | Also selected both skills, supplied their absolute locations and purposes, and explicitly required reading before review. Its fresh child reported both reads and returned the same material contradictions, preserving authorship and acceptance boundaries. |
| Role selection | Assigned design to `solution-design`, authorship to `contract-author`, implementation to the supplied `parcel-implementation`, and completed-work review to `completed-work-review`. The shared parcel-domain skill supported each relevant role. No experimental or absent same-named skill was assumed. |
| Conditional authorship skills | Included `solution-design` alongside author and domain skills for an unresolved writer choice within the author's authority. Omitted the design skill initially when the writer choice was already supported and accepted, retaining a return path if new evidence changed it. |
| Missing guidance | Reported the optional absent performance skill without blocking authorized export work. Kept the project-required accessibility acceptance blocked while allowing independent export work with its own prerequisites. Invented paths and installation were avoided. |
| Conflicting responsibilities | Withheld the contradictory read-only-review plus mandatory-edit assignment and routed the mismatch for resolution. Proposed separate repair ownership and fresh review without silently granting edit permission. |
| Independence and small tasks | Rejected renaming the author context as an independent reviewer. Kept a trivial spelling correction in the current context, with no unnecessary child or skill. |
| Menu extension | Selected the added catalog-auditor role and `catalog-audit` skill using unchanged dispatch guidance. Its fresh child reported reading the skill and found the conflicting names for `KIT-7` on source lines 2 and 4, without editing the catalog or claiming acceptance. |

The original coordinator already succeeded on the comparison task. These observations support the requested explicit menu and handoff behavior; they do not demonstrate a causal improvement over the baseline. Both review children also identified an invalid-input-policy gap and unverified writer evidence; those extra observations were not required to score the two protocol contradictions.

## Initial structural and consistency checks

- Skill Creator's installed `quick_validate.py` passed for the candidate and all five synthetic supporting skills. The first attempt lacked PyYAML in the default Python environment; rerunning with an existing cached PyYAML on process-local `PYTHONPATH` passed. No package was installed or environment configuration changed.
- Fixture catalog paths and local Markdown links resolved. Tracked changes passed `git diff --check`; new evaluation files were checked for whitespace separately.
- The top-level shipped skill inventory is unchanged. Existing helper and installation code is unchanged, so unrelated helper suites were not rerun.
- A separate fresh reviewer directly inspected the tracked change and all three existing role handoffs, without evaluation outcomes or sibling worktrees. It reported no material findings. This was static consistency review, not a second behavior trial.
- All four fixture packages were byte-checked against their frozen manifests after their writers stopped. Retained copies preserve the inputs and raw reports. The exact task scratch directory was inspected, marked complete, previewed, and removed with the installed scratch helper.

## Review revision

Following user review, the menu now contains only roles and their directly assigned skills. The contract-author row names only `contract-author`; its existing instruction to use `solution-design` for unresolved consequential choices remains in that skill. The shared dispatch instructions are unchanged. The extension fixture uses the corresponding two-column menu row.

The evaluation README and all five synthetic skill entrypoints now identify their evaluation-only purpose. They explain which test agents receive them, what each case checks, and that a parcel here is a fictional shipping package. These files remain nested fixtures, outside the installer's top-level skill inventory.

The revised coordinator SHA-256 is `a6610eed82f15ac44dab6988991ad585d64b071f1847bc127ad32094d22cac68`. Skill Creator validation passed for it and all five fixture skills. Local references and whitespace checks passed. The contract-author entrypoint and shipped skill inventory remain unchanged. The revised source snapshot and check receipt are retained as `revised-coordinator.md` and `review-revision-checks.json` alongside the original evidence.

No behavioral trial or independent source review was run for this intermediate revision. The observations above apply to the frozen initial candidate and fixture bytes. The following check evaluates the subsequent task-contract guide revision.

## Task-contract guide follow-up

The coordinator now provides an inline task-contract guide for starting prompts and substantive reassignments. It replaces the handoff field list with a reusable format covering the task, owner and role, objective, selected skills, authoritative inputs, scope and authority, exclusions, dependencies, expected output, observable completion criteria, and conditions for returning to the coordinator. It permits compact or project-specific formats, preserves existing specification and approval requirements, and does not require a new document or delegation for small direct tasks.

Coordinator SHA-256: `062a1dd562cccb179dc601cb42e26a2ed4484799a6f12c45dfc2fa5837ed4404`. One fresh evaluator (`/root/task_contract_trial`, `fork_turns: none`, inherited settings without overrides) received the frozen candidate, the existing fixture package, and only the request to prepare implementation and final-review assignments from cases 3 and 4 of `fixtures/roles.md`. It received no rubric or prior outcomes and did not launch workers or execute either assignment.

Both proposed prompts used the guide and carried selected skills with package-resolved paths and explicit reading instructions. The implementation prompt kept the file boundary, existing-writer constraint, and design-consultation return path. It identified the missing accepted contract, source files, tests, and writable workspace as execution prerequisites without treating the supplied proposed contract as accepted. The review prompt required a fresh independent context, direct output inspection, concrete protocol evidence, and explicit verification limits; it granted no editing or acceptance authority. Both supplied expected outputs, observable completion criteria, and blocker routing.

This is one assignment-preparation observation covering two cases in the same context. It supports the guide's use in those proposals, not actual worker execution, compact-format behavior, or general reliability. Earlier live trials were not repeated. Skill Creator validation, reference resolution, and whitespace checks passed. The three companion role skills remain unchanged. The exact request, complete response, frozen inputs, hashes, and check receipt are retained under the existing evidence directory's `task-contract-guide/` subdirectory.

## Limits

There was one live trial per coordinator variant and one extension trial. Most boundary coverage is assignment preparation rather than execution of those assignments. Child read lists are self-reports; concrete outcomes and role-specific review behavior corroborate application of the supplied guidance, but the caller did not independently audit every tool call. Fresh conversation contexts share a filesystem and rely on instructed read boundaries. Automatic startup discovery, robustness across models or projects, and real implementation performance remain untested. No installed skills, active links, support pins, merges, or publication were changed by this work.
