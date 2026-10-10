# Verifier fixtures — 2026-10-09

Three small, runnable projects for evaluating verification-method authoring and independent verification. They use Python's standard library, and the browser page needs only an existing browser tool. This bundle supplies evaluation inputs and organizer checks; it does not contain a new verification framework or a production installation.

## Boundary and layout

- `fixtures/` contains raw requests, project READMEs, data, and existing tests or guides. None contains seeded-defect labels or intended verdicts.
- `setup/products/` contains the known-good product files. `setup/variants.json` defines small reproducible faulty and follow-up variants. These are setup material, not reviewer input.
- `setup.py` combines a raw fixture and one product variant into an isolated project. Give reviewers only that resulting directory, plus the assigned candidate texts for a treatment arm.
- `scoring.md` fixes expected outcomes and scoring dimensions before trials. Keep it, this README, setup material, source hashes, and sibling results hidden from reviewers.
- `setup/prompts.md` gives neutral task templates for the organizer to adapt. Record the actual dispatched prompts separately.
- `inputs.sha256.json` freezes source files and each materialized project's expected file hashes.
- `self_check.py` checks the fixtures themselves. Raw preflight evidence is retained outside the application under the workspace’s ignored `artifacts/verifier-20261009/fixture-self-check/`. This check is not a skill trial and does not operate a browser.

`REQUEST.md` authorizes verification additions under `verification/` and forbids edits to product code, requirements, project instructions, and supplied inputs. It requires retained evidence and process cleanup. Requirements are ordinary user requests, not a prerequisite formal-contract workflow.

## Setup and run

From this evaluation directory, choose a fresh absolute run path outside this bundle:

```sh
python3 setup.py new cli good /absolute/path/to/runs/cli-good
python3 setup.py new http good /absolute/path/to/runs/http-good
python3 setup.py new browser good /absolute/path/to/runs/browser-good
```

Each target must not already exist. The script never initializes Git, installs packages, starts a server, or includes the scoring file. Variants are:

| Case | Variants |
|---|---|
| CLI | `good`, `wrong-total` |
| HTTP | `good`, `discount-regression`, `route-change`, `route-and-regression`, `missing-catalog` |
| Browser | `good`, `persistence-regression` |

From the resulting CLI project:

```sh
mkdir -p scratch
TMPDIR="$PWD/scratch" TMP="$PWD/scratch" TEMP="$PWD/scratch" PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 report.py --input data/invoices.csv --output scratch/report.json
cat scratch/report.json
```

From an HTTP project:

```sh
python3 checks/check_catalog.py
mkdir -p scratch
python3 server.py --port 0 --port-file scratch/server.port
```

The server stays running; its stdout gives the local URL. `api.json` gives the current route. Query from a second process or browser. From a browser project, use the same command with `serve.py`, then open the printed `http://127.0.0.1:PORT/` URL in an available browser. Its README uses ordinary visible controls and has no dependency on a particular automation library. Keep the server alive during interactions and stop only the process owned by that run.

Some hosts deny loopback binds in a filesystem sandbox. If so, preserve that preflight result and use the host's supported, narrowly scoped permission mechanism to run the local server. Give paired arms the same environment facts. A denied bind does not establish product behavior. This bundle binds only `127.0.0.1` and requires no external service, credentials, downloads, or publication.

## Follow-ups and cold reuse

Keep authored verification files and evidence before changing a run copy. The update action restores supplied baseline files and applies the chosen variant, preserving added `verification/` files:

```sh
python3 setup.py update cli wrong-total /absolute/path/to/runs/cli-good
python3 setup.py update http route-change /absolute/path/to/runs/http-good
```

Updates require the unchanged raw `REQUEST.md`. Do not use this operation as a reviewer or against an unrelated project. Preserve the initial run first so evidence and any prohibited edits cannot be overwritten unnoticed. For independent follow-up arms, copy the same initial handoff to separate run directories before applying a variant. Do not let a correction in one arm leak into another.

For a dirty-revision probe, the organizer may initialize a disposable run as a small independent Git repository, commit its initial supplied files, run the first review, then apply `update` without committing. Record the same HEAD and the relevant changed product bytes/diff. The materializer deliberately does not manage Git. A source/content fingerprint can test freshness without Git, but that does not exercise unchanged-HEAD/dirty-worktree handling.

Use fresh reviewer contexts for a cold handoff. Supply the current materialized project and the prior saved verification method; do not supply author conversation history, scoring, setup variants, or sibling findings. Keep the actual prompt, model/effort, skill hashes, commands, outputs, exit codes, final report, and changed verification files. If a reusable artifact needs a run-specific address, give both arms the actual local URL as an environment fact.

Keep retained trial results outside disposable scratch before cleanup. Check for active owned servers, inspect the exact task directory, and remove only that task's scratch. Do not delete the only saved method, logs, observations, or screenshots.

## Fixture self-check

Use a fresh work directory and a retained report path outside it:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 self_check.py --work /absolute/path/to/scratch/fixture-check --report /absolute/path/to/evidence/fixture-check.json
```

Exit 0 means the setup matches the prewritten oracle, including the expected failures in faulty variants. The report retains commands, outputs, observed HTTP results, server logs and stop status. It also checks that updates preserve added verification files and change product bytes. It leaves scratch for explicit inspection and cleanup. It does not execute JavaScript, click controls, or establish browser correctness.

The first recorded self-check was blocked by the host's loopback-bind restriction. A second run with narrow loopback permission matched all nine setup variants; all six servers it started were stopped. Python was 3.12.2. Both raw reports were moved intact to the retained artifact directory above. The browser variants still require actual browser trials.

The successful command, run from the verifier application worktree, was:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evals/verifier/2026-10-09/self_check.py --work /Users/phil-mac/Projects/skills-ws/tmp/verifier-20261009/fixture-author/self-check-loopback --report /Users/phil-mac/Projects/skills-ws/.worktrees/codex-skills/verifier/evals/verifier/2026-10-09/results/fixture-self-check-loopback.json
```

That report path was temporary; the retained report is now `artifacts/verifier-20261009/fixture-self-check/fixture-self-check-loopback.json` relative to the workspace. The earlier denied run used `self-check` in the work path and `fixture-self-check.json` as its report basename. For a new run, use a fresh disposable work path and a report path directly in retained artifacts.

These are small synthetic cases. They cover reuse, observable failures despite exit 0, missing methods, cold reuse, current dirty state, missing prerequisites, evidence retention, changed methods versus product regressions, and informal requirements. They do not establish statistical reliability, automatic skill discovery, production readiness, or security/performance coverage. Unrun follow-up conditions must remain untested in any outcome report.
