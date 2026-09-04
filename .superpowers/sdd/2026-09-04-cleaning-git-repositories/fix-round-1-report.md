# Cleaning Git Repositories — Fix Round 1 Report

## Status

All four final-review safety findings were reproduced and remediated without changing the frozen design or implementation plan. The helper retains its two-command surface (`plan` and `apply-local`) and has no force-delete or remote-delete operation.

## TDD evidence

The reproduction tests were added before production changes. The initial full behavioral run executed 23 tests and failed exactly five tests:

- symlinked `.agents` ancestor was accepted;
- symlinked `skills` ancestor was accepted;
- a plan could not be bound to independently supplied trusted inputs;
- a branch with one removable and one retained checkout was scheduled for deletion; and
- a mid-apply recheck failure returned the generic error path without completed actions or the failing target.

After the minimal implementation changes, the suite passed 23/23. Two additional trusted-input cases cover integration-ref substitution and removal of a protected branch that does not change the action set. The final suite passes 25/25.

## Remediation

1. Protected-install validation now examines every component from the invoked script through the real `.agents` boundary. Copied scripts beneath symlinked `.agents` or `skills` ancestors are rejected before plan loading or mutation.
2. `apply-local` now requires `--repo`, `--integration`, and repeated `--protect` values in addition to `--plan`. Revalidation derives repository identity, integration ref/commit, and protected branches from these independent apply-time inputs and rejects disagreement with the untrusted JSON plan before comparing actions. `SKILL.md` tells callers to repeat the independently established cleanup basis rather than copy authority from the plan.
3. Planning now records every worktree for each branch and separately records the worktree paths scheduled for removal or metadata pruning. A branch deletion is emitted only when no checkout for that branch remains unscheduled.
4. Each apply action runs through one target-scoped error boundary. Git failures and validation/recheck failures after prior mutations now produce exit code 3 with the complete action log and the failing worktree, metadata set, or branch target.

## Verification

- Behavioral suite: `python3 -m unittest cleaning-git-repositories/tests/test_repository_cleanup.py -v` — 25 passed.
- Bytecode compilation: `python3 -m py_compile cleaning-git-repositories/scripts/repository_cleanup.py cleaning-git-repositories/tests/test_repository_cleanup.py` — passed.
- Skill validation: bundled `quick_validate.py` — `Skill is valid!` when run with an available cached PyYAML module. The default interpreter lacks PyYAML and the sandbox cannot fetch it from PyPI; this is an environment dependency issue, not an artifact validation failure.
- CLI surface: top-level help lists only `plan` and `apply-local`.
- Static production scan: no `branch -D`, `push`, `remote-delete`, `shell=True`, `os.system`, or `subprocess.Popen` match under `cleaning-git-repositories/scripts`.
- Patch hygiene: `git diff --check` passed.
- Scope check: only `cleaning-git-repositories/{SKILL.md,scripts/repository_cleanup.py,tests/test_repository_cleanup.py}` and this requested report changed; the frozen design and plan have no diff.

## Self-review

The changes preserve standard-library-only production code, argument-array Git execution with `shell=False`, full-plan validation before the first mutation, per-target rechecks, worktree-before-branch ordering, safe `git branch -d`, and the separate remote-authorization boundary. No unrelated refactor or feature was introduced.

## Concerns

The bundled validator's default Python environment does not include PyYAML. Validation succeeded using the existing cached PyYAML installation, but a bare invocation of the validator on this host fails before reading the skill unless its dependency is supplied.
