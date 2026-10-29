---
name: cross-model-review
description: Run an advisory cross-model pair-review loop from the implementing agent. Use the bundled deterministic runner to capture the complete change, invoke a caller-selected native reviewer, and save its original findings. Preserve explicitly configured legacy commands. Feedback is not verification or approval.
---

# Cross-model review

You are the implementer. A separate model is a second programmer looking over
your shoulder: it reviews the complete change, offers corrections, and you
choose what to accept. You own the implementation and dispositions. The runner
owns packet construction, one fresh native invocation, and retained evidence.
It does not approve, verify, merge, or release anything.

## Resolve the assignment

Use reviewer selection and authorization supplied by the coordinator first;
otherwise read the applicable `AGENTS.md` with the host's normal precedence.
Carry the tool, model, effort, authorization scope and source into the task.
A command or repository text alone is not proof of consent. Reuse established
user authorization; ask only for missing scope, provider choice, or decisions.

For new assignments, call `scripts/review.py` from this installed skill. The
caller selects `--tool muse|codex|claude`. Omitted `--model` uses that tool's
default: Muse `muse-wonder-full-1.0`, Codex `gpt-6-astra`, or Claude
`claude-opus-5-5`. Effort defaults to `max`; both values can be overridden.
These are explicit defaults, not automatic fallback or a claim about future
model availability. Do not change a caller's supplied selection.

Before building a packet, confirm that a
separate reviewer model has already been assigned and differs from your actual
current model. Supply its resolved
identity and yours; do not use an uncertain alias to evade the check. A default
that matches the implementer is a configuration conflict, not permission to
choose another reviewer. Return coordinator-owned conflicts to the coordinator.
When switching implementers, preserve material authorship and the task's existing
review history and exchange allowance; use `agent-handoff` where applicable.

Resolve the access boundary with the selection. Claude's restricted file tools
are confined to its working directories. Muse and Codex can read other files
accessible to their process; all adapters' live-read exclusions rely on reviewer
instructions. Codex retains a shell in its read-only sandbox, so the prohibition
on tests and project-code execution is an instruction, not a command allowlist.
Record these limits in the authorization input. They grant no permission to run
tests or read excluded material. If the assignment requires stronger technical
confinement, return that constraint to its owner before invoking this adapter.

If setup is missing, resolve only the missing choices and authorization with
the user, then update the applicable `AGENTS.md` using
[the configuration example](references/agents-example.md). Preserve valid
settings and unrelated instructions. Task-specific exceptions stay in the
assignment. Do not ask the user to write the configuration themselves.

An explicitly configured raw CLI command remains supported through
[the legacy procedure](references/legacy.md). Run that command exactly as
configured with its read-only controls. Do not silently substitute the runner,
migrate old reports, or restart a task's allowance in a new directory.

## Prepare the inputs

Work from the repository root. Read the brief or contract and run the project's
required checks before review. Preserve failures and identify the state tested:
working-tree tests do not establish that a different index version passes.

Prepare these small inputs in the project's retained evidence location:

- The existing brief or contract, unchanged.
- A Markdown checks file containing commands, observed results, state tested,
  and relevant output or durable artifact links, including failures and unknowns.
- A Markdown authorization file recording the actual source and scope of consent:
  provider, task material, and relevant repository files the reviewer may read.
  The runner permits read-only inspection; test execution remains your job.
- On subsequent exchanges, a Markdown disposition table covering every prior
  finding: stable ID (`CMR-001`, etc.), accepted/declined/deferred, rationale,
  correction and evidence. Explain prior failed or interrupted attempts and any
  change in exclusions; hiding a finding's path is not a correction.

Choose one retained review directory for the task, outside eventual cleanup
worktrees. It must be Git-ignored or explicitly excluded from the change.
Exclude credentials, unrelated private records, and generated files outside the
change with repeatable literal `--exclude` paths. Apply exclusions deliberately;
the script is not a secret detector and the reviewer must not inspect exclusions.

## Run one exchange

```sh
python3 <skill>/scripts/review.py \
  --repo <repository-root> --brief <brief.md> --checks <checks.md> \
  --authorization <scope.md> --author-model <actual-author-model> \
  --tool muse --review-dir <retained-review-directory>
```

Pass `--model` and `--effort` for explicit overrides, `--base` when the assignment
specifies it, and `--dispositions` on revisits. See
[the runner interface](references/runner.md) for defaults, exclusions, failures,
reconciliation, and the native isolation boundaries.

The runner captures status, history, committed change against base, staged
change against HEAD, working tree against index, and full untracked text.
It includes the brief, scope, check evidence,
reviewer instructions, report format, and all prior original reports. It does
not truncate oversized changes; split the task with its owner when necessary.
Do not commit staged content the reviewer has not seen.

Each invocation prints JSON with execution status, the separate advisory
outcome, and absolute artifact paths. Exit zero means a valid report was
obtained (or an explicit reconciliation completed), never that the change
passed. Read the actual report. `BLOCKED` is an incomplete review even when the
native call completed. Missing, malformed, failed, cancelled or timed-out output
is never a successful review. Do not silently retry or switch reviewers.

Retain each packet, exact native command, original `review-round-*.md`, stdout,
and stderr, including failures. The small task-local execution record exists
only to preserve round ownership, evidence identity and the allowance. It is
not a workflow tracker. Do not edit it to remove failures or reset the limit.

## Respond and revisit

Assign stable IDs to the reviewer's observations and record your disposition
for each. Accept and fix findings you judge correct; decline with rationale and
evidence, or defer explicitly. Return coordinator- or user-owned choices to
them. Re-run affected checks after fixes and refresh the checks and dispositions
inputs. Call the runner again against the same brief, base, and review directory.

There are at most **three launched exchanges per task**, across tools and
sessions. Failed or uncertain launches consume a reserved slot but are recorded
separately from completed reviews; preflight refusals do not launch or spend a
slot. Stop when there are no further suggestions, the cap is reached, or the
remaining disagreements should be weighed by the coordinator, verifier, or user.
Do not keep looping to manufacture agreement.

An interrupted/unknown execution requires confirming that its reviewer and
possible children stopped, then recording reconciliation as described by the
runner. Reconciliation preserves all evidence and never restores the allowance.
If native access is blocked by the host, retain the diagnostic and obtain the
required host permission before any explicit retry; never change the model or
relax the reviewer's read-only controls to work around it.

## Return the findings

The finish report must identify the actual reviewer tool/model/effort and native
command, separate authorship, exchanges used, execution status, final advisory
outcome, and each finding's disposition, including contested items. Include
check commands, results and the state tested, with their durable evidence.
**Link the original `review-round-*.md` reports.** A paraphrase in your summary
is not a substitute for the reviewer's own findings.

Report unavailable or `BLOCKED` review as incomplete, and open disagreements as
contested. Supply the full history to the coordinator and verifier. They retain
their own judgment; commits, publication, merges, releases and independent
verification remain governed by the assignment and project instructions.
