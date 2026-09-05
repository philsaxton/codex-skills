# Set Up the Garage — Skill Design

## Purpose and agreed direction

The workspace is the garage; applications are the things built inside it. Small projects accumulate generated reports, shared working state, development-agent instructions, and tools alongside application code. The skill establishes distinct homes for these domains while preserving the connections needed to use them.

The user approved starting with garage setup, leaving application space empty unless a starter repository is requested. Existing-workspace restructuring is a second entry point serving the same outcome. This document records the conversation's design; the user authorized implementation on 2026-09-04.

## Boundaries

- The garage is the directory opened as the agent workspace. Application repositories live beneath it and retain independent Git histories and origins.
- A thin root Git repository tracks explicitly selected workspace governance and shared tooling. Application repositories and generated runtime/work artifacts stay outside its index.
- Applications carry their code and human-facing documentation and remain usable without the author's garage. Workspace instructions defer to application documentation instead of duplicating it.
- Agent development instructions and local support tooling belong to the garage. Classify an MCP interface by its purpose: a supported application feature can belong to the application; a local agent adapter belongs to workspace support. The word “agent” alone does not determine ownership.
- Generated artifacts have a separate workspace location. Application output locations must be configurable without hard-coded dependence on this particular garage.
- Directory names, repository manifests, skill installation mechanisms, tool selections, origins, and retention policies are workspace-specific choices recorded locally.

Physical containment does not imply shared Git ownership. The root repository must neither absorb application files nor register applications as submodules merely because they are beneath it. Ignore rules affect untracked files; they do not remove already tracked files or enforce permissions.

## Proposed skill

Implementation name: `workspace-setup`, with display name “Set up the garage.” The user favored the garage metaphor and asked about discoverability; this pairing follows the recommendation summarized before the user authorized implementation.

The [official skill documentation](https://learn.chatgpt.com/docs/build-skills), consulted on 2026-09-04, says Codex initially sees names and descriptions and matches tasks against descriptions for implicit invocation. It recommends front-loading use cases and trigger words because descriptions may be shortened. A descriptive identifier is a clarity recommendation, not a documented guarantee of better selection. Proposed setup description: “Set up an agent workspace with separate homes for independent application repositories, generated artifacts, and shared agent instructions and tools.” Extend it to existing-workspace restructuring only when that mode is validated.

### One entry point, conditional guidance

Keep one discoverable `SKILL.md` that inspects the starting directory and selects new setup or existing-workspace restructuring. This is the layered loading behavior discussed as “nested skills”; the design does not assume a special nested-skill runtime feature or automatically create a second skill.

Keep the common boundaries and new-setup workflow in the entry point. When the existing-workspace mode is implemented, put its substantial migration procedure in `references/refactoring.md`, linked explicitly from the entry point and read only when existing content requires restructuring. Existing files alone do not authorize migration. The reference must add mode-specific guidance rather than duplicate common instructions; its separate loading is justified by keeping migration detail out of new-workspace tasks.

Extract a separately discoverable refactoring skill only if later evidence establishes independent usefulness. Do not add bundled scripts or assets unless testing demonstrates a concrete need.

### Deterministic scaffold

During implementation the user requested a script for the repeatable Git initialization, ignore file, and generic root instructions. Add `scripts/init_workspace.py` with a no-write preview by default and explicit `--apply`. For an absent or empty directory outside another repository, it creates the thin Git root, `.gitignore`, `AGENTS.md`, `README.md`, and empty `apps/` and `artifacts/` homes. It stages nothing and creates no application, remote, or commit. Existing content, repository ownership, and symlink paths cause refusal before writing. Custom layouts and refactoring remain agent-guided. These concrete scaffold defaults are optional conveniences, not cross-project requirements.

Trigger on requests to establish an agent workspace around independent applications or separate application code, generated work, and workspace support in an existing workspace. Routine feature edits, stylistic cleanup, branch/worktree cleanup, and general security audits are outside this skill's outcome.

### New workspace

Inspect the starting directory, repository boundaries, existing instructions, and actual execution permissions. Establish a minimal layout and root tracking policy using the user's choices. Create workspace instructions that explain domain ownership, where applications can be placed, how their documentation is discovered, and where generated work belongs. Install or configure only tools required by the stated workflow; do not populate a generic tool collection. Leave application space empty by default. Do not create remotes or publish anything without authorization.

### Existing workspace

Inventory tracked and untracked material, application roots, generated state, and references to existing paths before proposing changes. Produce a source-to-destination map, required reference/configuration updates, and proportionate verification and recovery steps. Preserve existing work and repositories. Apply only authorized migration scope; do not infer permission to delete data, alter trust boundaries, or rewrite history from a request to inspect or plan.

The user clarified the application-root case during the refactoring stage: establish a dedicated enclosing garage and place the intact application repository beneath it. Prepare exact source/destination paths and any required access or host handoff before relocation. Move from a stable context outside the checkout being moved; do not rely on changing shell directories to change the agent workspace or sandbox. Preserve shared-history suites as units unless extraction is separately requested. Repository relocation and separating local-only agent support are distinct steps; neither implies deleting application history.

For staged migration paths and interrupted attempts, reconcile committed, indexed, working, and destination versions before replacing data or changing tracking. Current destination existence is evidence to inspect, not an invitation to overwrite it. Update producer/consumer contracts together, including filenames as well as directories.

Follow-up decisions: preserve mixed `AGENTS.md` requirements by purpose, placing product build/use and contributor conventions in human-facing application docs and local Codex governance/support in the garage. Save a durable migration contract before active-directory relocation, covering authorization, requirement destinations, preservation, steps, verification, recovery, and the receiving session's required access. `contract-author` is optional; the workflow supplies a standalone fallback. Setup authorization covers running the scaffold within allowed roots without another gate, while environment approval remains controlling outside them.

The separate future Workspace trust review candidate concerns mutable executable inputs to tooling trusted with greater permissions. Current refactoring only checks relevant trust changes caused by migration. A skill does not bypass the sandbox, and standing command approval does not pin script or dependency contents. No future skill is required by this workflow.

### Completion receipt

Report the resulting domain map, what the root repository tracks and excludes, independent application roots, relevant verification results, and any unresolved constraints. Record workspace-specific conventions in that workspace, not in this reusable skill.

## Evidence and verification requirements

The concrete source examples are `/Users/phil-mac/Projects/workspace-refactoring-plan.md` and `/Users/phil-mac/Projects/vending-ops/.gitignore`. They inform the design but are not runtime dependencies or universal layouts. The latter ignores root entries by default and permits selected governance paths while excluding local Codex configuration.

Before encoding Codex-specific instructions, verify current instruction discovery, skill discovery, workspace startup, and sandbox behavior using the openai-docs workflow. Opening a directory must not be represented as automatically granting write access or guaranteeing newly installed skills are loaded in an existing session.

Validate Git ownership with actual index and ignore behavior in disposable workspaces. Test application portability from an independent checkout with no garage present. Test an existing-workspace migration for preserved data and repaired path references. Test that a supported application MCP interface is not incorrectly extracted as development governance.

Use varied scenarios to assess whether dedicated guidance improves decisions beyond ordinary capability, consistent with the backlog's qualification criteria. One known workspace establishes the user's intent, not proof of cross-project effectiveness.

## Scope of the next deliverable

Author and validate the new-workspace behavior first. Evaluate existing-workspace restructuring separately before advertising that mode as supported. General trust-boundary auditing remains a separate backlog candidate. This plan does not authorize restructuring any live project.
