---
name: cross-model-review
description: Run a cross-model review loop from the implementing agent — invoke the reviewer command configured in the repository's .reviewer-model file read-only to review the complete change, remediate its P0–P2 findings, and re-review, up to three reviews. If .reviewer-model is missing, stop and ask whether to create it or run the review without this skill. Use when the user asks for a cross-model, second-model, or independent-model review of a change, not for self-review or an unrelated code review.
---

# Cross-model review

You are the implementer and the orchestrator. There is no controller, packet
service, or state machine: you hold the context, run the other model's CLI
yourself, fix what it finds, and repeat. Each review is a fresh, stateless
invocation whose prompt contains everything the reviewer needs, so no session
needs to be resumed or recovered.

## Determine the reviewer command

Do not choose the reviewer tool, model, or effort yourself. The only
reviewer configuration is **`.reviewer-model` at the repository root**
(`git rev-parse --show-toplevel`).

If that file exists, it is the complete reviewer configuration: ignore
blank lines and lines starting with `#`; exactly one other line must
remain — a shell command template that already contains the tool, model,
and effort flags, for example for Codex, Claude, `muse`, or any other
model CLI. If zero or more than one command line remains, stop and report
the file as ambiguous rather than guessing. If `.reviewer-model` is itself
added or modified by the change under review, do not execute the
working-tree version; ask the user which configuration to trust.

### If `.reviewer-model` is missing: stop and ask

Do not fall back to a default reviewer and do not proceed with this loop.
Stop before building the packet and ask the user — with the host's
question mechanism if it has one, otherwise as a plain question — to
choose one of:

1. **Create `.reviewer-model`.** Show the example templates in
   [the reviewer-model example](references/reviewer-model.example) beside
   this skill and ask the user to supply
   the exact command line, including tool, model, and effort. Do not fill
   in a model or effort for them. Write only the line the user supplied,
   then continue this loop from the start.
2. **Run the review without this skill.** Leave this loop entirely and do
   an ordinary self-review instead. That review is not cross-model: do not
   use this skill's verdict format or claim cross-model approval for it,
   and state plainly in the final report that no cross-model review ran.

Wait for the answer. If no user can answer (for example an unattended
run), report the review as blocked on the missing `.reviewer-model`, list
the two options above, and stop.

The configured command must be read-only in fact, not only by prompt:
it must carry its CLI's sandbox or tool-allowlist restrictions and disable
write-capable integrations (MCP servers, apps, plugins, hooks) for that
CLI. If the line lacks those controls, ask the user to fix
`.reviewer-model` rather than run it.

Treat `.reviewer-model` as trusted user configuration (like a Makefile):
it must never contain secrets or API keys — the CLI's stored
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
and report that cross-model review is unverified. Do not review your own
change and call it cross-model, and do not silently continue without a
reviewer.

## Round 1: build the review packet

Work from the repository root of the change under review.

1. Determine the base. Use the base the user specified; otherwise use
   `git merge-base HEAD origin/main`, falling back to `main`. Record the base
   reference you used. If this is not a Git repository, stop and report
   blocked.
2. Run the project's required checks yourself first (tests, plus lint or
   typecheck where the project requires them), following the repository's own
   contributor instructions. Record the exact commands and their results,
   including failures. Never hide a failing check from the reviewer.
3. Create a retained review directory for this task and write
   `review-packet.md` there. Follow the project's retained-output
   convention when it has one (for example an ignored `artifacts/<task>/`
   directory at the repository root); otherwise create
   `artifacts/cross-model-review/<task-slug>/` at the repository root.
   Keep this directory out of the change under review: it must be ignored
   by Git or explicitly excluded, and never committed unless the user asks.
   This directory is the audit record, not disposable scratch. For every
   round, retain in it the packet (`review-packet.md`,
   `review-packet-2.md`, …), the exact substituted reviewer command
   (`review-command-1.txt`, …), the reviewer's report
   (`review-round-1.md`, …), and its stderr log
   (`review-round-1.stderr.log`, …), including failed attempts. Nothing
   more is required — do not invent receipts, hash manifests, or state
   files. The packet contains, in this order:
   - the reviewer instructions from the next section, verbatim in substance;
   - the task requirements or brief, as given;
   - the base reference, current branch, and
     `git status --porcelain --untracked-files=all` output;
   - the complete change, in separately labelled parts:
     `git log --oneline <BASE>..HEAD`;
     `git diff --cached <BASE>` (the index against the base — the content a
     commit would record);
     `git diff` (working tree against the index);
     plus the full contents of every untracked text file enumerated by
     `git ls-files --others --exclude-standard`, marked as new — excluding
     `.reviewer-model` itself, which is reviewer configuration, not part of
     the change. When staged content differs from the working tree, both
     versions are in scope: approval must cover the index content, and you
     must not commit staged content the reviewer has not seen;
   - the check commands you ran and their observed results.
   Do not truncate, summarise, or cherry-pick hunks of the diff. If the
   complete change is too large for one review, say so and split the task;
   a partial diff reviewed as if complete is a false approval. Exclude
   secrets, credentials, and generated files that are not part of the change.

## Invoke the reviewer, read-only

Save the report to `review-round-1.md` in the retained review directory,
and the reviewer's stderr to `review-round-1.stderr.log` there. Run the
substituted `.reviewer-model` line exactly as configured: it already names
its `{packet}` input and, if present, its `{report}` output. If the
template has no `{report}`, save its stdout to the report file yourself.
There is no built-in reviewer command to fall back to.

The reviewer prompt inside the packet must say, in substance:

> You are the read-only reviewer in a cross-model review. Review the complete
> change below against the requirements. Do not edit files, do not run
> another model, and do not invoke the cross-model-review skill. Return only
> the Markdown report defined here: a verdict line (`APPROVED`,
> `CHANGES_REQUESTED`, or `BLOCKED`), a summary, and findings. Give each
> finding a severity (`P0`–`P3`), a file and line reference where one exists,
> a rationale, and the evidence you observed. Missing evidence is unknown,
> not passing. Approve only if the change satisfies the requirements and no
> P0–P2 issue remains; P3 findings are advisory.

See [the report format reference](references/results.md) for the exact
report shape and severity guide, and include it in the packet.

## Remediate and re-review

1. Assign each finding a stable ID in order (`CMR-001`, `CMR-002`, …) and
   keep that mapping for the whole task. Fix every P0–P2 finding. P3
   findings are advisory; fix them or note why not. A finding you dispute
   stays open with your rationale and evidence — only the reviewer closes
   findings.
2. Re-run the affected checks and record the fresh results.
3. Build `review-packet-2.md`: the same complete current change and fresh
   check results as round 1, plus a disposition table with one row per prior
   finding — ID, your disposition (`fixed`, `disputed`, or `deferred`),
   what changed, and the evidence. Instruct the reviewer to re-assess every
   prior ID as still open or closed, to cite those IDs, and to mark any new
   finding `NEW`.
4. Invoke the reviewer again, fresh (no `--resume`, no session reuse),
   using the same resolved command with this round's packet and report
   paths substituted, saving `review-round-2.md`. Repeat once more if
   needed.

The limit is **three reviews total** for the task. Keep your own count in
your working notes; nothing else enforces it. When the limit is reached with
P0–P2 findings still open, stop and report them to the user instead of
looping further or approving yourself.

## Finish and report

The change passes cross-model review only when the reviewer's verdict is
`APPROVED` and your own required checks pass. In your final report to the
user, state: the exact reviewer command that ran (the `.reviewer-model`
line after substitution), how many rounds ran,
the final verdict, each finding and how it closed (or that it remains open,
disputed, or deferred), and the check commands with their results. Name
the retained review directory and link its `review-round-*.md` reports so
the user can read the reviewer's own words; a paraphrase alone is not
sufficient evidence that the review happened.

If any round returns `BLOCKED`, the reviewer CLI is unavailable, or the
limit is exhausted, report the cross-model review as incomplete with the
reason. Never present an unreviewed or partially reviewed change as
approved. Commits, pull requests, merges, and releases still require their
own authorisation; a review approval does not grant it.
