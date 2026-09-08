---
name: workspace-setup
description: Set up an agent workspace (the garage) around independent application repositories, including local scratch and worktree locations, or reorganize existing work to separate application code, generated artifacts, and agent support. Use for workspace setup and domain separation, not routine feature work or Git branch/worktree cleanup.
---

# Set up the garage

The workspace is the garage; applications are the things built inside it. Give application code, generated work, and agent support distinct homes while keeping each application usable by someone with a different garage.

## Inspect and choose the path

Read the request and applicable instructions. Inspect the starting directory, including hidden files, Git roots and tracked files, existing application repositories, and actual write permissions. Resolve relevant symlinks before treating a path as inside the workspace.

- **New workspace or additive setup:** Follow the setup steps below when existing work can remain in place.
- **Existing content needs separation:** Read [refactoring guidance](references/refactoring.md) before planning or applying moves, index changes, or path rewiring. For governed projects, use that guidance to authorize the governance transition and development pause as one scoped migration amendment. Existing files alone do not authorize a migration. A planning request produces a plan, not a migration.
- **Already organized:** Verify the relevant boundaries and fill only requested gaps. Do not rebuild a working garage or initiate restructuring during an ordinary application task.

Before creating a new workspace directory, settle its name and location with the user. Reuse an explicitly supplied destination; otherwise ask what to call the workspace and whether any application-directory renaming is desired as part of this setup. “Garage” is a metaphor, not an automatic directory suffix. Preserve existing names unless a rename is requested; do not rename repositories, branches, remotes or product identities merely because a local folder name changes. Record chosen source/destination names in the migration map before copying or creating paths.

For a migration, inspect first, then present the proposed destination layout as a directory tree or diagram before filesystem or index changes. Identify the current-to-proposed paths, independent repository boundaries, tracked workspace docs/support, retained artifacts/recovery and disposable scratch, including what stays, is copied or is renamed. Mark unresolved choices, invite the user to revise the layout and names, and obtain approval of the resulting plan before applying it. If that specific plan is already approved, proceed without another approval gate; a general request to organize an unfamiliar project is not approval of an unseen layout. Use the scaffold layout as an option, not an assumption that all projects need identical directories. For a single-application migration, offer placing the application directly under the workspace; use an `apps/` container when grouping applications helps or the user prefers it. Preserve an established layout unless its change is part of the requested refactoring. Keep approved choices in the migration contract, and revisit only material departures from them.

## Preserve domain ownership

| Domain | What belongs there |
| --- | --- |
| Application repository | Product code, supported interfaces, README, contributor documentation, and intentional source/test assets. Own Git history and origin; usable without this garage. |
| Workspace documentation | Lasting workspace organization plans, migration contracts and workspace decisions. Default to tracked garage documentation such as `docs/`; application-specific documentation remains with the application. |
| Retained generated work | Reports, runtime outputs and exchanges between applications, typically in ignored `artifacts/`. Retention does not imply Git tracking. |
| Disposable work | Task scratch under the selected temporary directory, typically ignored `tmp/`. No migration contracts or recovery evidence. |
| Workspace support | Development-agent instructions, selected skills, shared tools, and workspace conventions. Version-control the portable support; keep secrets and machine-local state out. |

Classify by purpose, not filename or whether an agent generated it. A workspace migration contract governs the workspace and belongs in its tracked documentation; it is not a runtime report. A supported MCP endpoint can be product code; a local agent adapter can be garage tooling. An intentional test fixture is not disposable merely because it was generated. Keep machine-local or sensitive recovery data in a retained, access-appropriate location outside scratch, ignored unless deliberately selected for tracking; reference that evidence from the contract without copying sensitive contents into it. Preserve the user's chosen ownership when it differs from these defaults.

## Set up the workspace

For a new empty garage using the default layout, preview the bundled scaffold:

```sh
python3 <skill-directory>/scripts/init_workspace.py <garage-directory>
```

Run the same command with `--apply` to create it within the authorized setup scope. A request to set up the garage authorizes its scaffold; do not add another approval gate merely to run it. Environment approval still applies outside allowed roots, and the script grants no sandbox access. The script creates a local Git repository, root `.gitignore`, `AGENTS.md`, `README.md`, empty `apps/`, `docs/`, `artifacts/`, `tmp/`, and `.worktrees/` directories. It installs no scratch helper. It does not stage, commit, create an application or worktree, or configure a remote. It refuses existing content, symlink paths, and directories already owned by a Git repository. Those cases need inspection and the appropriate path above, not a force option. Use the steps below directly for a different chosen layout or additive setup; these defaults are a convenience, not mandatory workspace policy.

1. **Choose the smallest layout.** Use existing conventions and the user's choices. Establish where independent applications can be cloned, where generated work will live, and where shared support belongs. Record the mapping locally. Leave application space empty unless a starter repository was requested; do not create unused tool collections or placeholder applications.
2. **Give the garage its own tracking boundary.** For the thin-root-repository pattern, initialize Git at the garage root only when that directory is not already owned by another repository. Otherwise inspect the existing boundary and use the refactoring path if it must change. Make workspace files eligible for tracking by default and explicitly ignore the chosen application and runtime directories. Preserve an existing user-selected tracking policy; do not silently replace it. Keep applications and runtime work excluded; do not register applications as submodules merely because they live beneath the garage.
3. **Document how to work here.** Write concise root `AGENTS.md` guidance naming the domains and directing agents to the selected application's own README, contributor docs, and applicable instructions before editing it. Keep human-facing application conventions authoritative for the app. Record workspace-specific paths, output settings, installation choices, and ownership in the garage, rather than embedding them in reusable skills.
4. **Set up only needed support.** Install or configure skills and tools required by the request using the chosen installation mechanism and existing authorization. Separate portable configuration from local credentials and machine-specific state. When the application itself supplies skills, distinguish its editable source from the selected installed version; retain deliberate pins or copies rather than silently linking active instructions to a changing checkout. Report which version is active. Do not silently relocate protected control files or broaden permissions to make setup succeed.
5. **Connect outputs without coupling the product.** Use application-supported flags, environment variables, or configuration to select external artifact locations. Document how producers and consumers agree on those locations and how relative paths resolve. If an app lacks this capability, identify the needed application change; implement it only within the authorized scope. Keep a documented standalone invocation that works without garage files.

For the default scaffold layout, use explicit root-directory exclusions:

```gitignore
/apps/
/artifacts/
/tmp/
/.worktrees/
```

Adapt the application exclusions to the selected layout: for an application directly under the garage, ignore its actual directory instead of an unused `apps/` path. New workspace documents, nested documentation, and support files remain eligible without individual exceptions. Avoid a blanket root ignore or a document allowlist unless the user chose that policy.

Add narrow ignore rules for private or generated content outside the excluded directories. Eligibility is not approval to commit: review content before staging, including documentation and support configuration. Ignore rules do not untrack existing files, block force-adds, or enforce sandbox permissions. Stage only intentional paths in the intended repository and inspect the index; application contents and accidental application Git links must not enter the outer index.

Write lasting workspace plans, decisions and migration contracts under `docs/` by default. Keep application-specific docs in the application's index, reports in retained artifacts, and disposable work in scratch. For existing garages, reconcile the selected documentation and tracking rules without moving unrelated material.

Designate one authoritative migration document and link it from garage instructions or the README. Handoff/recovery copies are labeled snapshots with a source revision or content identity and a pointer to the current authoritative document. Record any change of authoritative location, including the transition from a pre-garage working location into tracked garage docs, so receiving sessions can locate the current record instead of resuming from a stale copy. See the refactoring reference for transfer and reconciliation.

## Keep scratch and worktrees local

Record the chosen locations in the garage's `AGENTS.md` so ordinary work follows them without re-invoking this setup skill. The default is `tmp/<task>/` for disposable scratch and `.worktrees/<app>/<task>/` for worktrees of independent apps. Retain established local conventions such as `.worktree/` when appropriate. For an existing garage, inspect and add only missing directories, ignore rules and guidance; do not rerun the empty-directory scaffold, adopt existing content as disposable, or relocate existing worktrees just to match a spelling.

Workspace setup establishes scratch locations and ownership rules; ongoing task lifecycle is separate. If available, `workspace-scratch` can manage named task directories from its installed helper. Do not copy the helper into the workspace or make that skill a prerequisite for setup. Inspect existing helper installations before changing them; preserve active tasks and update callers when a migration explicitly includes their removal.

Document how agents select unique task directories, route temporary output through supported settings, stop writers, inspect contents, and retain useful data before scoped cleanup. Some workflows require temporary storage outside any enclosing Git repository; use an allowed location and record the reason. Never use scratch cleanup for repositories or worktrees.

For requested worktrees, use the owning application's Git repository and the selected garage-local destination, with a distinct app/task namespace and collision checks. Inspect both destination and shared Git metadata access (`git rev-parse --git-common-dir`); local placement does not eliminate protected-metadata approval or change host-managed worktree locations. An app-root session may also exclude the enclosing garage from its writable scope. Remove worktrees through Git-aware checks for active use, dirty/ignored data, locks and merge status; `cleaning-git-repositories` can supply that workflow if available. Never use the scratch helper to remove worktrees, and do not impose a dependency on another skill.

## Verify the garage

- Inspect the root index with `git ls-files` and status; check representative governance, application, and artifact paths with `git check-ignore -v`. For tracked paths, inspect the index separately. Application files must not appear as root-tracked files or accidental Git links.
- Verify new workspace files, nested documentation, and support files are eligible under the selected tracking policy and, when staging is authorized, appear in its index. Check the authoritative migration document and snapshot pointers; retained reports and private recovery data must not enter the index merely because they were generated by an agent or retained for handoff.
- Verify scratch and worktree paths are ignored. Check effective access and temporary output placement using the selected workflow; setup does not require installing or exercising a particular cleanup helper. System temporary directories may already be permitted; garage-local storage is an organization/default-location choice, not a permission override.
- For existing applications, compare Git roots, history, and origins before and after. Verify the documented invocation from an independent checkout outside the garage when application paths/configuration changed. Exercise a producer and consumer if artifact routing changed.
- Treat agent startup, Git tracking, and write permissions as separate checks. Launch/open the garage as the agent workspace. For Codex, put selected discoverable skills under the garage's `.agents/skills` using its installation convention. Starting inside an independent app may stop discovery at that app's Git root. Root startup does not automatically read every descendant application's instructions.
- Verify loaded instructions and skills through the current host when available; compare the intended selections with the loaded inventory, not just the filesystem links. Test ordinary destination writes separately from protection of instruction directories and access to shared Git metadata. If a restarted session retains the old scope, use a supported destination session when authorized; changing shell directories does not repair its permissions. Report unresolved discovery or access limitations without repeatedly retrying the same blocked operation.

Return the domain map, files created or changed, what the garage tracks/excludes, application boundaries, and verification results or limitations. For migrations, state separately whether the copy is preserved, the destination is ready for development, and old paths are removed or intentionally retained; use the refactoring receipt guidance. State where to clone the first app when the garage is empty. Do not create remotes, publish, or migrate unrelated projects as a consequence of setup.
