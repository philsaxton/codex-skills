# Verifier evaluation — 2026-10-09

This is a small behavioral pilot of [verifier](../../../verifier/SKILL.md) and [verification-method-author](../../../verification-method-author/SKILL.md). It evaluates new instructions directly; historical final-reviewer evaluations are not evidence for them.

No false pass or protected-input change was observed in the 11 application reviews. Candidate reviewers reused adequate checks, preserved and reran methods, detected the seeded defects, and kept unavailable behavior inconclusive. Baselines also reached correct conclusions in all four paired conditions. Three additional scope probes stayed outside the verification workflow. These results support the narrow V1 behavior, with the limits below.

## Design and identity

The application base was `5526d2473e32e412b79f0bbca778f8b7e60691e6`. The evaluated skill files were uncommitted additions, identified by SHA-256:

| Skill | SHA-256 |
|---|---|
| verifier | `78683c04e5c4ff2e3e42671b0dcf5ae772a7f3d40790b0025d10418f477a9dee` |
| verification-method-author | `4973e2bd67899d80838b1a284f2715584f95abf509871f286adddc1f0e2bbd8c` |

Each reviewer started with a fresh context (`fork_turns=none`), inherited model and reasoning settings, and no overrides or subagents. The collaboration interface did not expose the exact model identifier or effort value. Baseline and candidate prompts differed only by project path and the candidate's explicit skill-use suffix. Both received the same runtime facts and normal host guidance. Baselines used the project's existing request, README, tests, and smoke guide; they could create methods where the request allowed it.

[Scoring](scoring.md) was written before the trials. Reviewers received only materialized projects, not scoring, setup variants, sibling results, or author conversations. Ordinary cold transfers excluded earlier receipts and run evidence; the deliberate stale-evidence CLI probe retained its old receipt. Some method indexes consequently link to omitted receipts. This was an instruction-based access boundary, not filesystem isolation.

The runtime was Python 3.12.2 on macOS arm64, with the supported Codex in-app browser for actual UI interaction. Loopback execution required the host's narrow permission mechanism. Matching arms were told this environment fact. No packages or skills were installed.

## Paired results

All four paired conditions reached the correct current-application conclusion in both arms. These samples do not establish a general advantage over existing guidance.

| Condition | Existing guidance | Candidate skills |
|---|---|---|
| CLI with adequate supplied coverage | Passed the four supplied tests; added a 92-line wrapper with seven additional cases, including status variants and large decimal values. | Inspected and reused the four supplied tests, covering seven real CLI invocations. Added a receipt and evidence, without another harness. |
| Same CLI commit, dirty product change and old passing receipt | Detected the changed product hash and two fresh failures. | Recorded the dirty diff and current identity; rejected the earlier pass and reported the same two failures. |
| HTTP service lacking behavior checks | Authored a 190-line checker and 120-line control runner. Twenty HTTP cases and eight controls passed. | Authored a 181-line checker, a 96-line control runner, and a small independent acceptable-response fixture. Eighteen HTTP cases and three controls passed. |
| Browser behavior lacking interaction checks | Used a saved CUA helper and procedure; 25 current-application checkpoints passed. | Saved a manual browser procedure and isolated negative-fixture helper; 16 current-application checkpoints passed. A broken Save control failed after reload, and an unavailable-server control was inconclusive. |

The CLI defect still exited 0 but reported `198.75` instead of `19.75`, and `5.00` instead of `0.00` for pending-only input. Both cold reviewers caught the output errors. The unchanged commit ID did not make earlier evidence current.

The HTTP methods queried real servers and compared status and JSON values with the request. Both validated representative known failures and missing catalog input, retained denied sandbox attempts, and stopped their servers. Candidate validation used an independent fixed-response positive fixture and a quantity-boundary negative control. Its successful current run was not repeated solely for the verifier/method-author handoff.

Browser results came from actual controls, same-origin reloads, accessibility observations, and screenshots. HTTP serving and page title checks were kept separate. The candidate's negative copy displayed `Preferences saved.` and On immediately, but Off after reload; that contradicted the persistence requirement. Its stopped-server control retained connection-refused evidence rather than accepting a cached page. The baseline did not exercise a known-failure browser control in its initial trial.

The additional CLI cases in the baseline are a difference in review scope, not a correctness failure. The HTTP baseline also produced sound methods without the new skills. The narrower candidate CLI run and explicit candidate browser controls are useful observations, not statistical proof of improvement.

## Cold reuse and maintenance

Two additional HTTP reviewers received saved method sources and current project artifacts, without the method author's conversation or verdict:

- **Route drift plus product regression:** the organizer first calibrated a fixed `/v1/quote` method against its earlier service state: 18 cases passed. The configuration then changed to `/api/quote`, while the product's discount threshold regressed. The cold reviewer repaired route discovery, adapted the guarded negative control, and validated all three controls. Fresh HTTP evidence still failed mug and tea quantity 3: totals were 7500 and 3600 instead of 6750 and 3240. Sixteen other cases passed. Product files and the expected discount were unchanged.
- **Missing catalog:** the saved method returned inconclusive with exit 2 and zero HTTP cases. Direct startup returned 78. The reviewer did not fabricate catalog data, repair the product, or claim behavior passed. Evidence survived cleanup.

The route probe intentionally used a fixed-route historical method variation. The originally authored candidate checker already read configuration and would not itself have required that repair. The prior calibration is setup evidence, not an independent reviewer result. Old method sources and new method diffs/hashes are retained with the cold review.

A fresh browser reviewer received only the saved procedure/helper and a changed application. It discovered and ran that method, observing that Save appeared successful but reloading restored the previous choice in both directions. The reviewer reported a product failure, repaired a control helper whose source guard no longer matched, and exercised isolated acceptable and failing controls. The product under review stayed unchanged. Full browser observations were retained; screenshots have a narrow viewport and should not be read as a broad visual-layout evaluation. A final operational message asked the reviewer to retain that limitation instead of restarting solely for a clearer image.

## Scope boundaries

Three fresh reviewers received the optional skill descriptions rather than a forced invocation. Raw requests are retained in [fixtures/boundaries](fixtures/boundaries):

- Planning CSV export produced design tradeoffs, with no edits or verification workflow.
- Pre-implementation contract review identified unclear export scope and unmeasurable criteria, with no edits or runtime checks.
- A routine typo request changed only `verifcation` to `verification` in `overview.txt`.

All three selected neither skill. These are supplied-metadata routing probes; they do not establish automatic host discovery after installation.

## Evidence and checks

Raw outputs are retained in the workspace's ignored `artifacts/verifier-20261009/`. They are not dependencies of the portable skills. Exact prompts, agent names, initial file manifests, environment identity, and setup records are under `dispatch/` and `environment.json`.

| Evidence within that retained root | Meaning |
|---|---|
| `trials/cli-{baseline,candidate}/verification/` | Supplied-suite execution, scope decisions, receipts, hashes, cleanup. |
| `trials/cli-followup-{baseline,candidate}/verification/current-review/` | Fresh failures, dirty/current state and comparison with old evidence. |
| `trials/http-{baseline,candidate}/verification/` | Saved methods, actual HTTP responses, control results, denied attempts, cleanup. |
| `trials/http-followup-a/verification/current-review/` | Method repair, new method validation, current product failure and unchanged product identity. |
| `trials/http-followup-b/verification/current-review/` | Missing-input limitation, unsuccessful startup, zero HTTP cases and cleanup. |
| `trials/browser-{baseline,candidate}/verification/` | Real UI observations/screenshots, saved procedures, environment recovery and cleanup. |
| `trials/browser-followup/verification/current-review/` | Cold procedure reuse, Save failure after real reloads, method maintenance, isolated controls and cleanup. |
| `boundary-audit.json` | Only the requested typo changed in boundary probes. |
| `completed-trial-input-audit.json` | Comparison against the frozen protected inputs, including additions outside allowed output paths. |
| `fixture-self-check/` | Original denied preflight and successful nine-variant setup check. Six servers stopped; this check does not exercise UI. |
| `packaging/` | Ruby/Psych frontmatter/link checker and exact source identities. |

The fixture scripts were executed, including their update operation and all nine setup variants. The [input manifest](inputs.sha256.json) retains the original bundle identities. Boundary requests were prepared separately before their routing trials and later copied into the bundle. The standard skill-creator validator was unavailable because PyYAML was absent. An installed Ruby/Psych parser instead checked valid YAML, required fields, supported keys, names, description bounds, unfinished placeholders, whitespace, and relative skill links. Both skills passed. A separate fresh source reviewer found no actionable instruction defects; that read-only review is not runtime evidence.

## Design references and limits

The local pstack checkout was read at `ccb5507cec1546dc88135c1139c811e6c59115ba`, particularly its [creation workflow](https://github.com/cursor/plugins/blob/ccb5507cec1546dc88135c1139c811e6c59115ba/pstack/skills/create-verification-skill/SKILL.md) and [maintenance workflow](https://github.com/cursor/plugins/blob/ccb5507cec1546dc88135c1139c811e6c59115ba/pstack/skills/maintain-verification-skill/SKILL.md). Reuse, runnable procedures, evidence, cleanup, and distinguishing drift from regression informed the design. These skills instead keep methods in the project's existing artifacts and preserve this repository's requirement/reviewer boundaries. They introduce no shared CLI or running agent.

This pilot uses small synthetic projects and one sample per condition on a shared host. It does not establish statistical reliability, production readiness, automatic skill selection, or coverage of other browsers, platforms, library integrations, load, security, concurrent reviewers, or direct retirement requests. Not every setup variant had a separate reviewer trial, and candidate cold maintenance probes were not paired with baseline maintenance probes. Browser visibility-option and sandbox errors were retained and recovered; unavailable measurements were not credited as passes. No installation, support-pin changes, publication, automation, governance changes, or release gates were performed.
