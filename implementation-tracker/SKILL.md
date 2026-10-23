---
name: implementation-tracker
description: Read, insert, and update implementation slices in a normalized Markdown tracker, with revision-checked writes and structural validation. Use when maintaining recorded delivery state or retrieving slices by recorded status.
---

# Implementation Tracker

Keep one human-readable record of each slice's current state. Agents and the
project's governing workflow decide readiness, priority, assignment, approvals,
gates, and completion. The helper records supplied decisions; it never makes
those decisions or starts work.

Use the bundled `scripts/implementation_tracker.py` with Python 3.10 or newer;
it needs only the standard library. Resolve the script from this skill's
installation, not from a guessed project copy.

## Select the record

The default is `./IMPLEMENTATION.md` in the command's working directory. Run
from the intended application root, or pass `--file PATH` explicitly. The
override changes the location, not the schema. Do not discover a different
tracker by guessing filenames or select an enclosing workspace's tracker.

Read [the format and command reference](references/format.md) when creating,
normalizing, or directly editing a tracker. `init` creates a new empty document
and refuses to overwrite any existing file. Existing project formats require
deliberate normalization: preserve IDs, decisions, contracts, evidence and
history, and have the responsible agent resolve status mappings. The CLI does
not silently migrate them.

## Retrieve and record

Examples below use `TRACKER` to mean the absolute path to the bundled script:

```sh
python3 "$TRACKER" list --status ready --json
python3 "$TRACKER" inspect S001 --json
python3 "$TRACKER" update S001 --status in_progress --owner "delivery agent" --expected-revision REVISION --json
python3 "$TRACKER" insert S002 --title "Add export" --checkpoint "Export matches the approved contract" --expected-revision REVISION --json
python3 "$TRACKER" --file docs/delivery.md validate --json
```

Every successful command returns the selected file and its revision. Use the
revision from the read on which the recording decision was based for each
`insert` or `update`. If the file changes, the helper refuses the stale write.
Reread the affected records, reconsider the intended edit, and retry with the
new revision only if it still expresses the authorized decision. Do not blindly
substitute the latest revision or invent authority from a successful validation.

Multiple slices may be active. `list --status ready` filters recorded values;
it does not evaluate dependencies, select the next task, promote other records,
or infer a parent's state. A coordinator can use the returned records in its
own decision-making workflow.

## Preserve one authority

Store current fields once, inside the marked table. Use `list` and `inspect`
for views; keep detailed specifications and dated evidence at linked locations.
Do not add manually maintained current-status tables or summaries elsewhere.
Historical evidence keeps its original meaning when a current record changes.
The helper does not interpret arbitrary prose as a second live record.

Direct Markdown editing remains supported. Run `validate` after manual changes;
subsequent reads see those bytes immediately. Cooperating CLI writers serialize
their saves and check the whole document revision. Ordinary editors do not take
that lock and can overwrite newer work from an old buffer, so coordinate manual
saves with CLI writers. Separate Git worktrees are separate copies: designate
one shared tracker path for concurrent recording, or reconcile their changes
through the project's Git workflow before treating either as current.

For a busy lock, identify the writer before retrying. The reference describes
recovery after a crashed writer; the helper never breaks a lock automatically.
Report structural errors to the record's owner rather than guessing missing
IDs, rewriting decisions, or adding new project gates.
