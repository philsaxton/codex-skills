# Three-way completion guidance evaluation

See [results.md](results.md) for the completed comparison and disposition, [results.json](results.json) for hashed observations and independent scores, and [protocol.md](protocol.md) for the original criteria and disclosed amendment. The shared-rule arm reduced handoff-only repetitions beyond reviewer reuse in this bounded study. Delivery validation remains before any switch; this bundle does not install or activate a skill.

`setup.py` builds isolated trial directories from existing invoice fixtures and a supplied City of Vice checkout. It copies only the assigned guidance, adds execution recording, runs real initial checks, and prepares the specified evidence condition. It never writes to either source repository. City of Vice product files are private retained inputs, not copied into this application repository.

```sh
python3 setup.py \
  --application /absolute/path/to/codex-skills \
  --superpowers /absolute/path/to/pinned/superpowers \
  --city /absolute/path/to/city-of-vice-card-game \
  --output /absolute/path/to/retained/evaluation
```

The output contains `manifest.json`, copied guidance, neutral per-worker task contracts, isolated projects, and actual starting receipts. The manifest and setup code reveal treatment assignments and deliberately altered conditions. Give a worker only its assigned `TASK.md`. Keep the manifest, setup code, protocol, and sibling runs out of worker context. Workers may write only their own reports, evidence, and disposable scratch. Use a task-specific external scratch path in the environment where supported.

Project `check.py` records commands, exit status, full output, state hashes, stage, and actor. Test-file instrumentation also records direct suite invocation, so bypassing the wrapper does not hide an extra suite. It is observational instrumentation, not a sandbox against malicious evasion. Manual focused probes need retained output in the worker's report or evidence files. Hash checks detect prohibited source edits.

Results must distinguish fixture self-checks and setup executions from model trials. A successful setup is not an evaluation result.

The recorded run required a disclosed fixture amendment after the prototype exposed previously uncovered behavior. `amend.py` applies that amendment to an existing original bundle, taking the same source arguments as setup and `--bundle` instead of `--output`. It preserves the original inputs and manifest, adds the replacement CLI stage probe and SQLite case, and validates the SQLite checks against a duplicate-replacement mutation. See the amendment in the protocol; do not present it as an original preregistered fixture.

`self_check.py /absolute/path/to/bundle` validates initial fixture setup before model trials. `collect.py /absolute/path/to/bundle` gathers execution observations and checks protected-file hashes without grading reports or rerunning tests. These scripts refuse to reuse setup/self-check output directories where doing so could mix evidence.

Run the initial self-check before the amendment, which adds its own isolated SQLite mutation check under `preflight/`. Setup and self-check failures must be retained and identified separately from worker trials. The collector's focused-invocation count covers only calls that load the supplied audit helper; it is not an exhaustive count of custom checks. Inspect retained command receipts and reports for those checks.
