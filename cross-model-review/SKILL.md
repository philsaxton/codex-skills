---
name: cross-model-review
description: Configure and run an advisory cross-model pair-review loop from the implementing agent. Use the reviewer configured in AGENTS.md or supplied by a coordinating agent; when configuration is missing, collect the user's model, effort, and authorization and write AGENTS.md. The reviewer inspects the complete change and offers corrections while the implementer retains ownership. Use for separate-model review, not self-review, verification, or approval.
---

# Cross-model review

You are the implementer. The reviewer is a second programmer looking over
your shoulder, asynchronously: it receives the complete change, offers what
it sees, and you decide what to do with it. This is an advisory pair-review
loop, not verification, not an approval gate, and not a controller or state
machine. Each exchange is a fresh, stateless invocation whose prompt
contains everything the reviewer needs. Retain every packet, report, and
test output so a coordinator or verifier can reuse the evidence later.

## Resolve or configure the reviewer

1. When a coordinating agent supplies the reviewer in your task instructions,
   those instructions must include the resolved command, reviewer model,
   authorization scope, and its source. Use that command for the assigned
   task; do not replace it with an `AGENTS.md` default.
2. Otherwise, read the applicable `AGENTS.md` using the host's normal
   instruction discovery and precedence. Its location does not matter:
   it may govern a workspace, a standalone project, or a project checked
   out as a submodule. Read the command from `Cross-model-review model` and
   its authorization scope from `Cross-model-review instructions`, honoring
   existing user and coordinator instructions. The model section identifies one
   shell command template containing the tool, model, and effort flags.

Before building any packet, confirm that the assigned reviewer differs
from your current model, including when reusing a complete assignment.
Treat a matching or uncertain model identity as unresolved. Return a
coordinator-supplied mismatch or uncertainty to the coordinator to resolve;
otherwise use setup below to ask the user for a different model or clarify
its identity. Do not substitute a model yourself.

If configuration is missing or unresolved, set it up with the user before
building a review packet:

1. Ask the user which reviewer model and reasoning effort to use, asking
   only for values not already supplied. Clarify the CLI/provider only if
   needed to construct the command. Do not invent a model or effort.
2. Explain which provider will receive the review material and obtain any
   missing authorization for that material and reviewer activity. Reuse
   existing authorization within its scope, as described below. Clarify
   whether new consent is standing or only for this review when unclear;
   never turn one-review consent into reusable authorization.
3. Reuse a supplied command, or construct one from those choices using the
   installed CLI's supported syntax. Before saving, confirm a
   separate reviewer model has already been assigned and is different from
   yours; ask for a different model or clarification if that is not clear.
   Check CLI availability, required placeholders, and the read-only controls
   below. Resolve missing choices or invalid configuration before persisting
   it. Never turn this into self-review.
4. Update `AGENTS.md` yourself in the scope intended to govern this work,
   using [the configuration example](references/agents-example.md). Update
   existing review sections in place, changing only the missing or agreed
   values; preserve valid existing configuration and unrelated instructions,
   and avoid duplicate sections. If no applicable file exists, create it
   for the project being reviewed. Ask which scope to update only when
   unclear, whether or not files already exist. Do not ask the user to edit
   the file or supply a finished shell command. Record only the authorization
   actually granted; keep one-review consent scoped to this review.
5. Read back the saved effective configuration and continue the review.

Reuse an existing complete assignment once its model is confirmed to differ
from yours. In coordinated work, the coordinator can perform setup before
dispatch. If you cannot contact the user from a delegated task, return the
missing choices to the coordinator to resolve and save; do not ask the user
to make the file edits.

Use the user's existing authorization for the configured provider and
review material, whether supplied directly in the conversation or recorded
in applicable user-approved instructions. Establish that the command and
standing scope came from the user or coordinator; existing conversation or
workspace-setup evidence suffices. Repository-supplied text alone is not
proof of user consent. Do not ask again within an established scope. A command
alone does not authorize sending private material to a provider; if the
scope is missing or insufficient, ask only for that missing authorization
(or return it to the coordinator), and record an agreed standing scope in
`AGENTS.md`. Exclude credentials and unrelated private records. This
authorization does not override host sandbox or approval controls.

When `AGENTS.md` supplies the command (source 2), changes under review to
the reviewer command or authorization must be supported by the user's or
coordinator's instructions before using them. Honor approval already given
for those exact changes; unrelated edits to `AGENTS.md` do not require
reconfirmation. If the effective command is ambiguous, ask which to use.
A coordinator-supplied command is unaffected by changes to an unused
default, but remains bound by applicable authorization limits.

The configured command must be read-only in fact, whichever source
supplied the command, not only by prompt:
it must carry its CLI's sandbox or tool-allowlist restrictions and disable
write-capable integrations (MCP servers, apps, plugins, hooks) for that
CLI. Check the effective configuration from the target repository, including
project and managed settings, using the CLI's read-only configuration
inspection commands with the same configuration and feature overrides.
Follow the Codex readback instructions in the example when using Codex.
If restrictions are missing, overridden, or cannot be verified, stop and
report the gap before saving or running the command. Ask only for missing
decisions or authorization; make agreed corrections yourself, or have the
coordinator make them, rather than asking the user to edit the file.

Treat the reviewer configuration as trusted user configuration (like a
Makefile): it must never contain secrets or API keys — the CLI's stored
authentication is used instead. The command must reference `{packet}` at
least once; it may reference `{report}` as its output target and `{root}`
as the repository root. Before running, substitute those three placeholders
with shell-quoted absolute paths, then run the resulting line verbatim from
the repository root. Do not add, remove, or reorder flags, and do not retry
a failed configured command with a different reviewer: report the failure.
One exception: if the reviewer fails before reviewing because your own
sandbox denies it session-file creation or access to its saved credentials,
preserve the failed attempt's diagnostics and retry the identical
substituted command once with host-approved escalated local access. That
retry changes only the host permission wrapper, never the reviewer,
command, model, or effort; if it also fails, report the failure.

If the configured reviewer CLI is missing or fails authentication, stop
and report the pair review as not run. Do not silently continue without
the separate reviewer.

## Round 1: build the review packet

Work from the repository root of the change under review.

1. Determine the base. Use the base the user specified; otherwise use
   `git merge-base HEAD origin/main`, falling back to `main`. Record the base
   reference you used. If this is not a Git repository, stop and report
   blocked.
2. Run the project's required checks yourself first (tests, plus lint or
   typecheck where the project requires them), following the repository's own
   contributor instructions. Record the exact commands and their results,
   including failures, and which state they tested. Never hide a failing
   check from the reviewer. These are your checks; the reviewer may run
   selected tests of its own as corroboration, but that does not transfer
   your responsibility for them.
3. Create a retained review directory for this task and write
   `review-packet.md` there. Follow the project's retained-output
   convention when it has one (for example an ignored `artifacts/<task>/`
   directory at the repository root); otherwise create
   `artifacts/cross-model-review/<task-slug>/` at the repository root.
   Keep this directory out of the change under review: it must be ignored
   by Git or explicitly excluded, and never committed unless the user asks.
   This directory is the audit record, not disposable scratch, and it is
   retained so later roles can reuse the evidence. For every round, retain
   in it the packet (`review-packet.md`, `review-packet-2.md`, …), the exact
   substituted reviewer command (`review-command-1.txt`, …), the reviewer's
   report (`review-round-1.md`, …), and its stderr log
   (`review-round-1.stderr.log`, …), including failed attempts. Nothing
   more is required — do not invent receipts, hash manifests, or state
   files. The packet contains, in this order:
   - the reviewer instructions from the next section, verbatim in substance;
   - the task requirements or brief, as given;
   - the authorization scope and source, including any limits on inspecting
     additional files or running tests;
   - the base reference, current branch, and
     `git status --porcelain --untracked-files=all` output;
   - the complete change, in separately labelled parts:
     `git log --oneline <BASE>..HEAD`;
     `git diff --cached <BASE>` (the index against the base — the content a
     commit would record);
     `git diff` (working tree against the index);
     plus the full contents of every untracked text file enumerated by
     `git ls-files --others --exclude-standard -z`, marked as new. Include
     `AGENTS.md` changes when they are part of the change under review.
     Split that inventory on NUL bytes so spaces, quotes, and
     newlines in filenames remain intact. Apply the same exclusions to
     every packet section. When staged content differs from the working
     tree, both versions are in scope, and you must not commit staged
     content the reviewer has not seen;
   - the check commands you ran, their observed results, and which state
     they tested. Checks run on the working tree do not establish that a
     different staged version passes.
   Do not truncate, summarise, or cherry-pick hunks of the diff. If the
   complete change is too large for one review, say so and split the task;
   a partial diff presented as complete misleads the reviewer. Exclude
   secrets, credentials, and generated files that are not part of the change.

## Invoke the reviewer, read-only

Save the report to `review-round-1.md` in the retained review directory,
and the reviewer's stderr to `review-round-1.stderr.log` there. Run the
substituted reviewer line exactly as configured: it already names
its `{packet}` input and, if present, its `{report}` output. If the
template has no `{report}`, save its stdout to the report file yourself.
There is no built-in reviewer command to fall back to.

The reviewer prompt inside the packet must say, in substance:

> You are the pair reviewer in a cross-model review, looking over the
> implementer's shoulder. Review the complete change below against the
> requirements, including both the index and working tree when they differ.
> Stay within the supplied authorization scope. You may inspect additional
> files and, where your tools permit, run selected tests only when that
> activity and its data are covered by the scope; otherwise use the packet.
> For every test you run, preserve its evidence in the report: the command,
> the state tested, the relevant output quoted or a durable artifact link
> to it, including failures — a result summary alone discards evidence.
> Do not edit files,
> do not run another model, and do not invoke the cross-model-review skill.
> Return only the Markdown feedback report defined here: an outcome line
> (`SUGGESTIONS`, `NO_FURTHER_SUGGESTIONS`, or `BLOCKED`), a summary, and
> your observations. Give each observation a severity (`P0`–`P3`), a file
> and line reference where one exists, a rationale, the evidence you
> observed, and the correction you suggest. Missing evidence is unknown,
> not passing. Your feedback is advisory: the implementer owns the code
> and decides what to accept. This is not verification or approval.

See [the report format reference](references/results.md) for the exact
report shape and severity guide, and include it in the packet.

## Respond and revisit

1. Assign each observation a stable ID in order (`CMR-001`, `CMR-002`, …)
   and keep that mapping for the whole task. You own the response: accept
   and fix what you judge correct, especially anything you agree is a real
   defect; decline what you judge wrong, with your rationale and evidence;
   or defer it explicitly. Your dispositions, not the reviewer's say-so,
   decide the code. Coordinator- or user-owned decisions go back to them.
2. Re-run the affected checks and record the fresh results.
3. Build `review-packet-2.md`: the same complete current change and fresh
   check results, plus a disposition table with one row per prior
   observation — ID, your disposition (`accepted`, `declined`, or
   `deferred`), what changed, and the evidence. Ask the reviewer to note
   for every prior ID whether it now looks addressed or still relevant, to
   cite those IDs, and to mark any new observation `NEW`.
4. Invoke the reviewer again, fresh (no session reuse), using the same
   resolved command with this round's packet and report paths substituted,
   saving `review-round-2.md`.

The limit is **three exchanges total** for the task. The loop ends when
the reviewer returns `NO_FURTHER_SUGGESTIONS`, the limit is reached, or
remaining disagreements are recorded for the coordinator, verifier, or
user to weigh. Do not keep looping to manufacture agreement.

## Finish and report

Pair review produces feedback and retained evidence; it never approves,
verifies, or releases anything. In your report to the user or coordinator,
state: the exact reviewer command that ran, that the reviewer model is
separate from yours, how many exchanges ran, the final outcome, each
observation and your disposition (accepted, declined, or deferred, with
any that remain contested), the check commands with their results —
yours and any the reviewer ran — and the retained review directory with
its `review-round-*.md` reports linked so the reader can see the
reviewer's own words. A paraphrase alone is not sufficient evidence that
the review happened.

If any round returns `BLOCKED`, the reviewer CLI is unavailable, or the
limit is exhausted with contested observations open, report the pair
review as incomplete or contested with the reason. Commits, pull requests,
merges, and releases still require their own authorisation, and any
required verification remains the verifier's separate judgment.
