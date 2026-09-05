# Existing-workspace refactoring validation — 2026-09-04

## Scope

This extends the earlier [setup validation](2026-09-04-organizing-workspaces-validation.md). The user authorized developing the existing-project workflow and later clarified that an application-root launch should establish an enclosing garage containing the intact application repository. No live project migration is authorized or performed.

The task began as a same-directory fork and was handed off to `/Users/phil-mac/.codex/worktrees/8733/skills` on `codex/workspace-setup`. Prior uncommitted setup work and the refactoring edits arrived intact. The setup script, its tests, display metadata, and entry point were checked against recorded hashes and remain unchanged. Changes in this stage are the refactoring reference and associated design/evidence records.

## Fixtures and baseline

Disposable fixtures live at `/private/tmp/garage-refactoring-stage2-i35dpk9f`. They represent:

1. A standalone application checkout, with only its current directory writable in the planning scenario.
2. A thin garage containing an independent reporter, an interrupted migration with conflicting report copies, a supported MCP product module, an intentional test asset, and separate staged/unstaged work.
3. A suite whose component directories share one Git repository and release history.

The original reference was exercised by an independent agent in planning-only mode. The agent received the skill and fixture requests, without the design, prior findings, or saved oracle state. It chose an enclosing garage for the standalone app, retained the existing thin garage's layout, kept the shared-history suite together, and did not invent origins. It detected four distinct report versions and a producer/consumer filename mismatch (`next.json` versus `latest.json`), requiring resolution before migration. Root verification found all four Git roots' HEADs, indexes, status, and fixture file contents unchanged after the exercise.

One gap appeared: the standalone-app plan explicitly preserved its local development `AGENTS.md` inside the application as part of intact relocation, without a later transfer to garage support. The reference now distinguishes relocating the repository intact from completing domain separation. This is a current-skill baseline, not a no-skill comparison or a claim of superiority over ordinary model behavior.

## Focused changes

- Distinguish component directories within one repository from independent applications.
- Explicitly map and relocate local-only development guidance/support while retaining product interfaces and documentation.
- Add the enclosing-garage sequence, including destination choice, access for both paths, a stable relocation context, handoff information, and verification of the relocated repository and active workspace.
- Preserve distinct indexed content when changing migration-related tracking, and reconcile interrupted moves before resuming.

The latter preservation conditions were already recognized by the baseline agent. They are concise operational clarification based on the fixtures, not additional claimed baseline failures.

## Mechanical checks

The interrupted fixture's committed report contains batch 1, its index batch 2, its working copy batch 3, and the destination batch 99. An ordinary `git rm --cached` refused removal because the indexed version differed from both HEAD and the working copy; the index stayed unchanged. This demonstrates why copying only working files is insufficient preservation evidence and why a refusal must not automatically lead to force removal.

A separate relocation check copied the reporter fixture into an ordinary source checkout, ran the unchanged empty-garage scaffold for a dedicated sibling container, then relocated the whole repository from a process outside it. HEAD, branch, origin, index, dirty status, and every working file were preserved. The application Git root resolved to the new location, and the garage index excluded application contents. The result is recorded at `relocation-result.json` beneath the fixture root. This verifies ordinary repository relocation, not linked-worktree/submodule relocation or a live Codex handoff.

The 9 existing scaffold tests passed before reference changes. The bundled skill validator passed after the changes using the already cached PyYAML environment. No runtime dependencies or migration script were added.

## Independent execution

An authorized two-application migration exercise was started before the worktree handoff. The handoff ended that worker; inspection confirmed it had not changed the fixture. A fresh copy (`execution-v2`) was used for the restarted exercise, with the revised skill and raw fixture as inputs and no prior conclusions or oracle state.

The independent agent created a thin garage index containing exactly `.gitignore`, `AGENTS.md`, `README.md`, `run.sh`, and `support/producer/check.py`. It transferred the explicitly local guidance/helper from the producer, removed the migrated runtime/support paths from that application's index, added runtime ignore rules, and connected both apps through `artifacts/producer/sales.json`. It retained the original report as an ignored recovery copy. It made no commits and contacted no remotes.

Parent verification compared actual results with saved pre-migration evidence: both app HEADs/origins, product code/interfaces/docs/examples, distinct staged and working notes, relocated helper bytes, and original recovery-report bytes were preserved. The consumer repository stayed clean. The root index excluded both applications and artifacts. `run.sh` worked when invoked from outside the garage and produced the expected value, 8.

The worker corrected two test assumptions: the original runner was not executable, so it enabled execution; regenerated JSON differed in trailing whitespace, so recovery preservation was checked against the original file's hash instead of requiring byte-identical regenerated output. Parent verification separately checked semantic output and exact recovery bytes.

Current application snapshots, copied without Git metadata or runtime reports, both ran standalone outside the garage. This verifies the current deliverable's invocation rather than merely cloning the pre-migration HEAD. Snapshot path: `/private/tmp/garage-current-app-snapshots-iik4r_rp`.

## Application-root recheck

A fresh independent agent answered the same planning-only application-root request with the revised reference. Its map explicitly separated local `AGENTS.md` guidance after moving the repository intact, preserved application code/docs, identified the missing destination permission, and called for restart/handoff before relocation. It also checked the actual program and observed that the README's advertised output setting had no implementation yet, deferring output routing instead of assuming support. The fixture remained unchanged. This is a bounded recheck, not a controlled statistical comparison of models or a no-skill ablation.

## Remaining limits

These independent exercises cover three planning topologies, conflicting/interrupted output state, local-support classification, and one authorized two-app migration. The ordinary repository relocation has a separate mechanical check. Linked-worktree/submodule relocation, active-writer cutover, and a live application-root Codex restart/handoff remain untested; the reference preserves explicit checks and stops dependent actions when access or preservation cannot be established. No broader automatic-migration guarantee or live-project adoption is claimed.

## Final instruction follow-up

The user requested the narrower future Workspace trust review candidate and durable migration-contract handoff. `FUTURE_SKILLS.md` now separates implemented workspace organization from that unimplemented candidate. The reference retains only a migration-specific executable-input/editability check, without a future-skill dependency or a broad audit. Mixed `AGENTS.md` requirements are classified into product/contributor docs versus local agent governance, and the handoff contract has a direct fallback when `contract-author` is unavailable. The entry point now explicitly says setup authorization covers the scaffold while environment boundaries still apply.

This follow-up changes the entry point as well as the reference and records, superseding the earlier byte-for-byte entry-point preservation statement for this final delta. The deterministic script, its tests, and display metadata remain unchanged. Prior fixture runs are evidence for the versions they exercised; they are not presented as new executions of the final wording.

A fresh independent read-only scenario check of the final wording correctly mapped build and contributor requirements to application docs, local helper guidance to the garage, and supplied a durable contract without `contract-author`. It distinguished the unapproved/out-of-scope relocation from a separately authorized in-sandbox scaffold, required stable context and access before moving the source, and identified mutable imports/configuration beneath a standing outside-sandbox approval as the focused trust issue. This validates bounded planning decisions, not execution of a live permission transition.

Final checks: all 9 scaffold tests passed; the skill validator passed; scaffold/test/UI file hashes matched their starting identities; changed Markdown links and whitespace checked cleanly. No Workspace trust review implementation directory was created. Changes remain uncommitted in the refactoring worktree; no live project was migrated and no merge or push was performed.
