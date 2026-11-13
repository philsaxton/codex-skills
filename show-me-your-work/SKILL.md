---
name: show-me-your-work
description: Keep an evidence-linked decision trail for long-running, unattended, or multi-phase work that a human will review later. Use when asked to show the work or preserve decisions, pivots, and verification outcomes; ordinary progress updates and explanations alone do not need a log.
---

# Show Me Your Work

Leave a compact trail that lets a human see what happened, why consequential choices were made, and what evidence supports the result. Record concise decision summaries and observable facts, not private internal reasoning or a transcript of every action.

## Establish the trail

Read the task's existing records and applicable project instructions. Reuse an adequate decision record rather than creating a second source of truth. If one exists, keep its format and retention policy; the TSV format below is for a new trail.

Keep current delivery status in the project's authoritative tracker. Link historical decisions and evidence from that record instead of maintaining competing current-status summaries.

Choose a task-specific retained artifact location using the project's conventions. Keep logs and evidence out of disposable scratch and out of worktrees or checkouts scheduled for removal. A local working trail stays uncommitted by default; do not change ignore rules, publish records, or commit them merely because this skill is active. Follow the task's authorization and repository policy for intentional deliverables. Exclude secrets and unrelated private material.

Identify each contributing run with a stable label: an available chat or agent ID, or a unique task-local label. Keep it across later turns and context compaction in the same chat; use a new label for a replacement agent or new chat. On resumption, read the latest entries before continuing. Record a short start or handoff entry identifying the inherited state and any evidence not yet checked. Do not claim authorship or verification of inherited rows.

Keep one canonical trail per task. Give a shared file one writer and have other workers return entries to that owner. The helper does not coordinate concurrent writers; separate worker logs may be linked from the canonical trail when shared writing cannot be serialized.

## Record decisions and checkpoints

Log material choices, completed units with their observed checks, pivots or reverts and their triggers, blockers, and handoffs. Record a repeated attempt when it changes the approach, evidence, or outcome; skip repetitive tool activity that adds no review value. Write entries close to the event. Label reconstructed entries and their source; their timestamp is the recording time, not an invented event time.

Use one TSV row per entry with these columns:

| Column | Content |
|---|---|
| `ts` | UTC ISO 8601 recording time. |
| `run` | The contributing run's stable label. |
| `phase` | Workstream or checkpoint, such as design, implementation, verification, correction, or handoff. |
| `decision` | What was chosen or done, in concrete words. |
| `why` | The concise rationale or observed trigger; mention a decisive tradeoff when useful. |
| `evidence` | Resolvable pointers to relevant files, revisions, commands' saved results, screenshots, or scoped tool receipts. Use `unavailable: <reason>` when evidence is missing. |
| `result` | Observed outcome or current state, including failed, open, or inconclusive where appropriate. |

Cells stay on one physical line. Replace tabs and line separators with spaces and prefix formula-shaped values with an apostrophe. Enclose cells containing double quotes in double quotes and double their internal quotes. Read or import the result as tab-delimited text with `"` as the quote character; quoted text stays literal after decoding. Append TSV rows with the bundled helper, which applies this encoding and a UTC timestamp; any other writer must apply the same encoding:

```sh
bash /path/to/show-me-your-work/scripts/log.sh /path/to/trail.tsv \
  run-a verification 'Retained the retry failure' \
  'The second attempt reproduced the timeout' \
  'artifacts/task/retry.txt' 'failed; cause still open'
```

Pass arguments as quoted data; do not interpolate untrusted text into shell code. The helper checks the header and final newline, not every existing row. Before continuing an existing TSV, confirm that its rows use this encoding. If a legacy trail does not, preserve it and start a linked continuation instead of appending incompatible rows. Use the existing record's own mechanism when its format differs.

Name evidence precisely enough to recover the state reviewed: a commit or base/head pair for code, and the relevant instance, method, inputs, and result for a check. A command string alone shows a proposed method, not that it ran. Distinguish tests read from tests executed, and carried-forward evidence from fresh observations. Check that the cited evidence supports the claim; neither a worker's summary nor a green exit code establishes every requirement.

Preserve failures and abandoned approaches that materially shaped the work. Append corrections that identify the earlier row by run and line number, state what was wrong, and give the supported replacement. Do not silently edit or delete earlier rows, including unsupported success claims. A later success does not erase the earlier failure.

## Check and hand back

Before a handoff or final response, check this run's entries against the available active conversation, scoped tool receipts, and retained artifacts. Follow evidence pointers, resolve contradictions, and append material missing decisions or corrections. Do not scan unrelated chats for a transcript. If task-scoped history or evidence is unavailable, state which claims remain unchecked; do not describe the trail as fully audited.

Return a link to the trail and briefly flag unresolved decisions, weak evidence, failed or skipped checks, and remaining work that needs attention. Do not report independent review unless it actually occurred. If the task already requires review, supply the trail and relevant evidence through that workflow. Logging itself creates no new review gate and grants no authority to approve, merge, deploy, or publish.

Other skills may reference this skill for decision-trail mechanics. Keep application verification, advisory review, and workflow ownership with their assigned roles; a well-formed log is evidence to assess, not proof of correctness.

Adapted from pstack's `show-me-your-work`; see [NOTICE](NOTICE) and [LICENSE](LICENSE).
