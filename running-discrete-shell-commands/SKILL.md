---
name: running-discrete-shell-commands
description: Use when multiple independently meaningful operations, compound syntax, or indirection require command-shape decisions; exclude single direct commands and ordinary readable pipelines.
---

# Running Discrete Shell Commands

## Core rule

Each command tool call represents one small, coherent operation whose full behavior is visible in the command itself.

AGENTS.md remains authoritative. Don't silently override it.

Run independently meaningful sequential operations in separate calls. Do not join them with `&&` or `;` merely to save tool calls. Predictable order does not make separate operations one operation.

A short pipeline is one operation when every stage directly transforms the preceding output and the complete data flow remains readable.

## Keep commands inspectable

Prefer literal arguments and explicit paths. Do not move a sequence into a variable, command substitution, heredoc, generated script, or shell function merely to hide or shorten the terminal call.

When one operation genuinely requires complex shell syntax, use the smallest transparent form and state why it is necessary before requesting approval.

## Examples

| Situation | Command shape |
|---|---|
| `git status`, then `git diff`, then `git add`, then `git commit` | Four calls |
| Search output immediately filtered or sorted | One short pipeline |
| Multiline logic required by the operation itself | Smallest visible form, with explanation |
| Put independent actions in a helper to shorten the call | Keep the actions visible in separate calls |

Keep useful pipelines; do not replace them with temporary-file workarounds. Command separation does not make an operation safe or pre-approved and does not change authorization.
