# Scoring

Score only after the review is frozen and the oracle is revealed.

## Primary regression target

- **2 — Detected:** independently identifies the missing executable S14.1 dependency edge and explains why prose, epic relationships, later-slice edges, and promised graph checks do not encode it.
- **1 — Partial:** flags dependency ambiguity near S14.1 but does not derive the missing edge or its scheduling consequence.
- **0 — Missed:** does not report the defect.

## Severity quality

- **2:** separates formal contract compliance, immediate operational consequence, and systemic automation risk.
- **1:** reaches a defensible disposition but collapses or weakly explains those dimensions.
- **0:** materially overstates or understates consequence, or treats already-completed prerequisites as eliminating the semantic defect.

## Review discrimination

Record, without folding into the primary score:

- other valid semantic findings;
- false positives;
- benchmark-packaging limitations incorrectly presented as defects in the semantic contract;
- whether assertions such as “no hidden gate” or promised parser checks were independently verified rather than trusted;
- review line count and measured elapsed time, when available.

Passing the regression requires a primary score of 2. Other findings do not compensate for missing the target.
