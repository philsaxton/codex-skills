---
name: workspace-setup
description: Set up an agent workspace (the garage) around independent application repositories, or reorganize an existing workspace to separate application code, generated artifacts, and shared agent instructions and tools. Use for workspace setup and domain separation, not routine feature work or Git branch/worktree cleanup.
---

# Set up the garage

The workspace is the garage; applications are the things built inside it. Give application code, generated work, and agent support distinct homes while keeping each application usable by someone with a different garage.

## Inspect and choose the path

Read the request and applicable instructions. Inspect the starting directory, including hidden files, Git roots and tracked files, existing application repositories, and actual write permissions. Resolve relevant symlinks before treating a path as inside the workspace.

- **New workspace or additive setup:** Follow the setup steps below when existing work can remain in place.
- **Existing content needs separation:** Read [refactoring guidance](references/refactoring.md) before planning or applying moves, index changes, or path rewiring. Existing files alone do not authorize a migration. A planning request produces a plan, not a migration.
- **Already organized:** Verify the relevant boundaries and fill only requested gaps. Do not rebuild a working garage or initiate restructuring during an ordinary application task.

## Preserve domain ownership

| Domain | What belongs there |
| --- | --- |
| Application repository | Product code, supported interfaces, README, contributor documentation, and intentional source/test assets. Own Git history and origin; usable without this garage. |
| Generated work | Runtime outputs, reports, exchanges between applications, and local working state. Separate from application source and the garage's Git index. |
| Workspace support | Development-agent instructions, selected skills, shared tools, and workspace conventions. Version-control the portable support; keep secrets and machine-local state out. |

Classify by purpose, not filename. A supported MCP endpoint can be product code; a local agent adapter can be garage tooling. An intentional test fixture is not disposable merely because it was generated. Preserve the user's chosen ownership when it differs from these defaults.

## Set up the workspace

For a new empty garage using the default layout, preview the bundled scaffold:

```sh
python3 <skill-directory>/scripts/init_workspace.py <garage-directory>
```

Run the same command with `--apply` to create it within the authorized setup scope. A request to set up the garage authorizes its scaffold; do not add another approval gate merely to run it. Environment approval still applies outside allowed roots, and the script grants no sandbox access. The script creates a local Git repository, root `.gitignore`, `AGENTS.md`, `README.md`, and empty `apps/` and `artifacts/` directories. It does not stage, commit, create an application, or configure a remote. It refuses existing content, symlink paths, and directories already owned by a Git repository. Those cases need inspection and the appropriate path above, not a force option. Use the steps below directly for a different chosen layout or additive setup; these defaults are a convenience, not mandatory workspace policy.

1. **Choose the smallest layout.** Use existing conventions and the user's choices. Establish where independent applications can be cloned, where generated work will live, and where shared support belongs. Record the mapping locally. Leave application space empty unless a starter repository was requested; do not create unused tool collections or placeholder applications.
2. **Give the garage its own tracking boundary.** For the thin-root-repository pattern, initialize Git at the garage root only when that directory is not already owned by another repository. Otherwise inspect the existing boundary and use the refactoring path if it must change. Ignore root entries by default and permit only the selected governance/support paths. Keep applications and runtime work excluded; do not register applications as submodules merely because they live beneath the garage.
3. **Document how to work here.** Write concise root `AGENTS.md` guidance naming the domains and directing agents to the selected application's own README, contributor docs, and applicable instructions before editing it. Keep human-facing application conventions authoritative for the app. Record workspace-specific paths, output settings, installation choices, and ownership in the garage, rather than embedding them in reusable skills.
4. **Set up only needed support.** Install or configure skills and tools required by the request using the chosen installation mechanism and existing authorization. Separate portable configuration from local credentials and machine-specific state. Do not silently relocate protected control files or broaden permissions to make setup succeed.
5. **Connect outputs without coupling the product.** Use application-supported flags, environment variables, or configuration to select external artifact locations. Document how producers and consumers agree on those locations and how relative paths resolve. If an app lacks this capability, identify the needed application change; implement it only within the authorized scope. Keep a documented standalone invocation that works without garage files.

A minimal root ignore example, only when these are the chosen governance files:

```gitignore
/*
!/.gitignore
!/AGENTS.md
!/README.md
```

Add exceptions for actual support paths as needed. Re-including a directory can expose its descendants, so inspect local configuration and runtime files beneath it. Ignore rules do not untrack existing files, block force-adds, or enforce sandbox permissions. Stage only intentional paths in the intended repository and inspect the index; no blanket force-add.

## Verify the garage

- Inspect the root index with `git ls-files` and status; check representative governance, application, and artifact paths with `git check-ignore -v`. For tracked paths, inspect the index separately. Application files must not appear as root-tracked files or accidental Git links.
- For existing applications, compare Git roots, history, and origins before and after. Verify the documented invocation from an independent checkout outside the garage when application paths/configuration changed. Exercise a producer and consumer if artifact routing changed.
- Treat agent startup, Git tracking, and write permissions as separate checks. Launch/open the garage as the agent workspace. For Codex, put selected discoverable skills under the garage's `.agents/skills` using its installation convention. Starting inside an independent app may stop discovery at that app's Git root. Root startup does not automatically read every descendant application's instructions.
- Verify loaded instructions and skills through the current host when available; report untested startup behavior as such. Restart in the intended directory if instructions are stale or new skills do not appear. Check the active sandbox rather than assuming everything physically under the garage is writable.

Return the domain map, files created or changed, what the garage tracks/excludes, application boundaries, and verification results or limitations. State where to clone the first app when the garage is empty. Do not create remotes, publish, or migrate unrelated projects as a consequence of setup.
