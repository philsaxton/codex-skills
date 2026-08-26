---
name: running-discrete-shell-commands
description: Use when multiple independently meaningful operations, compound syntax, or indirection require command-shape decisions; exclude single direct commands and ordinary readable pipelines.
---

# Running Discrete Shell Commands

## Core rule

Each command tool call represents one small, coherent operation whose full behavior is visible in the command itself.

Run independently meaningful sequential operations in separate calls. Do not join them with `&&` or `;` merely to save tool calls. Predictable order does not make separate operations one operation.

A short pipeline is one operation when every stage directly transforms the preceding output and the complete data flow remains readable.

## Keep commands inspectable

Prefer literal arguments and explicit paths. Do not move a sequence into a variable, command substitution, heredoc, generated script, or shell function merely to hide or shorten the terminal call.

When one operation genuinely requires complex shell syntax, use the smallest transparent form and state why it is necessary before requesting approval.

## Quick reference

| Situation | Command shape |
|---|---|
| `git status`, then `git diff`, then `git add`, then `git commit` | Four calls |
| Search output immediately filtered or sorted | One short pipeline |
| Several checks that merely happen in order | Separate calls |
| Multiline logic required by the operation itself | Smallest visible form, with explanation |

## Common mistakes

- Calling a Git chain one operation because it is routine.
- Eliminating a useful pipeline and creating temporary-file workarounds.
- Moving a chain into a script, variable, or heredoc.
- Assuming separation makes a command safe or pre-approved. It does not change authorization.

## Red flags

“Fewer tool calls,” “these always run together,” and “put it in a script so it is shorter” are convenience arguments, not reasons to hide independent operations.
