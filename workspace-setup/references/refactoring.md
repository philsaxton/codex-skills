# Build the garage around existing work

Read this when workspace setup requires separating existing content. Use the entry point's domain ownership rules; this reference supplies the migration procedure, not a second skill or an automatic cleanup mandate.

## Map the existing connections

Inventory the affected repositories and their tracked, untracked, ignored, staged, and dirty content. Include hidden control files and symlink targets. Establish which repository owns each path; a directory containing a `.git` file may be a linked worktree or submodule rather than a movable standalone repository.

Distinguish a garage containing independent repositories from an application repository containing several components. Keep a shared-history suite together unless repository extraction was separately requested; directory names do not establish independent applications or origins.

Trace producers and consumers of paths being changed: application settings, scripts, tests, scheduled jobs, shared reports, local adapters, and instructions. Separate intentional product assets from runtime outputs. Preserve supported interfaces and human-facing application docs with the application.

Include existing scratch locations, active writers and registered application worktrees in that map. Add garage-local scratch/worktree defaults for future use without sweeping old directories into cleanup. Keep contracts and recovery copies outside disposable scratch. Worktree placement changes require Git-aware relocation and shared-metadata access, not an ordinary directory move or a scratch cleanup command.

Produce a compact migration map with source, destination, owner/repository, affected references, and verification. Record uncertain ownership explicitly. Resolve only material ambiguities that prevent a safe migration; use established conventions for routine choices.

Classify existing `AGENTS.md` content by purpose, not as a whole document. Preserve product build/use requirements and contributor conventions in the application's human-facing docs; transfer local Codex-agent governance and support guidance to the garage. Reconcile with existing docs, preserve requirements and their meaning, and update links before removing authorized old copies. Record unresolved conflicts rather than silently dropping requirements. Relocating a checkout intact preserves history but does not complete this separation. Keep product-supported interfaces and their documentation with the application.

## Save the migration contract

Record the authorized outcome, source/destination and ownership map, instruction-requirement destinations, preservation evidence, ordered migration steps, acceptance checks, recovery route, and unresolved decisions. Include the stable session context and access needed for relocation. When available and useful, `contract-author` may help draft this record; otherwise write the same concise record directly. No other skill is required.

Save it durably in the current workspace before copying the application. Keep the original workspace available while the agent finishes the contract and supporting handoff documents; copy their latest versions into the new garage once destination access is established, obtaining any missing environment approval. Record both locations, which version is authoritative, completed and pending steps, and changes made since the application copy. The receiving session must read the delivered contract and reconcile actual state before continuing; conversation memory alone is not the migration contract.

Include an explicit cleanup recommendation for the retained original checkout: its exact path outside the new garage, verification and reconciliation still required, any remaining writers or sessions using it, retained recovery material, and the approval/access needed to remove it. Mark this cleanup pending until it is performed or the user elects to retain the original; copying the app does not itself authorize deleting the old checkout.

## Enclose an existing application repository

When launched at the application's Git root, establish a dedicated enclosing garage and place the intact application repository beneath it. For example, a checkout at `/work/widget` could become `/work/widget-garage/apps/widget`; the names are local choices. Do not silently make a shared parent such as `Projects/` the garage, reinitialize the application, or turn its current index into a governance-only index.

1. Record the exact source and destination, repository type, history/branch/origin, index state, and working data to preserve. Keep a shared-history suite as one repository. A linked worktree or submodule needs a Git-aware transfer preserving its relationships; copying its directory alone may leave metadata pointing to the original and is not sufficient.
2. Prepare the layout and contract locally, then establish actual access before writing the new garage. Setup authorization covers the empty-garage scaffold for the chosen container but does not waive environment approval. Do not run it against the occupied checkout or enable a force mode.
3. Default to copying an ordinary application checkout intact into the garage, retaining the original so the active agent can continue writing and delivering handoff documents. Preserve `.git`, staged changes, untracked/ignored data and required file relationships; a fresh clone alone omits local work. Coordinate writers to obtain a consistent copy and verify preservation before separating domains in the destination. Stop only the dependent step if destination, preservation or access is unresolved. Use a direct move only when explicitly chosen from a stable session outside the source that will remain valid afterward.
4. Track changes after the copy, including newly written handoff documents, index changes and runtime output. Before switching the authoritative application to the destination, reconcile those changes without overwriting destination work, deliver the latest handoff documents and record the cutover. Do not let both copies continue as independent writable authorities. Keep the original available for recovery and cleanup, not as an unnoticed second active application.
5. Open the garage as the intended agent workspace; verify its instructions, selected skills, effective permissions, application identity/local work and absence of required dependencies on the old checkout. A shell `cd` or skill script does not change the sandbox or loaded instructions. Continue domain separation there and report operational handoff separately from pending old-checkout cleanup.

## Choose and apply a reversible migration

- A nested application repository already excluded from the garage can stay where it is. Avoid moving paths merely to fit a preferred spelling or layout.
- Capture the relevant starting state and a recovery route before mutation. Preserve unrelated dirty/staged work; do not reset it, stash it implicitly, or include it in migration commits. Check destination collisions before copying or moving. For active outputs, coordinate producers so that writes are not lost during the transition.
- When migration paths have staged changes, compare HEAD, index, and working-tree content; preserving the visible file alone can lose a distinct staged version. Preserve or resolve those versions before changing the index. A failed untracking command is not permission to force it.
- On a retry or interrupted migration, reconcile the actual source, destination, and current consumers against the migration map before resuming. Identical copies and divergent copies need different decisions. Never choose a canonical report by modification time alone or overwrite an existing destination to make the layout match.
- Apply only authorized moves and configuration changes. Copy valuable runtime data first when that allows verification before removing the old copy. Update producers and consumers together and preserve application-supported standalone defaults. Use local orchestration for garage-specific paths rather than hard-coding them into the product.
- Handle tracked files explicitly. Changing `.gitignore` does not remove them from an index. Where removing a generated file from tracking is authorized, keep the working data and change only the intended index entries. Do not rewrite history to tidy old artifacts. Intentional fixtures or published deliverables may need to remain tracked.
- Treat linked worktrees, submodules, and symlinks according to their actual relationships. Do not blindly move `.git` metadata or retarget a protected instruction/tool installation as part of cosmetic organization.

When migration changes what trusted tooling executes or who can edit it, check the affected script, imports/dependencies, symlink targets, and configuration against its actual execution permissions. Ordinary sandbox execution remains sandboxed; a standing approval for an outside-sandbox command does not pin the script's contents or dependencies. If the move makes higher-permission execution depend on newly editable code or configuration, record and resolve that specific trust change before activating it. This focused migration check is not a general vulnerability audit and requires no separate review skill.

An inspection or planning request stops at the migration map. Authorization to implement a defined migration carries through its routine reversible steps; do not repeatedly ask permission for work already approved. Stop only the dependent action if preservation, ownership, destination, or permission remains unresolved.

## Verify before retiring old paths

Check preserved data using content comparisons or hashes as appropriate. Run the affected producer-to-consumer workflow using the new locations, and search for stale references in the affected scope. Compare application roots, histories, and origins; inspect each repository's index and unrelated dirty state. Verify a standalone checkout when application behavior changed.

Keep old data or recovery material until the replacement is verified; remove it only when authorized. Report retained copies and remaining transitions instead of calling a partially migrated workflow complete. Return the final domain map and evidence through the entry point's completion receipt.

For copy-first handoffs, recommend cleanup of the exact original app path once the receiving workspace works, post-copy differences are reconciled, necessary recovery material is retained, and no agent, writer, worktree or consumer still depends on it. Recheck those conditions immediately before removal and use existing explicit cleanup approval or obtain it if missing. An original checkout outside the new workspace may also need separate filesystem permission. Never route it through the scratch remover or delete it merely because a destination with the same name exists. Record removal, intentional retention, or the remaining cleanup action in the handoff receipt.
