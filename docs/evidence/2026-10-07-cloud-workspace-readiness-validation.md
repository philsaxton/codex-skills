# Cloud workspace readiness validation

Date: 2026-10-07 UTC. Scope: local source candidate based on codex-skills main `4fb59298556a28f1eca6cffd29337f88817388e9`. This record describes implementation verification, not project acceptance, installation, or a live recovery.

## Change boundary

The existing skill gains one short cloud-mode routing bullet, updated discovery/UI text, one focused cloud reference, a declarative schema with three sanitized examples, and one read-only prerequisites helper. The initializer, its existing tests, and the migration reference remain byte-identical to the source base. No Git history was synthesized for the source candidate. No application, installed skill, vendor pin, provider, Mac task or publication was changed by this implementation.

Following a separately reviewed narrow packaging amendment, the helper uses the exact reviewed recovery dependency bundled under `workspace-setup/scripts/recovery/`. An operator-supplied alternate directory remains supported with identical pins. Both modules are verified before either is loaded:

- `garage_rebuild.py`: `8c0914a2830900989e090c9e904196167a1abd73d8cff3ac47013376a5daf0ef`
- `garage_workspace.py`: `bdabd09a0d988481c1f296a5ebba95720576ac386308534835dca7d5801b120c`

The authoritative pins are in `workspace-setup/references/recovery-dependency.json`. Exactly one unchanged implementation copy is maintained in the skill; the three original recovery test modules are also retained unchanged. `references/recovery-provenance.md` records hashes, the absence of an explicit standalone source license, and the test-only launcher that binds original CLI constants to bundled modules. The separately performed pre-packaging dependency baseline passed all 79 tests in 79.414 seconds, including its 304 MiB streaming private-restoration case. A relocated bundled run is reported below; the module bytes were not modified.

## Failing-first evidence

- The initial 23 test methods failed before the helper existed: 46 failing assertions/subcases, no test errors. The first implementation left one unregistered-skill state-classification failure; correction produced 23 passing methods.
- Additional failing-first checks demonstrated absent schema/examples and the need to compare an actual Git commit's tree with supplied source identity. The resulting 28-method suite passed.
- A large declared-check cross product produced an oversized report in a failing test. The helper now refuses profiles above 1,024 emitted checks before inspection/report generation.
- Two malformed-ref subcases failed before enforcing invalid dotted/lock-suffixed ref components. Both pass after that correction.
- Pre-packaging readiness suite: 29 methods, all passed, no skips, 4.069 seconds. Packaging then added three failing-first tests for default resources, true fresh-location use with an audit hook denying access to the original dependency directory, and discovery of all 79 preserved recovery cases. The packaged readiness suite passes all 32 methods with no external dependency environment setting. Tests construct isolated synthetic workspaces and local Git repositories, never actual application projects.

These checks cover selected source bytes and Git object/tree hashes; source-ready snapshots without history; exact genuine HEAD/tree and missing historical objects; shallow, promisor, alternate and unsupported-config refusal; fresh profile/workspace/context-bound host observations; registration/resource/version mismatches; optional private-input and companion-hash gates; report-parent existence/type and unproven write access; malformed/unknown schema fields and unsafe paths; private-error redaction; no profile-command execution; and unchanged inspected workspace/dependency inventories.

The three published example profiles drive tests with distinct outcomes: Scope-like ordinary prerequisites ready, ACKS-like missing optional audit input with build still ready, and CAW-like history/report prerequisites blocked on a source snapshot. They are fictional and carry no actual project approval or readiness claim.

## Verification commands and results

The tests default to the bundled recovery modules; `GARAGE_RECOVERY_DEPENDENCY` can select an alternate exact reviewed copy for the new helper tests. Set `TMPDIR` to allowed disposable test storage. All Python test runs used `PYTHONDONTWRITEBYTECODE=1`.

```sh
python3 -m unittest discover -s tests -p test_cloud_readiness.py -v
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s cleaning-git-repositories/tests -v
python3 tests/run_recovery_tests.py
bash tests/test-link-skills.sh
python3 <skill-creator>/scripts/quick_validate.py workspace-setup
```

- Packaged readiness: 32/32 passed in 4.429 seconds
- Packaged full root discovery: 54 executed; 49 passed and the same five pre-existing scaffold-positive tests failed in 6.339 seconds
- Relocated bundled recovery dependency: 79/79 passed in 70.899 seconds, including the 304 MiB private-file streaming case
- Repository cleanup: 25/25 passed in 3.622 seconds
- Shell skill-link tests: exit 0
- Skill-authoring validator: `Skill is valid!`
- JSON Schema Draft 2020-12 validation: schema valid; all three profiles, a generated host observation and selected private manifest validated with the available `jsonschema` validator. That validator is a development check, not a runtime helper dependency
- Byte comparison confirmed the initializer, migration reference and existing scaffold tests remain unchanged; no candidate `.git` metadata exists

The inherited failures are:

1. `test_apply_accepts_an_absent_target`
2. `test_apply_creates_thin_unstaged_repository_with_expected_boundaries`
3. `test_dry_run_reports_fixed_layout_without_writing`
4. `test_rerun_refuses_and_preserves_the_workspace`
5. `test_workspace_docs_track_separately_from_app_docs_reports_and_recovery`

Each refuses a pre-existing ancestor `.git` sentinel in the cloud test environment. Both default and task-local temporary ancestors had already exhibited this unchanged baseline behavior. The initializer deliberately guards entry presence even when Git does not recognize a repository. No ancestor sentinel was deleted and no guard was weakened. Therefore this is not a wholly green root-suite result; a clean-environment scaffold-positive run remains outstanding.

## Remaining trust and capability boundaries

Host registration/resource/tool observations are supplied evidence, not independently authenticated host state. Connector metadata similarly supplies commit-to-tree provenance; byte hashes do not authenticate its origin. Selected-source verification does not certify a clean working tree or inspect unrelated private material. Report parents remain unverified for actual writing without a separately authorized smoke test. Source symlinks, linked-worktree metadata and unsupported Git storage/configuration report unavailable.

The helper never acquires source, restores files, installs/registers tools or skills, runs profile commands/tests, writes reports, performs ongoing backups, or claims project acceptance. Missing or modified bundled bytes and actual connector acquisition limits remain explicit blockers. Independent final review and forward testing are separate outstanding gates for this implementation record.
