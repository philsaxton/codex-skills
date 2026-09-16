# Implementer evaluation — 2026-09-16

This bundle evaluates issue [#1](https://github.com/philsaxton/codex-skills/issues/1). Read [DISPOSITION.md](DISPOSITION.md) for the decision and evidence limits. The candidate under `treatments/implementer/` is an experimental input, not a shipped or activated skill.

## Inputs and execution

- `fixtures/` contains the raw tasks, project instructions, and starting files. Software starts with missing TSV registration; its failing test is intentional.
- `inputs.sha256.json` identifies the frozen raw inputs. `dispatch.json` records exact prompt construction, host-selected model/reasoning settings, fresh-context configuration, run identities, and treatment hashes.
- `treatments/narrow.md` isolates the provisional-requirements correction. `treatments/implementer/SKILL.md` adds the compact execution-owner guidance.
- `scoring.md` was written before inspecting evaluator outputs. It is not evaluator input.
- `results/` preserves the actual changed-file contents, evaluator handoffs/check records, input/output hashes, and parent verification. Full local fixture copies and recovered historical evidence are retained in the workspace's ignored artifacts area.

For each arm, copy each implementation fixture to a distinct permitted temporary directory, keeping source fixtures immutable. Supply only the task directory and the prompt in `dispatch.json`; substitute its path. The baseline has no treatment. In the other arms, copy the assigned treatment to `INSTRUCTION.md` and append the recorded suffix. Use fresh contexts with the recorded host model selection. Do not expose scoring, sibling outputs, historical findings, or disposition. Do not create a production installation to run the trial.

For boundary tasks, copy the fixture plus the candidate as `SKILL.md`; expose its name, description, and entry-point location through `CATALOG.md`. Use the separate boundary prompt. This tests explicit selection and observed task behavior, not automatic host discovery.

Inspect file changes against the frozen input, then rerun relevant checks on the resulting artifacts. Keep the raw exit status for `check_release.py`: 77 is unavailable evidence, never success. Evaluate meaning and authority rather than literal use of particular words. Preserve unfavorable results and check-script failures.

## Environment and scope

Nine implementation trials use three materially different cases and three guidance conditions. Three boundary trials cover planning, independent contract review, and a spelling correction. The software target and actual trial runtime are Python 3.12 (observed 3.12.2). The API reference is the official [Python 3.12 csv documentation](https://docs.python.org/3.12/library/csv.html); supplied opsctl help is synthetic fixture authority, not documentation for a real installed product.

The requesting host supplies system/developer guidance overlapping scope preservation, proportional verification, autonomy, and authority. Its available skill inventory includes Skill Creator and workspace helpers; the workspace exposes three selected skills and no active Superpowers links. Fresh agents receive no parent conversation history, but share the host instructions and filesystem. Directory boundaries are instructions, not OS isolation. Handoffs/check records are agent-produced evidence; parent verification independently checks the resulting files and executable behavior. Model selection is attested by dispatch parameters, not a backend model fingerprint.

These are small synthetic tasks, one sample per condition. They do not estimate success rates, prove general robustness, or cover production deployment, package adoption, security/licensing tradeoffs, difficult API migration, prolonged remediation, or automatic skill discovery. No policy relaxation, installation, publishing, or independent acceptance is part of this experiment.
