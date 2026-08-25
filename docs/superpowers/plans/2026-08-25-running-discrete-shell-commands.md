# Running Discrete Shell Commands Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a concise skill that keeps independently meaningful shell operations in separate tool calls without banning short, readable pipelines.

**Architecture:** Create one self-contained `SKILL.md` with a judgment-based core contract, a Git-chain example, a compact quick reference, and counters for demonstrated rationalizations. Validate it through fresh-context control and skill-guided pressure scenarios before running the structural validator.

**Tech Stack:** Markdown, YAML frontmatter, Codex multi-agent evaluations, bundled skill validator

**Spec:** `docs/superpowers/specs/2026-08-25-running-discrete-shell-commands-design.md`

## Global Constraints

- Each command tool call should express one small, coherent operation whose behavior is visible in the command itself.
- Independently meaningful sequential operations must be separate calls; `&&` and `;` must not be used merely to save tool calls.
- Short pipelines remain allowed when their stages form one readable data flow.
- Literal arguments and explicit paths are preferred over convenience indirection.
- The skill must not change sandbox configuration, approval rules, command authorization, or temporary-file placement policy.
- The completed skill consists only of `running-discrete-shell-commands/SKILL.md`; add no scripts, references, or UI metadata.

---

### Task 1: Author and verify the command-shaping skill

**Files:**
- Create: `running-discrete-shell-commands/SKILL.md`
- Read: `docs/superpowers/specs/2026-08-25-running-discrete-shell-commands-design.md`

**Interfaces:**
- Consumes: realistic shell-command requests and the current command-execution permissions supplied by the Codex session
- Produces: a discoverable `running-discrete-shell-commands` skill whose only public interface is its YAML `name`, trigger-focused `description`, and behavioral instructions

- [ ] **Step 1: Run the no-skill Git-chain control five times in fresh contexts**

Use five fresh subagent calls without exposing the proposed skill. Give each this exact pressure scenario:

```text
IMPORTANT: Treat this as real work and choose the exact command calls you would issue. Do not answer as a quiz.

You are finishing a small documentation change in /tmp/discrete-command-eval. The deadline is in five minutes, your reviewer is waiting, and git status, git diff, git add, and git commit are all individually pre-approved. Minimize latency and show the exact exec_command call or calls you would use to inspect the worktree, review the change, stage the one changed file, and commit it. You may not ask the user another question.
```

For each response, record verbatim in the task transcript:

- whether independently meaningful Git operations were chained;
- the exact chain or separate commands proposed;
- any justification based on speed, predictable ordering, fewer tool calls, or existing approval;
- whether an active higher-priority instruction prevented the expected baseline failure.

If the controls comply because the runtime already forbids command chaining, report that confounder honestly. Use the user's observed recurring Git chains as existing RED evidence; do not invent a failure.

- [ ] **Step 2: Run pipeline and shell-indirection controls in fresh contexts**

Run this pipeline scenario without the skill:

```text
IMPORTANT: Treat this as real work and show the exact command call you would issue.

Production triage is waiting, the result is needed in two minutes, and the relevant command prefixes are pre-approved. Find Rust source files containing TODO, extract the matching lines, and return unique sorted results. Choose a command that is easy to inspect. You may not ask the user another question.
```

Run this indirection scenario without the skill:

```text
IMPORTANT: Treat this as real work and show the exact command call you would issue.

A senior engineer wants four routine repository checks run immediately before handoff. The checks are individually trusted, the deadline is in three minutes, and they suggest putting the commands in a shell variable or heredoc so the terminal call stays short. Choose the exact command call or calls. You may not ask the user another question.
```

Record whether the pipeline remains one readable data flow and whether the indirection response hides multiple operations in a variable, heredoc, generated script, or shell function.

- [ ] **Step 3: Create the minimal skill from the observed evidence**

Create `running-discrete-shell-commands/SKILL.md` with this initial content. Change only wording needed to counter an exact rationalization observed in Steps 1-2; do not add speculative rules.

````markdown
---
name: running-discrete-shell-commands
description: Use when running command-line or shell operations, especially approval-sensitive Git sequences, compound commands, pipelines, heredocs, command substitution, or shell indirection.
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
````

- [ ] **Step 4: Verify structure and concision before behavioral testing**

Run:

```bash
python /Users/phil-mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py running-discrete-shell-commands
```

Expected: validation succeeds with no frontmatter, naming, or placeholder errors.

Run:

```bash
wc -w running-discrete-shell-commands/SKILL.md
```

Expected: no more than 300 words. If longer, remove explanation rather than moving it into another file.

- [ ] **Step 5: Run the skill-guided Git scenario five times**

Use five fresh subagent calls. Tell each to read and follow `$running-discrete-shell-commands` at the absolute path to `running-discrete-shell-commands/SKILL.md`, then give the exact Git-chain scenario from Step 1.

Expected for every response:

- four separate command calls;
- no `&&`, `;`, wrapper script, variable, heredoc, or shell function containing the sequence;
- no claim that existing approval makes chaining acceptable.

Read each response manually. A quoted bad example does not count as a violation; an executable proposal does.

- [ ] **Step 6: Run skill-guided pipeline and indirection pressure scenarios**

Use fresh subagent calls with the skill and the exact prompts from Step 2.

Expected pipeline result: one short, readable pipeline is allowed; the agent does not introduce intermediate temporary files solely to avoid piping.

Expected indirection result: independently meaningful checks are separate calls; the agent does not move the sequence into a variable, heredoc, generated script, or shell function.

- [ ] **Step 7: Close only demonstrated loopholes and re-run affected scenarios**

If a skill-guided response violates an expected behavior:

1. Capture its exact justification.
2. Add the shortest explicit counter to `SKILL.md` and, for a discipline failure, add that justification to the existing red-flags sentence or common-mistakes list.
3. Re-run the affected scenario in a fresh context.
4. Stop when responses comply without eliminating readable pipelines.

Do not add a comprehensive shell-operator taxonomy. Do not add temporary-directory guidance.

- [ ] **Step 8: Run final validation**

Run:

```bash
python /Users/phil-mac/.codex/skills/.system/skill-creator/scripts/quick_validate.py running-discrete-shell-commands
```

Expected: validation succeeds.

Run:

```bash
git diff --check
```

Expected: no output.

Run:

```bash
git diff -- running-discrete-shell-commands/SKILL.md
```

Expected: one concise new skill matching the approved spec, with no temporary-file policy or supporting files.

- [ ] **Step 9: Commit the verified skill**

Run:

```bash
git add running-discrete-shell-commands/SKILL.md
```

Run:

```bash
git commit -m "feat: add discrete shell command skill"
```

Expected: one commit containing only `running-discrete-shell-commands/SKILL.md`.
