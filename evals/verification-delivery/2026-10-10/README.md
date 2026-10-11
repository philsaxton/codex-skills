# Completion-rule delivery evaluation

Read [results.md](results.md) and the [independent assessment](assessment.md) for outcomes, limitations, and the activation hold. A missed local parser defect and an assisted merge remain part of the evidence.

Read [protocol.md](protocol.md) for the frozen gates and [guidance-manifest.json](guidance-manifest.json) for the exact guidance identities. This is a delivery extension to the earlier [three-way comparison](../../verification-completion/2026-10-10/results.md), using its C wording unchanged. [The explicit implementer companion](explicit-dispatch-extension.md) records a pre-dispatch coverage addition.

All projects, runtime files, raw command receipts and model event streams are retained outside the application repository. Active consuming-project installations are not changed. The fixture repositories have no remotes and are not development worktrees for a real application.

To materialize a fresh retained run directory:

```sh
python3 setup.py --output /absolute/retained/run --superpowers /absolute/pinned/superpowers
python3 boundaries.py --output /absolute/retained/run --superpowers /absolute/pinned/superpowers
```

Use Superpowers revision `bb92a77741419a4ab5f06e711a283343f1ada0c3` and the application role bytes identified in the manifest. `setup.py` resolves the application from this bundle's location. Compare the generated guidance hashes before dispatch if reproducing after later skill changes. `variants.json` is organizer-only and is excluded from worker projects. `boundary-preparation.json`, the protocol, and sibling cases must also remain outside worker scope.

Each CLI invocation is a fresh context with a natural prompt. Example:

```sh
python3 run.py /absolute/retained/run P01 implementer
python3 run.py /absolute/retained/run P01 reviewer
python3 run.py /absolute/retained/run P01 controller
```

Run roles serially within a project and independently across projects. Check that a role finished and saved its report before dispatching its successor. P01's handoff also presents a shortened output excerpt linking to its complete receipt; preserve the original report and evidence. P02's controller performs an actual isolated merge and the required post-merge suite. R02 has author and contract-reviewer assignments in the same project, in separate contexts. B02 has a reviewer and an unchanged-state controller handoff. Other CLI boundary cases have one reviewer or the indicated document/design/method role.

D01 and R06 use fresh native subagents with no inherited conversation. Their starting prompts carry the absolute project, AGENTS, canonical completion and selected skill paths, and the task file. Record this as explicit delivery, not automatic discovery. The organizer copies the task into TASK.md and sets `.owner` before dispatch. Do not give workers the grader's expected outcomes or failure mutations.

`run.py` retains stdout JSONL, stderr, final answer, timing and invocation metadata. It uses the installed CLI and configured model without a model override, separate supported runtime/log directories, ephemeral sessions, and a workspace sandbox with approvals disabled. On this host the CLI process needed outer startup permission; inner sandbox restrictions remained enabled. Optional configured connectors produced startup warnings; those warnings are infrastructure output, not application test failures. Never publish runtime databases or raw configuration: they can contain unrelated host metadata.

`check.py` records actual commands, outputs, exit status, source/test/input/dependency hashes and relevant environment. Test invocation logs and worker command events also expose direct test runs. `collect.py /absolute/retained/run` creates a private observation index for assessment; it does not automatically declare tests or skills successful. Independent assessment reads the actual reports, edits and raw evidence.

The receipt fixture's [scope manifest](fixtures/receipt-app/verification_scope.json) and [control map](fixtures/receipt-app/variants.json) describe its checks and setup-only controls. Fixture preflight is separate from model trials. B07 later found an invalid-JSON defect outside those passing controls; the original fixture is preserved. The [assisted merge record](assisted-merge.md) includes P02's blocked result and exact continuation assignment. P01's display used the first 120 characters of passing output, a truncation label, and the complete receipt's actual path; the original implementer report remained accessible.

After all workers finish, `export.py /absolute/retained/run results.json` publishes execution identities and metadata without raw runtime files. Record observed model/host settings in the private manifest before dispatch; the setup scripts do not infer them. Review exported content before publication. Independent assessment still reads the raw evidence rather than treating process exit status or a wrapper receipt as a verdict.
