# Configure cross-model review in AGENTS.md

Resolve the tool, any overrides, and authorization from the user or coordinator.
Use the governing AGENTS.md, preserve unrelated instructions and valid existing
choices, and record only the consent actually supplied. This example grants none.
Task-only exceptions belong in the assignment rather than standing configuration.

```markdown
### Cross-model-review instructions

Requested reviews may send the task's change, requirements and check evidence
to PROVIDER, and inspect relevant repository files read-only. Exclude credentials
and unrelated private records. This is standing authorization; do not ask again
within its scope. Tests remain the implementer's responsibility.
Record the selected adapter's limits: Muse/Codex reads can extend beyond the
repository, and Codex retains shell execution in a read-only sandbox. Live-read
exclusions and the no-tests rule are instructions, not filesystem/command filters.
They remain binding; this consent does not permit tests or out-of-scope reads.
Use stronger isolation when the assignment requires it. Claude's restricted
file tools additionally confine reads to its working directories.

### Cross-model-review model

Use the installed cross-model-review skill's scripts/review.py with --tool muse.
Use its Wonder-Full/max defaults unless the assignment supplies an override.
The implementer must supply its actual model identity, the brief, check evidence,
authorization scope, and one retained review directory for the task. Keep the
original review-round-*.md reports and link them in the finish report.
```

Replace PROVIDER, tool and overrides with the agreed choices. The available
tool defaults and complete command are in [runner.md](runner.md). Do not put
credentials into the file; native CLIs use their existing authentication.
Verify that the selected reviewer differs from the actual implementer before
invocation. A default collision requires a caller-owned selection change.

Existing native command templates remain supported; follow
[legacy.md](legacy.md) and [reviewer-commands.example](reviewer-commands.example).
Do not silently rewrite their flags or authorization. For those templates,
{packet}, {report} and {root} still mean shell-quoted absolute paths.
