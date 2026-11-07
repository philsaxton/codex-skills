# Deterministic review runner

Run `python3 <skill>/scripts/review.py --help`. Python 3.10+ and Git are required;
locking and process control currently target macOS and Linux. The caller prepares
the repository and inputs; this helper creates no worktrees and edits no source.

## Inputs

Required for a review: `--repo`, `--brief`, `--checks`, `--authorization`,
`--author-model`, `--tool`, and `--review-dir`. File inputs are UTF-8 Markdown;
their contents are preserved in the packet. Paths resolve from the caller's
directory. `--repo` must be the exact checkout root. The authorization file
records permission already established by the caller; writing it grants none.

| Tool | Default model | Default effort |
| --- | --- | --- |
| Muse | `muse-wonder-full-1.0` | `max` |
| Codex | `gpt-6-astra` | `max` |
| Claude Code | `claude-opus-5-5` | `max` |

Use `--model` / `--effort` to override. These defaults were selected on
2026-10-29. Opus's ID is confirmed in the [Anthropic documentation](https://platform.claude.com/docs/en/models/opus-5-5/overview);
Astra and `max` in the [OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra).
Muse's installed model-profile resolver recognizes Wonder-Full at max.
There is no automatic fallback. Supply resolved identities for independence;
the caller is responsible for resolving aliases and actual model changes.
Leading and trailing whitespace is removed from both model identities before
validation, recording and invocation; identity comparisons ignore case.

`--base REF` pins a commit. Initially the default is the merge-base with
`origin/main`, falling back to `main`. Revisits reuse that pinned commit.
Changing the repository or base is refused. A normal review also refuses a
brief change that has not been recorded through a continuation.

Repeat `--exclude path` for literal repository-relative files or directories,
not glob patterns. Exclusions apply to status, history, all three diffs and untracked
content, and are listed in the packet. History retains empty commits and merges
that change included paths or introduce included history. Commits and merges
confined to excluded changes are omitted, including their subjects.
Input documents are supplied explicitly
and are not filtered. Symlinks are recorded as link targets, never followed for
packet capture. Binary, non-UTF-8, special-file and submodule changes require an
explicit exclusion or another review method; they are never silently omitted.
Unmerged index entries must be resolved or explicitly excluded before review.
Included tracked paths marked `assume-unchanged` or `skip-worktree` are refused,
even if they appear clean: Git can hide their working-tree changes. The caller
must clear those flags or explicitly exclude those paths; the runner never
changes index flags.
Each exchange records its exclusion list, tool, model, effort and author.
Revisits expose that earlier scope alongside the current scope. Explain every
scope change in dispositions; the reviewer must flag unexplained narrowing.
Older runner records without indexed exclusions point to their original packet
and explicitly mark that field unknown rather than invent a prior scope.

`--max-packet-bytes` defaults to 2097152. Oversized inputs or packets fail before
invocation, without truncation. Raise the limit explicitly only when the chosen
model can accept the complete packet. `--timeout` defaults to 1800 seconds.
`--dispositions FILE` is required after the first launched exchange, including
after a failed attempt. Supply finding IDs, decisions, evidence and failure
disposition; the script preserves this file without inventing judgments.

## Reassessment and continuation

The initial allowance is three reserved launches. Exhaustion requires the
coordinator or authorized owner to reassess the evidence and open findings.
Repeated remediation of the same unresolved root cause routes earlier for
diagnosis or design assessment, across all feedback sources. A different
reporter, model, context, commit or finding label alone is insufficient.

The owner may authorize one to three additional launches for materially new
authorized work, a distinct finding, an evidence-backed changed approach, or
a repaired review-execution prerequisite. The decision may precede exhaustion;
it retires unused old slots and replaces them with the new bounded allowance.
It never resets cumulative rounds. Routine in-scope continuation uses existing
authority; protected requirements and product choices retain their owners.

Record the decision separately from any reviewer invocation:

```sh
python3 <skill>/scripts/review.py --review-dir <same-directory> \
  --repo <same-checkout-root> --brief <current-authorized-brief.md> \
  --continue-with <decision.json>
```

This metadata operation requires existing valid runner history. It accepts
`--exclude` for output-location safety and an optional `--base` matching the
pinned base. It rejects review and reconciliation arguments, including model,
tool, checks, authorization, dispositions, effort, timeout and packet-size
options. It never probes or invokes a reviewer. Supply current check evidence,
provider/data authorization and dispositions on the subsequent normal review.

The UTF-8 JSON decision must contain exactly these fields. Replace the example
round, hashes and text with the inspected current state and actual decision:

```json
{
  "version": 1,
  "after_round": 3,
  "history_sha256": "<SHA-256 of exact current review-state.json bytes>",
  "allowance": 2,
  "brief_sha256": "<SHA-256 of exact supplied brief bytes>",
  "owner": "<coordinator or designated authorized owner>",
  "authorization_source": "<assignment or decision establishing authority>",
  "basis": "changed_approach",
  "rationale": "<changed basis, evidence, open findings and expected progress>"
}
```

`basis` is `new_authorized_work`, `distinct_finding`, `changed_approach`, or
`repaired_prerequisite`. Text fields must be nonempty, digests lowercase
64-digit hexadecimal, `after_round` the current cumulative reserved count,
and `allowance` an integer from 1 to 3. Booleans and duplicate JSON fields are
refused. The state hash binds a new decision to the exact current journal,
including reconciliations and earlier continuations. It does not pin the
working tree or authenticate the named owner, authority source or rationale.
The responsible roles assess those claims; accepting a file grants no authority.

Each decision is retained verbatim as `review-continuation-N.json`, alongside
the exact supplied `review-brief-N.md`, with hashes in the journal. The next
boundary is `after_round + allowance`; same-round decisions replace rather
than accumulate slots. The initial brief hash stays unchanged; the latest
continuation establishes the active brief. New histories use state version 2.
Valid version 1 histories retain their initial allowance and remain version 1
until an explicit continuation promotes the journal. Promotion preserves every
old exchange object, hash, report and other original artifact. Legacy directories
without runner state are never silently adopted.

Exact decision-and-brief replay is a no-op, including after later rounds or
continuations. It reports the current allowance without granting slots again.
Other stale decisions or changed replay bytes are refused. Any uncertain
execution must be reconciled first, even before replay; a decision prepared
before reconciliation is stale. Damaged or missing retained evidence blocks
continuation as it blocks review.

Evidence files are written without replacement before the atomic journal
update, under the same persistent lock. If both files were fully written but
the journal update failed, identical retry can finish once. Partial, conflicting,
symlinked or unexpected unrecorded evidence is preserved and refused; route it
to its owner for reconciliation. Evidence without a journal entry grants no
allowance. Never delete or edit history to obtain another window.

Future packets embed current requirements and checks, all original reports and
dispositions, and retained continuation decisions and brief snapshots marked
historical or current. Initial requirements may exist only in a linked original
packet; they are not extracted or fabricated. That path may be unavailable to
the reviewer, including under Claude's restricted reads. Report unavailable
historical comparisons as unknown, and `BLOCKED` when the missing basis materially
prevents the assigned review. An owner can supply an inspected, provenance-marked
excerpt through an authorized input when exact old text is needed. No additional
native permissions are implied. Complete history must fit the packet budget;
it is never silently truncated.

## Outputs and recovery

The review directory is the task's history, not temporary scratch. It holds the
existing `review-packet.md` / `review-packet-N.md`, `review-command-N.txt`,
`review-round-N.md` and `review-round-N.stderr.log` conventions. A stdout log
retains native output separately where the CLI supplies its final report through
a file. The original Markdown is not rewritten, even when invalid or partial.

`review-state.json` records execution identity, original artifact hashes,
cumulative attempts and bounded continuation decisions. `.review.lock` prevents
simultaneous callers. Output checks cover cumulative round and continuation files.
Initial input, output-location and packet validation happens before creating
a directory or lock. Existing locks remain in place after refusals and completed
calls so concurrent callers continue to use the same lock file.
Do not edit, delete or copy these to reset the task. Existing legacy reports
remain readable, but a directory without runner state is not silently adopted:
continue its explicit legacy procedure and retain its original allowance.

The review JSON result identifies `execution`, `outcome`, round, selected model/effort,
and absolute artifact paths. Successful review, reconciliation and continuation
results include `allowance_used`, `allowance_limit`, `allowance_remaining`,
`reassessment_required` and the exact current `history_sha256`. A refusal at an
exhausted allowance also includes these fields when history is valid.
`continuation_recorded` identifies its retained paths and whether it was a replay;
it is metadata success, not a review outcome. `completed` means the native process exited zero
and produced the required report shape. Advisory outcomes remain `SUGGESTIONS`,
`NO_FURTHER_SUGGESTIONS` or `BLOCKED`. A valid `BLOCKED` report is still incomplete
review. `failed`, `timeout`, `cancelled` and `invalid_output` preserve diagnostics
without becoming a completed review. `not_run` is a preflight/input refusal.
Exit codes: 0 for completed/reconciled/continuation_recorded, 1 for an unsuccessful invocation, 2 for
input/preflight refusal. None means the implementation is approved or verified.

After a crash or interruption, first establish that the native reviewer and all
possible children stopped. The runner records its own process group but cannot
prove the absence of an escaped or externally managed process. Save the evidence
and reconcile without launching a model:

```sh
python3 <skill>/scripts/review.py --review-dir <same-directory> \
  --reconcile-round 1 --reconciliation <stop-evidence.md>
```

A still-existing recorded group is refused. Reconciliation records the caller's
evidence, preserves partial reports, and consumes rather than restores the slot.
It freezes hashes of all present artifacts and explicitly records absent ones,
so later alteration or appearance is refused. This establishes identity from
reconciliation onward; the operator must establish what happened before a crash.
The reconciliation note is also hashed. Retrying with the identical note is
idempotent, including after a note write succeeded but the journal update failed;
different evidence never replaces the original. Earlier runner records without
a note hash retain that historical limitation rather than claiming retroactive
integrity checking.
The next explicit review uses fresh check evidence and dispositions. A surviving
`starting` record with no PID is unknown, not evidence that launch never happened.
Process-group IDs can be reused: compare the saved argv and launch timestamp
with the live process identity before signalling anything. Never stop an unrelated
group merely because its numeric ID matches. The runner conservatively refuses
reconciliation while that group exists; it does not signal it during recovery.

## Native adapters

All adapters use existing native authentication, fresh sessions, caller-specified
selection and supported read-only controls. They never change global settings or
select API billing. The host must still permit the native runtime's own storage
and network access. Model access errors are reported, not worked around.

Qualified versions on 2026-10-29: Claude Code 2.1.312, Codex 0.164.0 and
Muse 1.4.13-R6996.1. This does not establish equivalent behavior for every CLI
version or managed configuration. Unsupported controls fail rather than being
removed automatically.

- **Claude Code:** safe mode plus restricted mode, no session persistence,
  explicit Read/Glob/Grep tool allowlist, no MCP tools, and non-interactive
  permissions. Restricted mode confines file tools to working directories and
  ignores user/project/local settings; admin-managed policies still apply.
  It does not use
  bare mode, which would change authentication behavior.
- **Codex:** ephemeral execution in a read-only sandbox, no inherited execution
  rules, approvals disabled, and apps/plugins/hooks/subagents/browser/image/web
  capabilities disabled. It enumerates config-file MCP servers, disables each
  by exact name, and uses supported MCP and feature readback from the target
  checkout. The initial inventory is required to construct those exact-name
  overrides; unavailable or unusable inventory leaves the review unrun.
  Its shell remains available:
  the sandbox prevents repository writes, while no tests/project execution is
  an instruction rather than a technical command filter.
- **Muse:** native-basic preset restricted to read_file, shell and write
  tools disabled, hooks overridden empty, no session log, no reminders/web tools
  or foreign personal context. Known hook, MCP or plugin configuration in user
  or project settings, parsed installed plugins, and malformed local settings
  require resolution. A configuration source or file's presence alone is not
  a conflict; empty settings and hooks are allowed.

MCP/feature readback after Codex control construction and Muse status, plugin
inventory and local echo are corroborating inspection. Unavailable, incomplete
or unparseable inspection records a limit and permits the unchanged native
command; it does not require proof of internal enforcement. Parsed enabled
Codex capabilities or servers still refuse, as does a newly observed server
outside the constructed disable map. Local settings that cannot be read record
a limit; malformed actual settings still refuse. The runner never strips a flag
or changes reviewers when the native command rejects a control: that attempt
fails and the requested review remains incomplete.

Sanitized `configuration_notes` identify inspection limits in the packet,
exchange state, result and later review scope, and in preflight refusal results
when available. They omit raw probe output and configuration values. Earlier
records without this optional field have no recorded notes; they do not
establish successful inspection. Notes count toward the complete packet budget.

Reviewer instructions permit relevant file inspection and prohibit test/project
code execution. File readers and the read-only sandbox constrain changes;
authorization still determines which material may be inspected. Muse/Codex can
read outside the repository within their process's access, and exclusion filters
apply technically to packet capture only, not to live file reads. Record these
limits in the authorization input before selection; when the assignment requires
technical confinement that an adapter lacks, that adapter is unsuitable without
additional qualified isolation. These limits do not authorize forbidden reads
or execution. The helper is
not a general sandbox for hostile repository code or an authenticity verifier
for caller-supplied evidence.
