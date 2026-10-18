# Configure cross-model review in AGENTS.md

After collecting the user's missing model, effort, and authorization,
create or update the applicable `AGENTS.md` yourself using this template.
Use the file that governs the work, regardless of repository layout, and
preserve unrelated instructions. The user supplies choices and consent;
the agent constructs the command and edits the file. This template grants
no authorization itself.

The wording below illustrates standing authorization. Adapt it to the
provider, materials, reviewer activities, duration, and limits the user
actually agreed to. If consent is only for the current review, do not insert
this standing grant: record that restriction explicitly or retain the
one-review consent in the task context. Preserve existing valid settings
and update existing sections in place rather than duplicating them.

````markdown
### Cross-model-review instructions

Cross-model reviews requested under this project's workflow are authorized
to send repository changes, requirements, and relevant test evidence to
PROVIDER through the configured reviewer. Exclude credentials and unrelated
private records. Do not request approval again within this scope.

### Cross-model-review model

```bash
REPLACE_WITH_RESOLVED_REVIEWER_COMMAND
```
````

Replace `PROVIDER` with the authorized provider and the entire command
placeholder with the invocation you construct from the user's choices,
including the tool, separate model, effort, and read-only restrictions.
See [reviewer command examples](reviewer-commands.example)
for CLI-specific syntax and configuration checks. The command must use
`{packet}` and may use `{report}` and `{root}`. These expand to shell-quoted
absolute paths; do not add quotes around them. Keep credentials in the
CLI's stored authentication.

Existing authorization in the conversation also applies; do not ask the
user to repeat it. Host sandbox and approval controls remain in force.
