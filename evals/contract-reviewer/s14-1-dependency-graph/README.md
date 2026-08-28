# S14.1 dependency-graph reviewer evaluation

> **Retired:** The oracle's expected dependency was disproved. See [DISPOSITION.md](DISPOSITION.md) before using this bundle; its frozen oracle and scoring are preserved only as provenance.

This fixture preserves a real reviewer failure for blinded regression testing of the portable `contract-reviewer` skill. It is evaluation material, not project authority and not a reusable project contract.

## Blinded input

- `artifacts/counterfactual-contract.md`
- the historical Git objects named in `source-boundary.md`
- `rerun-prompt.md`

Do not expose `oracle/`, either prior review, or either original FR-07 contract to the reviewer before its judgment is frozen.

## Comparison artifacts

- `artifacts/original-contract-v1.0.0.md` — the historical draft that received a blocking dependency finding.
- `artifacts/original-contract-v1.1.0.md` — the approved historical revision.
- `artifacts/original-review-history.md` — the original adverse review and successful re-review.
- `artifacts/review-project-role-run.md` — first blinded counterfactual review; approved with advisories and missed the target defect.
- `artifacts/review-portable-skill-run.md` — blinded portable-skill rerun; found other blockers but missed the target defect.

## Evaluation sequence

1. Give a fresh reviewer only the blinded input and permitted historical Git objects.
2. Freeze its review and record model, reasoning setting, elapsed time when measurable, hashes, and source access.
3. Unblind against `oracle/expected-findings.md`.
4. Score the run with `scoring.md`.

The baseline demonstrates failure before any reviewer-skill change: both counterfactual reviews missed the same executable dependency defect found in historical FR-07 v1.0.0.
