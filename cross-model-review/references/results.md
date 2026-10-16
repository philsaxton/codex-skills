# Markdown pair-review feedback format

The reviewer returns one Markdown feedback report and nothing else. The
implementer includes this reference in every review packet so both rounds
use the same shape. The report is advisory feedback from a second pair of
eyes: it is not a verification judgment and it approves nothing.

## Report shape

```markdown
Outcome: SUGGESTIONS | NO_FURTHER_SUGGESTIONS | BLOCKED

Summary: <one short paragraph: what was reviewed, against which
requirements, and what the feedback rests on>

Observations:
- [P1] path/to/file.py:42 — <short title>
  Rationale: <why this may be a problem>
  Evidence: <what you observed: code, or tests you actually ran and
  their results>
  Suggested correction: <what you would change>

Tests run: <for each test: command, state tested, and the relevant
output quoted or a durable artifact link to the full output, including
failures — or "none">
Unknowns: <evidence you could not obtain or questions you need
answered, or "none">
```

On a revisit, cite the implementer's stable IDs for prior observations
(`CMR-001`, …) and note for each whether it now looks addressed or still
relevant, with the evidence for your view. Mark any observation not seen
before as `NEW`; the implementer assigns it the next ID. Restate a
disagreement plainly if you still see it — the implementer, coordinator,
or user weighs contested items; nobody needs your permission to proceed.

## Rules

- One observation per distinct issue. Use a concrete file and line where
  one exists; for a missing test or a cross-cutting issue, name the file
  or area and say what is absent.
- Report only tests you actually ran. For each one, preserve the
  evidence: command, state tested, and the relevant output quoted in the
  report or a durable artifact link to the full output, including
  failures. A pass/fail summary without output or a durable artifact
  link discards evidence the implementer is meant to retain. Supplied
  check results are the implementer's evidence; say when you are relying
  on them rather than rerunning them.
- When the index and working tree differ, cover both versions. Check
  results establish only the state they actually tested.
- `NO_FURTHER_SUGGESTIONS` means you see nothing more material to offer;
  it is not approval and does not verify the change. `BLOCKED` is for an
  incomplete diff, unreadable requirements, or a denied capability —
  name the missing input.

## Severity guide

Severity signals how much attention an observation deserves; it does not
create a gate.

| Severity | Meaning |
| --- | --- |
| `P0` | Likely breaks the change's core purpose or risks data loss or a security breach. |
| `P1` | Likely wrong behaviour on a realistic path, or a required check failing. |
| `P2` | Probable defect, missing coverage, or a maintainability hazard with a concrete cost. |
| `P3` | Minor or optional: style, small robustness, or polish. |
