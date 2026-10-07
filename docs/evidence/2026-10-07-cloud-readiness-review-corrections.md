# Cloud readiness review corrections

Date: 2026-10-07 UTC. Base: PR #2 head `36c1188446e0a940754376c5640f9a3d38472311`. Validation used a fresh selected-source snapshot: 31 required files were checked against their Git blob identities and preserved as the baseline. This is not a full repository/history recovery. The [earlier validation record](2026-10-07-cloud-workspace-readiness-validation.md) remains unchanged and describes its historical candidate.

## Corrections

- [Expanded inventory finding](https://github.com/philsaxton/codex-skills/pull/2#discussion_r4210273163): source traversal permits exactly 10,000 expanded entries, then refuses before allocating another path or entry. Directories, files and symlinks each count. Every occurrence of a shared subtree counts, and all selected checkpoints share one bundle budget, including repeated paths in separate checkpoints. Standalone validation starts with the same maximum. A valid large selection can now be refused; source identity and acquisition authority are unchanged.
- [Case-sensitive fixture finding](https://github.com/philsaxton/codex-skills/pull/2#discussion_r4210273166): the two filesystem collision tests check whether the second spelling already resolves after creating the first. Aliasing storage receives an explicit capability skip before an overwrite or second directory creation. Production collision protection remains unchanged; two virtual-source tests exercise file and ancestor collisions independently of filesystem case behavior.
- Runtime/test pins and [provenance](../../workspace-setup/references/recovery-provenance.md) distinguish the original release from deliberately revised bytes. The original 79 cases remain, with two fixtures adapted; 10 source-expansion/collision cases were added to the pinned recovery runner. Two root tests separately exercise the capability-skip branches.

## Failing-first evidence

Before changing production code, the 10-case expansion suite produced five expected failures: single-snapshot overflow, compact shared-tree DAG expansion, mixed directory/symlink accounting, aggregate checkpoint overflow, and traversal continuing to an unreachable missing tree instead of stopping at the budget. The five compatibility/collision cases passed. The corrected suite passes all 10 cases, including exact-boundary acceptance and valid shared-tree preservation.

Both skip-branch tests initially failed: the directory fixture reached `FileExistsError`, and the file fixture did not report a skip. Both pass after the fixture correction. On this Linux filesystem the branch exercises use symlink aliases; they do not establish a Mac or case-insensitive-filesystem run. Their setup detects naturally aliasing storage and avoids creating a self-referential symlink there.

The runner discovery regression failed with 79 discovered cases when 89 were required, then passed after adding the new pinned test module.

## Verification

Host: Linux x86-64, Python 3.12.14, Git 2.52.0. Python runs used `PYTHONDONTWRITEBYTECODE=1`. The relevant commands, run from the selected source root, were:

```sh
PYTHONPATH=workspace-setup/scripts/recovery python3 -m unittest discover -s tests/recovery -p test_source_expansion.py -v
python3 -m unittest discover -s tests -p test_recovery_case_fixtures.py -v
python3 -m unittest discover -s tests -p test_cloud_readiness.py -v
python3 -m unittest discover -s tests -v
python3 tests/run_recovery_tests.py
python3 -m unittest discover -s cleaning-git-repositories/tests -v
bash tests/test-link-skills.sh
python3 <skill-creator>/scripts/quick_validate.py workspace-setup
```

- Expansion/collision regressions: 10/10 passed
- Skip-branch exercises: 2/2 passed, using synthetic aliases on this host
- Readiness: 32/32 passed, including relocated dependency loading and 89-case discovery
- Bundled recovery: 89/89 passed in 75.278 seconds, including the 304 MiB private-file streaming case; no capability skips. Both real filesystem collision tests ran and passed on this case-sensitive host
- Root discovery: 56 executed, 51 passed, five inherited failures; no skips
- Repository cleanup: 25/25 passed
- Shell skill-link tests: exit 0
- Skill-authoring validator: `Skill is valid!`

The pristine baseline root run first reproduced the same five failures (49/54 passed). Each fails because the scaffold refuses the existing ancestor Git entry at the system temporary directory:

1. `test_apply_accepts_an_absent_target`
2. `test_apply_creates_thin_unstaged_repository_with_expected_boundaries`
3. `test_dry_run_reports_fixed_layout_without_writing`
4. `test_rerun_refuses_and_preserves_the_workspace`
5. `test_workspace_docs_track_separately_from_app_docs_reports_and_recovery`

No guard was weakened and no ancestor Git entry was removed. This is not a wholly green root-suite result; clean-environment scaffold-positive coverage remains outstanding. There was no Mac run or actual case-insensitive-filesystem run.

The original recovery core, other two original recovery test modules, initializer, migration guidance, schema, synthetic example identities and earlier evidence remain unchanged. No Git metadata was created in the selected source candidate. This correction did not install skills, change active pins, acquire application/private sources, mutate system settings, publish, modify PR #3, or establish project acceptance. Independent review and publication are separate gates.
