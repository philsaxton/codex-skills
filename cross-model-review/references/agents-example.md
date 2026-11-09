# Configure cross-model review in AGENTS.md

Resolve the tool, any overrides, and authorization from the user or coordinator.
Use the governing AGENTS.md, preserve unrelated instructions and valid existing
choices, and record only the consent actually supplied. This example grants none.
Task-only exceptions belong in the assignment rather than standing configuration.

```markdown
### Cross-model-review instructions

Requested reviews may send the task's change, requirements and check evidence
to PROVIDER. Exclude credentials and unrelated private records.
This is standing authorization; do not ask again
within its scope. Tests remain the implementer's responsibility.

### Cross-model-review model

Use the installed cross-model-review skill's scripts/review.py with --tool muse.
Use its Wonder-Full/max defaults unless the assignment supplies an override.
Muse uses packet-only access unless this project authorizes read/search.
The implementer must supply its actual model identity, the brief, check evidence,
authorization scope, and one retained review directory for the task. Keep the
original review-round-*.md reports and link them in the finish report.
```

Replace PROVIDER, tool and overrides with the agreed choices. The available
tool defaults and complete command are in [runner.md](runner.md). Do not put
credentials into the file; native CLIs use their existing authentication.
Verify that the selected reviewer differs from the actual implementer before
invocation. A default collision requires a caller-owned selection change.

For authorized live reads, name the permitted files and exclusions in the
authorization. Claude's restricted file tools operate in its working directories.
Muse read/search and Codex can read beyond the repository. Codex retains a shell
in a read-only sandbox. Record those limits when they apply.
Set tool, model and effort once. A launcher that pins a selection must change
the pin to apply an authorized override.
