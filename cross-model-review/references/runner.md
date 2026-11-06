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
Changing the repository, brief or base in an existing task is refused.

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

## Outputs and recovery

The review directory is the task's history, not temporary scratch. It holds the
existing `review-packet.md` / `review-packet-N.md`, `review-command-N.txt`,
`review-round-N.md` and `review-round-N.stderr.log` conventions. A stdout log
retains native output separately where the CLI supplies its final report through
a file. The original Markdown is not rewritten, even when invalid or partial.

`review-state.json` records execution identity, original artifact hashes and the
three reserved exchange slots. `.review.lock` prevents simultaneous callers.
Initial input, output-location and packet validation happens before creating
a directory or lock. Existing locks remain in place after refusals and completed
calls so concurrent callers continue to use the same lock file.
Do not edit, delete or copy these to reset the task. Existing legacy reports
remain readable, but a directory without runner state is not silently adopted:
continue its explicit legacy procedure and retain its original allowance.

The JSON result identifies `execution`, `outcome`, round, selected model/effort,
and absolute artifact paths. `completed` means the native process exited zero
and produced the required report shape. Advisory outcomes remain `SUGGESTIONS`,
`NO_FURTHER_SUGGESTIONS` or `BLOCKED`. A valid `BLOCKED` report is still incomplete
review. `failed`, `timeout`, `cancelled` and `invalid_output` preserve diagnostics
without becoming a completed review. `not_run` is a preflight/input refusal.
Exit codes: 0 for completed/reconciled, 1 for an unsuccessful invocation, 2 for
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
  by exact name, and reads back the effective MCP and feature configuration from
  the target checkout before calling the model. Its shell remains available:
  the sandbox prevents repository writes, while no tests/project execution is
  an instruction rather than a technical command filter.
- **Muse:** native-basic preset restricted to read_file, shell and write
  tools disabled, hooks overridden empty, no session log, no reminders/web tools
  or foreign personal context. The current adapter refuses every non-absent or
  unknown source reported by `muse config status` (currently enterprise defaults
  and policy planes), user hooks, installed plugins, configured MCP servers and project Muse
  configuration rather than assume it can isolate them. Its supported baseline
  is a normal native login without those integrations.

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
