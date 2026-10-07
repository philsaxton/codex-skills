# Cloud-development skill validation

## Scope and design

`cloud-development` is a standalone instruction skill for keeping ongoing ephemeral development recoverable. The name describes the ongoing task without tying the workflow to one cloud provider. The 35-line entrypoint routes to three focused references: publication checkpoints, private artifacts and recovery handoffs. UI metadata keeps normal implicit discovery enabled. There is no executable helper, transfer daemon or connector-to-shell bridge.

The skill consumes existing setup/profile evidence without requiring another skill to run. It leaves initialization/readiness with workspace-setup and roles/review/authority with the owning workflow, including coordinator when available. All pre-existing repository files, including those two skills, remain unchanged.

Independent pre-implementation design review supported the instruction-only approach. Its three clarifications were adopted: derive project/provider/computer restrictions from current policy; distinguish newly created source-snapshot commits from preservation of existing Git history; and keep recovery mutations/worker interruption within actual authorization. The review did not grant publication or installation authority.

## Source and delivery boundary

The isolated source snapshot was verified against all 109 files in remote tree `4d05008ea93c4d12d11b390b7e1f44f9d938f250`, commit `36c1188446e0a940754376c5640f9a3d38472311`. This is the reviewed workspace-setup extension in draft [PR #2](https://github.com/philsaxton/codex-skills/pull/2), not a full-history local checkout.

The new feature branch `dot/cloud-development-20261007` is explicitly stacked on `dot/workspace-setup-cloud-20261007` at that commit. Its separate draft PR targets that branch so this review contains only the new skill and its validation artifacts. The stack must be reconciled deliberately when the upstream PR changes or merges; this work does not merge or retarget it automatically.

Source development and publication are in scope. Skill installation, live project pins, Mac tasks, credential setup, recurring transfers, merge and deployment are outside this change.

## Mechanical checks

- Skill-creator quick validation: passed
- All relative Markdown resource links in the skill resolve
- UI name, short description and default prompt match the entrypoint
- Existing `bash tests/test-link-skills.sh`: passed
- Byte comparison: all 109 baseline files unchanged
- Root `python3 -m unittest discover -s tests -p 'test_*.py'`: 49 passed, five failed out of 54

The five failures are the existing workspace scaffold positive cases: `test_apply_accepts_an_absent_target`, `test_apply_creates_thin_unstaged_repository_with_expected_boundaries`, `test_dry_run_reports_fixed_layout_without_writing`, `test_rerun_refuses_and_preserves_the_workspace`, and `test_workspace_docs_track_separately_from_app_docs_reports_and_recovery`. Each stops because the cloud host reports `/tmp` as owned by an existing Git repository. A fresh run on the unchanged PR #2 baseline produced the same five failures. No guard, code or test was weakened. The clean-host scaffold positive run remains unverified.

## Behavioral validation

The [ten raw synthetic scenarios](../../evals/cloud-development/scenarios.md) exercise code/private-copy separation, ambiguous publication, cancellation, overlays, coherent recovery, active workers, prohibited ancestry, backup integrity, source-only commits and standalone/project-policy behavior. See the [observed results](../../evals/cloud-development/results.md) for outcomes and limits.

These are instruction-following trials with simulated provider evidence. They do not prove live transfers, reliable scheduling, implicit host activation, tested production restoration or improvement over a no-skill control. No remote data, private source material or actual project state was used in the scenarios.

## Reviewed instruction identity

The aggregate is SHA-256 of compact, key-sorted JSON mapping each skill-relative path to its SHA-256. It covers the entrypoint, UI metadata and all three references:

`a95c21b7dd59c99dec8fc197864967d9900d84293abb5d22c949dc49041d990b`

The entrypoint SHA-256 is `a14a5e782d78495c69602e2cdf7b73f4a37c1129a498dff3e534770f51409b58`.
