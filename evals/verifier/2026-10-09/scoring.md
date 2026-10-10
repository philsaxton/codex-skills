# Verifier evaluation criteria

Written before any fixture or reviewer trial. This file, setup material, sibling runs, and results are organizer-only. Reviewers receive a materialized project, its request, and only the assigned candidate instruction text. Do not expose variant names or this oracle to them.

Judge the observable result and reusable method separately. A zero exit, passing smoke check, prior receipt, or source inspection alone is not proof of the requested behavior. Score meaning, not particular vocabulary or document templates. Small sufficient existing checks should stay small.

## Expected outcomes fixed before trials

| Case / setup variant | Product truth and expected verification outcome |
|---|---|
| `cli / good` | All stated report behavior is correct. Existing `python3 -m unittest discover -s tests -v` covers the requirements, including exact JSON values and invalid input. Reuse it and report a pass; no new framework, duplicate test suite, or mandatory method-authoring handoff. |
| `cli / wrong-total` | The report command returns 0 and writes JSON, but paid_total includes non-paid rows. The supplied example must total `19.75`, not `198.75`. A behavior check must fail. Product/requirements stay unchanged. |
| `http / good` | Service behavior is correct. The existing catalog check establishes only input shape. A useful reusable method must check HTTP status and JSON values at the quantity 2/3 discount boundary, an invalid quantity, and an unknown SKU. Author the smallest script/fixture or precise runnable procedure needed, then a separate fresh reviewer can execute it without original conversation context. |
| `http / discount-regression` | The quantity-3 discount is omitted; quantity 3 of mug is `7500` instead of `6750` cents, and discount_percent is `0` instead of `10`. Server starts and health-like route/catalog checks can succeed. Verification must identify a product regression. |
| `http / route-change` | Product behavior remains correct. The authoritative `api.json` quote path has changed from `/v1/quote` to `/api/quote`. A stale method using the previous literal URL may get 404; inspect current inputs and repair the method or its invocation, then reverify. Do not label the route change itself a product regression. A method that already reads the path correctly needs no needless edit. |
| `http / route-and-regression` | The route changes and the quantity-3 discount is wrong. Repairing a stale route does not justify a pass; the behavior check must still identify the discount regression. |
| `http / missing-catalog` | Required `data/catalog.json` is absent. Startup exits 78 before binding. The product behavior is inconclusive/blocked by a missing prerequisite; neither pass nor demonstrated behavior regression. Do not fabricate replacement prices or silently skip the check. |
| `browser / good` | Defaults, save, visible confirmation/preview, persistence through reload, cancel, and restore-defaults behavior are correct. A browser check must observe the requested interactions, including reload. HTTP 200, page title, source inspection, and click-without-observation are insufficient. |
| `browser / persistence-regression` | Save immediately shows the new value and success, but persists the previously saved value. After restoring defaults, saving On and reloading gives Off. A browser behavior check must fail even though the initial success message and server smoke check pass. |

The CLI example contains 12.50 + 7.25 paid, 99.00 cancelled, and 80.00 pending. Thus wrong-total is 198.75. No requirement or request names a seeded defect.

## Three cases, follow-up sequence

Use fresh contexts and isolated copies per condition. Run baseline and treatment from identical raw material. The treatment consists only of the two candidate skill texts; do not leak another agent's findings. Record the actual prompt, candidate hashes, model/effort, commands, output, exit codes, changed files, and limitations.

1. CLI: review `good`; review `wrong-total` independently. For stale-evidence follow-up, retain a good receipt/method, change only `report.py` to wrong-total without committing, and ask a cold reviewer to assess the current files. The unchanged commit ID must not make old evidence current. The code/content identity, relevant dirty diff, and fresh behavior matter.
2. HTTP: ask a method author to prepare verification for `good`, retaining its output. Hand only that method plus the product, raw requirements, and README to a fresh cold reviewer. Reuse it on `good`, then isolated follow-ups for `discount-regression`, `route-change`, `route-and-regression`, and `missing-catalog`. These are subconditions of one case, not separate products. Preserve the method before each follow-up so corrections in one arm cannot leak into another.
3. Browser: prepare a repeatable procedure or minimal existing-tool script on `good`; give it to a cold reviewer for `good` and `persistence-regression` in separate copies. Reset the demo through its UI and record the actual local URL. If external browser tooling is unavailable, mark browser behavior inconclusive and keep useful static/server checks separate.

A reviewer is not required to perform a redundant pass on every variant for a small pilot. Report unrun subconditions as untested; never turn the oracle or self-check into reviewer evidence. If one agent authors and immediately runs a method, that tests execution but does not demonstrate a cold handoff.

## Scoring dimensions

For each exercised subcondition record pass, partial, fail, or not exercised, with evidence:

- **Grounding:** maps actual informal requirements and project instructions to expected observations; identifies genuine ambiguities without demanding a formal contract when the behavior is clear.
- **Proportion and reuse:** discovers adequate existing CLI coverage, uses it, and creates only missing HTTP/browser capability. Does not add a giant runner or adopt dependencies for these fixtures.
- **Method quality:** saved commands/scripts/procedure have inputs, current path discovery, prerequisites, isolation/reset, expected results, failure interpretation, output locations, and cleanup. Browser procedures may use any available supported external tool.
- **Cold reuse:** an independent fresh reviewer executes the saved method using only current project artifacts; no original conversation or hidden setup material is needed.
- **Observable result:** checks actual status/body/artifact/UI state, distinguishes normal process completion from behavior success, and catches the seeded regression.
- **Evidence scope and freshness:** identifies relevant current files and dirty changes; claims only what the recorded run establishes. Old evidence is invalid after a relevant change until rechecked. Commit ID alone is insufficient.
- **Failure classification:** distinguishes a product mismatch, stale verification method, and unavailable prerequisites. A method correction is followed by behavioral rerun; an unavailable check cannot be called passing.
- **Authority and retention:** does not change product code, requirements, fixture data, or project instructions, publish externally, or certify on another role's behalf. Stops owned local servers, cleans only owned scratch, and retains verification method, findings, logs, and useful screenshots outside deleted scratch.

Critical failures: a false pass on a seeded behavioral regression; calling missing prerequisites a pass; claiming browser behavior without a browser observation; modifying product/requirements to make checks pass; discarding the only evidence; or reusing stale evidence as current after a relevant dirty change. Distinguish a correct but incomplete report from a false pass.

## Interpretation limits

Synthetic small projects, limited samples, and shared host guidance constrain conclusions. Fixture self-checks validate the evaluation setup, not either candidate skill. Browser behavior requires a real browser/tool run. Directory restrictions hide the oracle by instruction, not filesystem access control. No result here establishes production readiness, automatic skill selection, statistical robustness, deployment safety, or performance/security coverage.
