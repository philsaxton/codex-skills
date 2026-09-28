# Validation — 2026-09-27

The three fresh evaluator contexts received only their copied skill and request files. They received no parent conversation, expected behavior, sibling results, or scoring guidance. Model and reasoning settings were inherited without overrides. Each evaluator read the two supplied files and returned a response; no implementation or external action was requested or reported.

The evaluated skill's SHA-256 was `7716f28e718925d5b402b276840d1a46f97b328b414d015b81bbf6df8f5420c9`. The evaluation copies matched the source as it stood on September 27, before the opportunity refinement below. The [fixture criteria](README.md) were written before dispatch.

| Case | Observed result | Assessment |
|---|---|---|
| Planning | Recommended direct MigrateKit 3.2 use with per-file credential references. Explained why fresh authenticated connections matter to RESET ROLE, rejected duplicating migration history without a demonstrated gap, and distinguished documented fit from runtime proof. Identified failure recovery and rerun behavior for later verification. | Met the case criteria. |
| Written-plan review | Found the laptop restriction unsupported, identified the existing hosted job, and rejected the claim that one tiny untagged copy established compatibility. Proposed a bounded multipart/tag/resume check subject to authorization. Returned findings and options without rewriting the plan. | Met the case criteria. |
| Implementation consultation | Identified the invalid callback assumption and documented exclusions of the existing tools. Recommended a bounded custom decoder, retained the protected limits, and required the existing contract's review and acceptance before replacement. Named useful fixture and inspection work that could continue. Explicitly noted that an 8 KB record does not establish total memory compliance. | Met the case criteria. |

Direct consistency review confirmed that the coordinator assigns design work and includes a return path from implementation, the contract author consumes design evidence before commitment, and the contract reviewer evaluates selection evidence without taking over the choice. The shipped library has no implementer skill; the existing experimental implementer treatment was left outside this change.

All four changed skills passed the Skill Creator `quick_validate.py` frontmatter and scaffold checks. The system and bundled Python interpreters initially could not run the validator because PyYAML was absent. The successful run used an existing Python 3.12.2 environment with PyYAML; no dependency installation or environment change was needed. Whitespace checks passed for the tracked edits and new files.

These are three single-run checks with supplied fictional documentation, not a baseline comparison or evidence of automatic discovery, live tool research, real migration compatibility, or a complete multi-role workflow. No pinned installation was updated by this validation.

## Opportunity refinement — 2026-09-28

A fresh evaluator received only the revised skill and the opportunity fixture, using the same explicit-invocation procedure and inherited model settings. The evaluated skill's SHA-256 was `bcf2090f3f57af6fc34557033a90c5f1b0ac4f477cae7746f87e6572d1252dd3`. The opportunity criteria were recorded before dispatch.

The response recommended a single service with the embedded library. It compared four remaining weeks for the existing architecture, two for direct adoption including replacement and qualification, and five for retaining the old service split around the library. It explicitly rejected the eight weeks already spent as sufficient reason to continue, identified reusable work and real switching costs, and kept estimated maintenance benefits separate from observed results. It specified bounded checks of protected behavior and required the existing contract amendment review and acceptance before architecture replacement. Unaffected work could continue while the decision was resolved. This met the opportunity case criteria.

All four skills passed structural validation again, and whitespace checks passed. Direct review checked the corresponding opportunity triggers in the coordinator and contract author. The earlier three behavioral cases were not rerun against this refinement; this new single-run result does not establish general reliability or automatic discovery.

## Final wording and workspace trials — 2026-09-28

The opening was clarified to respect the user's decision-making authority while explicitly distinguishing mandatory constraints from revisable choices and surfacing evidence-backed alternatives. The final candidate's SHA-256 is `aea8e3878938f2a29ec5b6f6820c93bbc81e2f8c520266c635523e48ce31cea9`.

Two fresh Codex CLI sessions launched from a consuming workspace confirmed the installed candidate in their supplied startup inventories before reading files, then used it for read-only real-project assessments. Both compared maintained alternatives and distinguished documented capabilities from untested compatibility. One retained the application-specific service while identifying possible simplifications; the other found a migration CLI but prioritized investigating another approach. The latter comparison concentrated on fitting the existing migration design, leaving a broader redesign around the CLI unresolved.

These were explicit-invocation, single-run checks, without a baseline arm. They verify startup inventory and observed consultation behavior, not automatic selection, causal improvement, or operational compatibility. Private source fixtures, prompts, logs, and reports remain outside this portable repository. The earlier synthetic cases were not rerun against this final wording.
