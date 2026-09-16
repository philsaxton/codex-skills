# Disposition: retain the hold

Date: 2026-09-16. Issue: [#1](https://github.com/philsaxton/codex-skills/issues/1).

The local evaluation is complete. Do not ship or activate a standalone `implementer` skill on this evidence. The compact candidate produced no distinct material improvement over ordinary Astra behavior or the narrower provenance correction across the tested software, configuration, and documentation cases. Preserve both treatments as experimental inputs. No existing role needs a new correction based on these trials.

The user approved the prepared issue update, merge, and push in a follow-up on 2026-09-16, resolving the initial automatic approval review block. This authorizes publishing the evaluation and contract-author refinements; the experimental implementer remains uninstalled.

## Observed comparison

Each cell represents one fresh context with actual edits. Host dispatch explicitly selected `gpt-6-astra`, medium reasoning, `fork_turns: none`. Exact prompts, candidate hashes, and all twelve agent identities are in [dispatch.json](dispatch.json). The candidate is the exact file at [treatments/implementer/SKILL.md](treatments/implementer/SKILL.md), not an installed skill.

| Case | Baseline | Narrow correction | Compact candidate |
|---|---|---|---|
| Accepted TSV exporter change | Registry extension only; 3 tests pass; Python 3.12 docs; release check unavailable (77); independent acceptance preserved. | Same substantive implementation, coverage, version choice, and handoff. Explicitly explains LF reuse as an implementation inference. | Same substantive implementation, coverage, version choice, and handoff. |
| No-contract staging configuration | Chooses info based on support's normal investigation level; preserves health logs, retention, access, and production; schema passes; runtime effect unmeasured. | Same configuration. More explicit provisional wording, rollback advice, and questions for possible later policy changes; no demonstrated improvement in the delivered setting. | Same configuration and evidence distinction. Adds a useful preservation assertion; no material decision difference. |
| No-contract operator quickstart | Correct 2.4 commands, approval ID and policy link; labels observed rollout/timings as observations rather than requirements. | Same substantive instructions; more source links and policy-owner wording. Corrects a failed local checking script and retains its failure in the evidence. | Same substantive instructions and authority boundaries; examples and link verified. |

All nine runs pass the exercised scope, provenance, verification, and handoff criteria. This does not mean every proposed capability was tested. In particular, suitable library adoption versus justified custom implementation was not exercised: software reused the installed standard library and an existing project extension point. Security/licensing and package-adoption tradeoffs remain untested. The newer-runtime proposal was correctly left outside scope, but this is not evidence about difficult real API migrations.

Read the actual changed files, handoffs, and check records in [baseline.json](results/baseline.json), [narrow.json](results/narrow.json), and [candidate.json](results/candidate.json). These include before/after hashes and patches. The parent reran each software suite and configuration validator, checked documentation command grammar and local links, and byte-compared unaffected files against frozen inputs. No unauthorized source edits or deletions were found. All three software release checks independently returned 77; no release or acceptance was claimed.

The preserved software fixture fails its TSV round-trip test before the change with `KeyError: 'tsv'`, and each resulting implementation passes all three tests. Existing tests were adequate and remained unchanged. The narrow documentation run first failed because its checking script did not parse indented Markdown fences; it corrected the script and reran successfully. This is a verification-script failure, not a product defect or a reason to weaken criteria.

## Trigger boundaries and handoffs

Three fresh boundary runs received the candidate's catalog description and an optional path to its body. Planning produced a proposal without editing the exporter. Independent contract review reported findings without rewriting the contract. The trivial edit changed only the requested spelling. All three declined to load the candidate. See [boundary.json](results/boundary.json).

These are explicit catalog-selection probes, not automatic host-discovery tests. Positive trials force-loaded their treatment to compare behavior. Automatic selection and performance in other host configurations remain unverified; activation is not warranted.

The experimental candidate was checked against current `contract-author`, `contract-reviewer`, and `coordinator` handoffs. It neither requires those skills nor inherits their acceptance authority, and it routes consequential unresolved decisions without taking requirements authorship. No handoff interface or existing role was changed. Pre-existing edits to `contract-author/SKILL.md` were preserved.

## Validation and provenance

- Skill Creator's installed `quick_validate.py` passes for the candidate. Initial attempts could not import PyYAML in the default and bundled Python environments. The successful run used an existing cached PyYAML package through process-local `PYTHONPATH`; no dependency was installed or configuration changed.
- The existing `tests/test-link-skills.sh` integration test passes with temporary output confined to this task's scratch directory. The candidate is nested beneath `evals/`, so it does not change the top-level installation inventory or active support links. No helper/interface changed, so unrelated Python helper suites were not rerun.
- Frozen fixture hashes remain unchanged. Relative evidence links and JSON records were checked. Whitespace checks passed for tracked changes; new text files were checked separately.
- After all evaluators completed, full run directories were retained under workspace `artifacts/implementer-eval-20260916/` and byte-verified against scratch. The named `tmp/implementer-eval-20260916/` task was inspected, marked complete, previewed, and removed with the installed scratch helper. The outer workspace remained clean; application edits were uncommitted at the evaluation handoff and subsequently authorized for merge and push.
- The original 2026-08-25 task's final evidence report was recovered read-only from task `01a03c1c-cbfb-7531-a2d4-71960d7ed7c8`. It reports Terra at medium reasoning with tools/edits prohibited in its individual scenarios. This explains why that evidence cannot establish current Astra artifact behavior. The earlier child transcripts/backend identities were not independently revalidated. The recovered report is retained privately under `artifacts/implementer-eval-20260916/historical-final.json` in the workspace.
- Guidance was informed by the plan's linked official [Astra skills article](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and the installed Skill Creator instructions. The experiment's outcomes, not that guidance alone, determine this hold.

## Limits and next condition

This is exploratory evidence from small synthetic fixtures, one run per condition. Shared host instructions already cover much proposed guidance; agents are fresh-context but use a shared filesystem with instructed read boundaries. The parent authored and scored the fixtures and candidate, so scoring is not independent acceptance. Preserved evaluator check records are self-reports, supplemented by the parent's artifact checks; a complete independent audit of every tool call is not claimed. No result establishes a general success rate or a cross-model conclusion.

Reopen implementation when realistic implementation failures demonstrate a portable decision gap beyond ordinary behavior and a narrow correction. Add those raw cases, repeat fresh comparisons, and retain only guidance with distinct benefit while preserving scope, permissions, required checks, and independent acceptance. No further approval, permission relaxation, or release gate is introduced by this disposition. The backlog remains open for that evidence. Publishing these findings does not activate the experimental skill.
