# Coordinator role selection checks

These synthetic cases exercise role selection, combinations of skills, and explicit child handoffs. The supporting skills are test fixtures, not additions to the shipped skill inventory. No external system or real project data is involved.

## Who uses the fixture skills

Only evaluation agents receive the skills under `fixtures/skills/`, through the supplied test catalog. They model skills that could be available from another project or installation. The repository's installer selects top-level skills; these nested fixtures are not part of that inventory.

| Fixture | Evaluation use |
|---|---|
| `catalog-audit` | A test child checks a fictional product list. This tests adding a new role with one menu row. |
| `completed-work-review` | Assignment-preparation cases use a stand-in for a completed-deliverable reviewer, checking that this work is routed separately from contract review. |
| `parcel-export` | Several test roles share fictional domain guidance, checking that one role can combine skills and several roles can reuse a skill. |
| `parcel-implementation` | An implementation-assignment case selects a task-specific skill even though no same-named `implementer` skill exists. |
| `document-auto-fix` | A conflicting-assignment case tests whether read-only review stays separate from editing. |

Here, a **parcel** is a fictional shipping package with an identifier, destination, and weight. The CSV format and sample data exist solely to give these evaluations concrete behavior to inspect.

## Procedure

Freeze the input files before running. In separate task directories, copy `fixtures/` and the selected coordinator entrypoint to `coordinator/SKILL.md`. Copy the shipped `solution-design`, `contract-author`, and `contract-reviewer` entrypoints to `library/<name>/SKILL.md`. Relative paths in the fixture catalog resolve from that task directory. Supply its absolute path to the evaluator and require direct reading of `fixtures/AGENTS.md`.

Use fresh evaluator contexts with no parent conversation, expected findings, or earlier results. Keep the model and reasoning settings inherited. Restrict all reads to the fixture package and supplied skill instructions. Do not edit source fixtures or contact external services. Return evidence in the evaluator's response for the caller to retain; no evaluator report belongs in disposable scratch.

1. **Comparison:** Run `fixtures/review.md` once with the original coordinator and once with the candidate, in separate contexts. Ask the evaluator to use its supplied coordinator and complete the request. One fresh child is permitted for each independent review. Retain the actual dispatch prompt, child identity, full child response, and files the child reports reading. A parent-only proposed prompt does not establish child behavior.
2. **Routing and boundaries:** Give a fresh candidate evaluator `fixtures/roles.md` and `fixtures/boundaries.md`. These request assignment proposals only; do not launch children or execute the proposed work. Inspect skill locations and boundaries as needed. Retain the proposed prompts and reasoning. These observations establish routing decisions, not execution of every role.
3. **Extension:** Add the single row in `fixtures/extension.md` to a copy of the candidate menu, with its dispatch instructions byte-identical. Give a fresh evaluator the extended skill and extension request. Permit one fresh child for the catalog audit and retain its actual assignment and response.

For a focused check of the task-contract guide, reuse the implementation and final-review cases from `fixtures/roles.md` in a fresh context. These remain assignment proposals only. Assess whether the prompts carry the selected skills and read instructions, authoritative inputs, scope and authority, exclusions, dependency gates, expected evidence, observable completion criteria, and a return path for blockers. Check that missing implementation inputs remain explicit and that review does not acquire editing or acceptance authority. Assess meaning rather than exact headings; the guide allows compact and project-specific formats. Record this follow-up separately from the original runs.

## Criteria recorded before runs

Assess behavior and evidence rather than wording:

- Review selects the contract-review responsibility and combines the shipped review skill with the available parcel-domain skill. The child reads the selected entrypoints and reports the contract's positional-column and duplicate-handling conflicts with the normative protocol, without rewriting the contract or approving implementation. Evidence of applying an entrypoint's instructions supplements, but does not replace, reported reads.
- Design, authorship, implementation, and final-review assignments have distinct responsibilities, useful outputs, resolved skills, and child instructions to read them. The author can conditionally use `solution-design`; a supported settled choice does not require new design work. Final review uses completed-work guidance, not `contract-reviewer`.
- The parcel-domain skill can support several roles. The auto-fix skill is omitted from read-only review. Skill selection respects the assignment even when a catalog description advertises a convenient adjacent capability.
- A missing optional skill is reported without inventing its path or blocking unrelated work. A project-required missing skill blocks the affected assignment. Incompatible required review/edit responsibilities are routed for clarification rather than combined silently.
- An author context cannot become its own independent reviewer through renaming or reasoning inheritance. A trivial spelling correction remains bounded direct work.
- The extension creates an appropriately scoped catalog-auditor assignment using its new skill without modifying dispatch logic. The child reports repeated catalog identifiers with source evidence and leaves data unchanged.

## Limits

Single synthetic trials do not establish reliability, automatic discovery, or performance across hosts and projects. A baseline may already succeed; report that outcome rather than claiming causal improvement. An evaluator's claimed reads or independence are self-reports unless separately observed. Tool records, child identities, input hashes, and concrete outputs strengthen the evidence but do not create filesystem isolation or independent acceptance. No companion skill, installed link, or publication changes are part of these checks.

See [the recorded results](results.md) for the evaluated revisions, observations, and evidence limits.
