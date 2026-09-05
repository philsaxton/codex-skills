# Workspace setup validation — 2026-09-04

This is the initial setup-stage record. The subsequent [existing-workspace validation](2026-09-04-workspace-refactoring-validation.md) records completed independent planning and migration exercises and the enclosing-garage extension; it supersedes this record's open refactoring checks only to that stated extent.

## Scope and implementation decisions

Implements the approved [design](../superpowers/specs/2026-09-04-organizing-workspaces-design.md) and [plan](../superpowers/plans/2026-09-04-organizing-workspaces.md). The implementation uses `workspace-setup` with display name “Set up the garage,” following the last recommendation and the user's instruction to implement. This is a reversible naming choice.

Work occurs on `codex/workspace-setup`. Initial tracked state was clean; the two untracked planning documents were created in this conversation. Live application workspaces are read-only examples, not migration targets. Tests use disposable directories.

The tasks share one instruction artifact and evidence record, so prose authoring is local and sequential, with independent baseline, forward exercises, and review where useful. During implementation the user explicitly requested a deterministic scaffold script. Its implementation and CLI tests are delegated independently of the prose; it is limited to new empty garages, with no migration automation.

Plan adjustment: the baseline agent was dispatched without the proposed skill or design and remained isolated while prose drafting proceeded. This preserves a no-skill comparison, but is not a strict test-before-prose sequence. Executable scaffolding uses a separate tests-first cycle. No evaluation claim is inferred from a missing file or from matching instruction text.

## Verified documentation

- [Skill discovery](https://learn.chatgpt.com/docs/build-skills): Codex initially sees name and description; implicit matching uses the description. Repository skill scanning runs from the current directory toward the repository root. Symlinked skills are supported. Changes are detected automatically, with restart recommended if they do not appear. This does not establish discovery above an independent application's Git root.
- [Instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md): Codex builds the instruction chain at startup, walking from the project root to the current directory; deeper instructions take precedence. Starting at the garage therefore does not automatically preload every application's descendant instructions. The garage should direct agents to read the selected application's applicable instructions and human-facing conventions before work.
- [Sandboxing](https://learn.chatgpt.com/docs/sandboxing): the active sandbox defines file and network boundaries; approval policy governs exceptions. A working directory and a Git ignore policy are not permission grants.

These sources were opened and read on 2026-09-04. Host-specific startup behavior is documented, not tested by launching a fresh desktop session. The skill must report that distinction when verifying a generated workspace.

## Evidence sources

The user supplied `/Users/phil-mac/Projects/workspace-refactoring-plan.md` and `/Users/phil-mac/Projects/vending-ops/.gitignore`. Both were read. They establish the intended garage pattern, including default-deny root tracking, not universal directory names or installation policy.

## Execution record

### Deterministic scaffold

Root verification: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_workspace_setup.py` passed 9 tests. Tests exercise the real CLI and Git: no-write preview, absent/empty target setup, space-containing paths, unchanged occupied directories and reruns, ancestor repository index preservation, bare repository and linked-worktree ownership, symlink refusal, root tracking exclusions, empty application/artifact homes, and no initial staging or remote. The script uses exclusive file creation as well as preflight refusal; there is no overwrite option.

### Repository checks

`sh tests/test-link-skills.sh` passed. The bundled skill validator passed using `uv run --with pyyaml python /Users/phil-mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py workspace-setup`. System and bundled Python lacked PyYAML, so uv's dependency environment was used with approved cache access. No dependency was added to the skill or repository.

Baseline and migration outcomes are recorded separately when complete; the checks above do not establish implicit selection reliability or universal migration safety.

### Baseline limitation

An isolated no-skill baseline was dispatched with empty-workspace setup, product-MCP ownership, and routine-feature boundary scenarios. It did not return a reviewable report within the bounded run and was stopped. Treat this comparison as inconclusive, not a failure of ordinary model behavior. The implementation packages the user's explicitly requested repeatable workflow; it does not claim demonstrated superiority over a no-skill baseline. Cross-project adoption evidence remains open.

### Direct migration smoke check

`python3 /private/tmp/verify-garage-migration.py` passed against a disposable fixture retained at `/private/tmp/garage-migration-check-3gpvbuc5`. It exercised a read-only inventory, then the scoped migration on a fresh copy: tracked and ignored reports copied to external artifacts with identical hashes; producer output configured through `REPORT_DIR`; consumer configuration updated; producer-to-consumer result verified; application HEAD/origin and unrelated dirty source preserved; supported MCP module retained; generated report removed only from the index while keeping working data; root index excluded application and artifact paths; a local standalone clone ran with no garage environment. Old report copies remain as explicitly retained recovery data.

This is an author-executed mechanical smoke check of the documented migration pattern, not an independent proof of agent decision quality. The temporary harness is validation scaffolding and does not ship inside the reusable skill.

### Final verification and limits

The final scaffold run passed all 9 tests in 1.271 seconds; skill-linking checks also passed again. Root inspected the scaffold implementation and its tests, the entry point, refactoring reference, and display metadata. The independent migration and review workers did not return reviewable reports within the bounded run and were stopped; no independent approval is claimed. The implementation worker also returned no RED-cycle report, so only the observed passing executable checks are recorded. Implicit skill selection, conditional-reference loading in a fresh host session, and live-project migration remain untested. No live workspace was restructured and no skill was installed into the user's global configuration.
