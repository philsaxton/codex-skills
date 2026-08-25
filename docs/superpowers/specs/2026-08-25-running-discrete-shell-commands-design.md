# Running Discrete Shell Commands

## Purpose

Create a lightweight, portable skill that reduces unnecessary approval pauses and makes shell commands easier for a user to inspect. The initial version should shape judgment without trying to classify every shell operator.

## Core contract

Each command tool call should express one small, coherent operation whose behavior is visible in the command itself.

- Run independently meaningful sequential operations in separate calls. Do not join them with `&&` or `;` merely to save tool calls.
- Allow a short pipeline when its stages form one readable data flow, with each stage directly consuming the preceding stage's output.
- Prefer literal arguments and explicit paths.
- Do not hide operations in variables, command substitution, heredocs, generated scripts, or shell functions merely for convenience.
- When an operation genuinely requires shell complexity, use the smallest transparent form and explain the necessity before requesting approval.

## Leading example

A routine Git sequence such as `git status`, `git diff`, `git add`, and `git commit` consists of independently meaningful operations. Run each in its own command call even though the sequence is predictable. This preserves command-prefix approval matching and lets the user inspect each action separately.

A pipeline such as a command whose output is immediately filtered remains one operation when the whole pipeline is short and readable. The skill will not impose a blanket pipeline ban.

## Artifact design

Create one self-contained `SKILL.md` under `running-discrete-shell-commands/`. Keep it concise, with no scripts or references. Automatic discovery remains enabled.

The description should trigger when an agent is about to run shell or command-line operations, especially chained Git commands, approval-sensitive commands, compound commands, heredocs, or shell indirection.

## Boundaries

This skill does not change sandbox configuration, approval rules, or command authorization. It does not imply that a separated command is safe or pre-approved.

Temporary-file placement is a separate concern. A future companion skill or instruction may direct agents to use a currently writable workspace or temporary root before requesting sandbox escalation, but that behavior is outside this skill.

## Evaluation

Treat this as a discipline-enforcing skill and test it before authoring:

1. Run baseline pressure scenarios without the skill, including a routine chained Git workflow, a readable pipeline, and a complex shell-indirection case.
2. Record whether agents chain independent commands, overcorrect by eliminating useful pipelines, or hide work in another shell construct.
3. Write the smallest skill that corrects observed failures.
4. Repeat the scenarios with the skill and tighten only demonstrated loopholes.
5. Validate the skill structure and confirm that the final wording stays lightweight.

## Success criteria

- Independent Git operations are issued separately.
- Short, coherent pipelines remain available.
- Commands are materially easier to inspect and approve.
- The skill does not create awkward workarounds or broaden execution authority.
- The skill remains concise enough to refine from real use.
