# Configure cross-model review in AGENTS.md

Keep the reviewer command and standing authorization together in the
applicable project or workspace `AGENTS.md`. Use the user's agreed values;
ask only for missing details. This template grants no authorization itself.

````markdown
### Cross-model-review instructions

Cross-model reviews requested under this project's workflow are authorized
to send repository changes, requirements, and relevant test evidence to
PROVIDER through the configured reviewer. Exclude credentials and unrelated
private records. Do not request approval again within this scope.

### Cross-model-review model

```bash
REPLACE_WITH_USER_SUPPLIED_COMMAND
```
````

Replace `PROVIDER` and the entire command placeholder with the user's
authorized provider and exact command, including the tool, separate model,
effort, and read-only restrictions. See [reviewer command examples](reviewer-commands.example)
for CLI-specific syntax and configuration checks. The command must use
`{packet}` and may use `{report}` and `{root}`. These expand to shell-quoted
absolute paths; do not add quotes around them. Keep credentials in the
CLI's stored authentication.

Existing authorization in the conversation also applies; do not ask the
user to repeat it. Host sandbox and approval controls remain in force.
If migrating from `.reviewer-model`, move the agreed command into these
sections; the skill no longer reads the old file. Retire that obsolete
file when authorized, preserving any unrelated content.
