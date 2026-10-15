---
name: pr-walkthrough
description: Guide a human through a pull request, branch diff, or commit one section at a time, explaining the code and unfamiliar language or framework concepts as needed. Use for understanding changes through conversation, rather than an autonomous defect audit.
---

# PR Walkthrough

Help the human understand a change well enough to review it, including code in languages or frameworks they are learning. Default to concise explanations and let follow-up questions determine the depth.

## Establish the comparison

Read applicable repository guidance, resolve the requested change, and inspect the diff and enough surrounding code to understand its behavior. Record the base and head revisions. When a supplied commit could mean either that commit alone or the combined branch changes, inspect both scopes and clarify a material ambiguity before starting.

Reuse the human's stated background and preferences. Otherwise assume general programming familiarity and explain unfamiliar language or framework details as they become relevant. Ask a brief calibration question only when it would materially improve the explanation; do not require a lengthy intake.

Walkthroughs are read-only unless the human requests further actions. Do not run setup, cleanup, or other mutating application commands merely to demonstrate them. Explaining a change does not authorize posting feedback, approving, merging, or fixing it.

## Orient, then show one section

Start with a short summary of what changes and a compact reading order. Group related hunks by behavior, including callers, tests, or other files when they clarify the same change. Account for the whole comparison; explicitly identify grouped mechanical or generated changes instead of silently skipping them. Split large groups into smaller steps.

Present the first section, then stop. For each section:

- Give it a recognizable number and behavior-focused title.
- Identify the relevant inputs and where they come from. When introducing a function, show or briefly explain one real caller and its arguments. If a framework invokes it, explain that entry point. Do not leave parameter names as the only explanation of their values.
- Show a focused, faithful diff in chat. Retain enough context to make the change understandable; label excerpts and omissions. Keep illustrative rewrites or pseudocode separate from the actual diff.
- Explain the before-and-after behavior in a short paragraph. Add only the syntax or framework detail necessary to follow this section. Avoid front-loading a glossary, every operator, or all possible edge cases. Reuse concepts already explained.
- Link to the relevant native diff when supported and verified. Otherwise provide a precise source link, labeled as source rather than diff. Keep links consistent with the reviewed revision; a local branch may differ from a published PR.

A small example or table can resolve a specific confusion. It is not a required part of every section. Keep the initial explanation short even when substantial surrounding investigation was needed.

## Follow the human's pace

After a section, wait. Advance when the human says "next," requests another section, or otherwise asks to continue. Answer questions about the current section without automatically appending the next one. Agreement such as "got it" alone does not require advancing.

Answer the specific question first, at the requested depth. Trace an argument back to its caller, a value to its producer, or an effect to its consumer when that is the missing context. Distinguish language conventions from behavior introduced by the application. If the human requests more detail or a faster overview, adapt accordingly.

Keep the comparison, current section, covered changes, open questions, and established background in conversation context. Resume the same section after a tangent unless asked to move on. Use the host's existing chat, side-chat, and review features; no custom interface is required. Do not assume conclusions from a separate side chat are available unless they are actually in context.

When returning to source after a pause, check for revision changes. Keep the pinned comparison or explicitly agree on a new one; do not mix explanations from different revisions silently.

## Keep explanations grounded

Separate observed code behavior, inferred author intent, and unresolved questions. Read the actual caller, configuration, or test when it is needed to substantiate an explanation. Briefly flag a material concern discovered during the walkthrough, while keeping the requested focus on understanding.

Do not present a plausible explanation as proof of correctness. Distinguish tests read from tests run. Use a small isolated demonstration only when it helps resolve a specific uncertainty, and identify simulated results as such.

After the final section, give a brief recap of the overall change and remaining questions. Describe what was covered and any verification limits; completing the walkthrough does not itself establish approval or a clean defect review.
