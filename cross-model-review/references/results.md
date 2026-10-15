# Markdown review report format

The reviewer returns one Markdown report and nothing else. The implementer
includes this reference in every review packet so both rounds use the same
shape. There is no JSON schema and no structured-output flag: the
implementer reads the report, assigns stable finding IDs, and tracks
dispositions in the next packet.

## Report shape

```markdown
Verdict: APPROVED | CHANGES_REQUESTED | BLOCKED

Summary: <one short paragraph: what was reviewed, against which
requirements, and the evidence behind the verdict>

Findings:
- [P1] path/to/file.py:42 — <short title>
  Rationale: <why this is a problem>
  Evidence: <what you observed: code, check output, or missing coverage>

Unknowns: <evidence you could not obtain, or "none">
```

On a re-review, cite the implementer's stable IDs for prior findings
(`CMR-001`, …) and state for each whether it is still open or closed, with
the evidence for closure. Mark any finding not seen before as `NEW`; the
implementer assigns it the next ID.

## Rules

- One finding per distinct issue. Use a concrete file and line where one
  exists; for a missing test or a cross-cutting issue, name the file or
  area and say what is absent.
- `Verdict: APPROVED` requires that the complete change was visible, the
  supplied check results pass, and no P0–P2 finding remains open. If any of
  that evidence is missing, use `CHANGES_REQUESTED` or `BLOCKED` — absence
  of evidence is unknown, not passing.
- `Verdict: BLOCKED` is for an incomplete diff, unreadable requirements,
  or a capability you were denied. Name the missing input.

## Severity guide

| Severity | Meaning |
| --- | --- |
| `P0` | Breaks the change's core purpose or risks data loss or a security breach; must fix. |
| `P1` | Wrong behaviour on a realistic path, or a required check failing; must fix. |
| `P2` | Real defect, missing required coverage, or a maintainability hazard with a concrete cost; must fix. |
| `P3` | Advisory: style, minor robustness, or optional improvement; may remain open. |
