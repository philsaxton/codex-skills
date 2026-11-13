# Show Me Your Work validation — 2026-11-12

The candidate adds `show-me-your-work`, its append helper, tests, and optional
coordinator routing. Validation used the candidate on base
`5a87b0a170c3537efc9fd95dc38615ba1c990062`.

## Executable checks

`python3 -B tests/test_show_me_your_work.py -v` passed all eleven tests. Two new
quote regressions failed against the original helper before its correction.
The tests cover append-only history, seven-column decoding, quoted and
unmatched-quote text, later-row preservation, formula-prefix protection after
decoding, separators, literal shell text, incompatible headers, incomplete
final lines, argument-count refusal, viewer line separators, byte preservation,
and failure before any log write when timestamp generation fails. The latter
failure and line-separator regressions also failed before their corrections.

`bash -n show-me-your-work/scripts/log.sh`, `sh tests/test-link-skills.sh`,
both changed skills' `quick_validate.py` checks, and the tracked whitespace
check passed. The skill validator initially lacked PyYAML; rerunning with
PyYAML 6.0.3 in task-local temporary dependencies passed. No application runtime
dependency was added.

Tests ran with Python 3.12.2 and `/bin/bash` 3.2.57 on macOS arm64, with
`LC_ALL=C.UTF-8`. License text was compared with both pinned source licenses
from NOTICE and matched after ignoring trailing blank lines; the Codex port
preserves the same original copyright notice.

## Representative behavior

Four fresh Codex subagent contexts received realistic user requests, skill
metadata with explicit candidate paths, local instructions, and synthetic
export receipts. They did not receive expected answers or the prior review.
The implementing agent inspected their artifacts against criteria recorded
before each exercise. No application export tests were actually run by these
agents; distinguishing supplied receipts from execution was part of the task.

| Exercise | Observed behavior |
|---|---|
| Retained handoff | Created one TSV trail; preserved the failed attempt, reported pivot, and passing focused receipt; labeled reconstruction; withheld unsupported partner acceptance; linked the authoritative tracker. |
| Existing record | Extended the designated Markdown history without replacing earlier text or creating a duplicate TSV; retained uncertainty and the original failed attempt. |
| Ordinary update | Returned a concise evidence-qualified progress update without creating a decision trail. |
| Replacement agent | Preserved the inherited TSV prefix, used a new run label, and appended a correction identifying the unsupported success claim by run and line. It also disclosed an unavailable inherited handoff instead of claiming to have checked it. |

All four kept supplied inputs and the authoritative tracker unchanged. Their
output supports bounded skill-selection, reuse, and worker-handoff claims;
these first four exercises do not establish coordinator dispatch. It does not
establish broad reliability, automatic host discovery, multiwriter safety,
actual spreadsheet application behavior, or correctness of the synthetic
export implementation. The helper intentionally requires one writer and a
tab-delimited import with double-quote decoding.

Raw prompts, criteria, outputs, file identities, check receipts, and advisory
review history are retained in the workspace's ignored
`artifacts/show-me-your-work-finish-20261112-01a1d293/` cycle directory, outside
the disposable feature worktree. They are not required runtime resources.

## Evaluated source identities

The first four behavior trials used the initial quoted-TSV candidate below.
Their supported claims are carried forward: the later helper changes preserve
those ordinary inputs, and the later skill edits clarify encoding/retention
without changing the tested history, attribution, or evidence boundaries.
Final executable checks use the corrected candidate.

| File | Initial behavior candidate SHA-256 | Corrected candidate SHA-256 |
|---|---|---|
| `show-me-your-work/SKILL.md` | `14d2d3518d6ef0f0ed014ad90fe65e947974940908917621d80a864f613294a0` | `c5f227d2a0a624309427f402d1137646780349721f03245bda1a6276e0c2ecb0` |
| `show-me-your-work/scripts/log.sh` | `bd11ca079c9c91e9809975e71707111f5f8c5f7d0273d23b8b2270e4f59546a8` | `30902e0f73562f7295827ed6b0b5c48d044c51b69dcf44044a690f5b8daea63b` |
| `tests/test_show_me_your_work.py` | `09e7dcd64d816982f0db50eeb568ce31d40d0833a530e9cb3400cded5f5b99fd` | `28560a78820149b30cbc41b2e562aefe62e9fea0b7a1c231d84941c62f6a4be8` |
| `coordinator/SKILL.md` | `63900c36236afa54ba6fda90e3377995b8b2d1bed5889793236ef5d37f638759` | `022f54709ecd37b3eb7d61a55775ed8f4dccf133a07080a49a5b780d53331eec` |

## Coordinator dispatch follow-up

After the first Claude review identified the missing dispatch coverage, two
additional fresh contexts received frozen copies of the corrected coordinator
and a small catalog, following the assignment-proposal lane in
`evals/coordinator/README.md`. They were explicitly told to read that
coordinator, prepare exact task contracts, and launch no workers. Criteria were
recorded before dispatch. The evaluator read claims remain self-reported; the
parent inspected the actual proposals and checked frozen-file identities.

- **Requested week-long retained history:** Selected the skill, named the
  coordinator as sole canonical-trail writer, carried the same path outside
  the disposable checkout into both implementer and final-reviewer contracts,
  and routed attributed decisions/evidence back to that owner. Kept the issue
  authoritative and introduced no logging-specific review or approval gate.
- **Bounded two-role heading correction:** Used the existing issue, diff and
  reviewer result; selected no decision-trail skill and required no new log.
  No additional review stage was introduced.

Both proposals passed the predeclared criteria. The copies match the corrected
coordinator/skill identities in the table above. These observations establish
coordinator routing decisions and contract contents, not actual execution of
the proposed implementer/reviewer workflow.
