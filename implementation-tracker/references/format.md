# Tracker format and commands

The Markdown file is authoritative. There is no database, persistent index, or
saved summary to synchronize. Each invocation parses the selected document
once into records; agents use commands rather than repeatedly parsing it.

## Version 1

Exactly one unfenced marker pair encloses a Markdown table. Prose, links, and
historical notes outside it are preserved. Fenced examples are not live tables.

```markdown
# Implementation

<!-- implementation-tracker:v1 -->
| ID | Title | Status | Checkpoint |
| --- | --- | --- | --- |
| S001 | Define the request contract | planned | [Acceptance criteria](docs/request-contract.md) |
<!-- /implementation-tracker -->
```

The four shown columns are required; other supported columns are optional and
may appear in any order. Empty cells represent absent optional information.
Column names are case-sensitive. Unknown or repeated columns are errors.

| Column | Meaning / representation |
| --- | --- |
| ID | Immutable, unique within this document. ASCII letters, digits, `.`, `_`, and `-`; begin with a letter or digit. Existing IDs such as `VO-026`, `ACKS-MD-0199`, and `S0.1` are valid. |
| Title | Nonempty short name, independent of ID and position. |
| Status | One of the values below. |
| Checkpoint | Nonempty testable completion condition or Markdown link to its contract. |
| Type | `slice` (default) or `epic`. |
| Priority | Empty or `P0`, `P1`, `P2`, `P3`; records the supplied priority only. |
| Owner | Free text naming the recorded assignee. |
| Dependencies | Comma-separated IDs in this document; empty means none. |
| Blocker | Free text or link describing the recorded impediment. |
| Evidence | Free text or Markdown links to verification and decision records. |
| Parent | One existing item ID, or empty. It does not imply a dependency. |

For new records, `S001`, `S002`, … is a useful convention. IDs are explicitly
supplied, never allocated from row position or renumbered on insertion. Preserve
existing identifiers when normalizing a project. No delete or rename command is
provided; retain obsolete records as `superseded` with an explanatory link.

Statuses are `planned`, `ready`, `assigned`, `in_progress`, `review`, `blocked`,
`done`, `deferred`, and `superseded`. They record the responsible agent's
decision. `assigned` distinguishes naming an owner from starting implementation;
`review` distinguishes review/integration work from accepted completion.
Project rules still govern what qualifies for each state. Normalizing a legacy
status requires an explicit semantic mapping, not case folding or inference.
Keep historical snapshots as dated evidence outside the current table.

Values occupy one physical line. Escape literal pipes as `\|` and literal
backslashes as `\\` within cells. Other Markdown, including links and inline
code, is retained. The CLI accepts literal strings and performs this escaping.
Keep long specifications and evidence in linked files instead of table cells.

Validation checks the format version, table shape, unique IDs/columns, required
values, enums, and references. Dependencies and parent links must refer to
existing IDs; duplicates, self references and cycles are errors. Validation does
not follow evidence links, assess acceptance, execute tests, decide readiness,
enforce transitions, infer approvals, or inherit dependencies from a parent.

## Commands

Run `python3 /path/to/implementation_tracker.py COMMAND ...`. Global `--file`
and `--json` options work before or after the command. Without `--file`, only
`./IMPLEMENTATION.md` is selected; no upward search or filename fallback occurs.
Parent directories must already exist.

- `init`: create a new empty tracker; any existing destination is an error.
- `list [--status STATUS] [--type slice|epic|all]`: return records in document
  order. Defaults to slices of all statuses. No scheduling decisions or sorting
  by presumed eligibility occur.
- `inspect ID`: return one complete record.
- `validate`: report structural validity and record count.
- `insert ID --title TEXT --checkpoint TEXT --expected-revision REVISION`:
  append a slice with status `planned`, or provide `--status` and other field
  options. `--before ID` or `--after ID` inserts at an explicit position.
- `update ID --expected-revision REVISION FIELD_OPTIONS`: change only supplied
  fields; at least one field option is required. ID is immutable.

Field options are `--title`, `--status`, `--checkpoint`, `--type`, `--priority`,
`--owner`, `--dependencies`, `--blocker`, `--evidence`, and `--parent`.
`--dependencies 'S001,S002'` replaces the whole dependency list. An empty string
clears an optional field; type defaults to `slice`. Unspecified update fields
are retained. Adding a previously absent column extends existing rows with their
defaults. Ordinary changes preserve other rows and all text outside the table;
the modified row is rendered in normalized spacing. LF or CRLF is preserved.

JSON success output contains `file` and `revision` (`sha256:` plus the hash of
the complete file bytes). List output has `slices`; inspect/insert/update have
`slice`; validation has `valid` and `count`. Mutations include `changed`.
Records use lowercase field keys; `dependencies` is a list, and absent optional
text fields are empty strings. A no-op update retains the file bytes/revision.
Human output also includes the revision for the next explicit write.

Exit codes: `0` success, `1` filesystem failure, `2` invalid input/format or
missing item, `3` stale revision, `4` writer lock busy. With `--json`, failures
emit an `error` object to stderr, including a machine-readable `code` and a
message. Stale errors include expected and actual revisions. Argument errors
use the same JSON envelope when `--json` is present.

## Concurrent writes and recovery

Writers take a sibling `.FILENAME.lock` file using exclusive creation, then
compare the complete current bytes with the expected revision. Paths are
resolved so symlink aliases use the same target and lock. Hard-linked tracker
files are refused for writes because distinct names cannot share this protocol.
A candidate is structurally validated before publication. A flushed temporary
file in the same directory is atomically published; updates preserve file mode.
The source is checked again immediately before publication to detect intervening
manual edits. Failed validation or stale revisions leave the tracker unchanged.

This protocol coordinates CLI writers to the same local filesystem path.
It is not a distributed lock across Git worktrees, cloud-sync replicas or hosts.
Manual editors can write outside the protocol, including in the final check/save
window. Do not claim protection against those writes or blindly retry decisions.

After a process crash, the sibling lock may remain. Inspect its PID/host record
and establish that the writer has stopped, retaining useful unfinished output,
before explicitly removing that exact lock. The helper never steals a lock.
Temporary files use `.FILENAME.*.tmp` in the target directory; after stopping
writers, inspect any crash leftovers before removing them. Neither locks nor
temporary files are state authorities or intended Git inputs.
