# Retire redundant backups

Use after an origin checkpoint is independently verified and at handoff. Assess retention now rather than making another indefinite copy. This procedure does not authorize backup deletion, restoration, uploads, a new computer task or history rewriting; apply current user instructions and confirmation requirements to each action.

## Prove redundancy, not just publication

1. Recheck the approved origin repository/ref and exact reachable commits, trees and required ancestry through the supported route. Record the UTC time and evidence. A push receipt, matching final files, squash/cherry-pick or reconstructed commit is not proof that the original exact history is preserved. If required objects cannot be obtained or a ref moved, keep the affected backup and report the gap.
2. Inventory every candidate's complete declared contents, manifests, refs/history and external prerequisites, including older bases and overlays, using stable identities, sizes and hashes. Coordinate with writers and pending transfers; keep changing or uninspectable packages. Classify code duplicated at origin separately from private inputs/extracts, unique tests/evidence, uncommitted/untracked work, garage governance/tooling, recipes, source manifests and audit/provenance records. Git publication alone cannot cover these other classes.
3. Build the dependency graph for all retained recovery points, including bundles, base snapshots, ordered overlays and locating records. Mark every incoming reference to a candidate. Never delete a base or intervening overlay still needed by a retained checkpoint. Do not infer redundancy from age, names such as "full"/"latest", size, a newer package or a successful upload.
4. Give each candidate a reasoned disposition: retain (unique, required, unknown or required by retention policy); compact/replace (mixed contents or dependency chain); or eligible for authorized retirement (all required contents/history preserved elsewhere, no live dependencies and no retention obligation). Keep evidence of that decision outside the object proposed for retirement. If there is no safe candidate, record the reason rather than forcing cleanup.

## Replace a chain before retiring it

For a mixed package or prerequisite-dependent chain, prepare the smallest replacement checkpoint within approved scope. Preserve all still-required private contents, exact history not recoverable from origin, governance, source manifests and audit/provenance, with explicit compatible code/profile identities and external prerequisites. Apply the stable-copy and destination read-back procedure in [private artifacts](private-artifacts.md). A replacement can omit origin-backed code only when its exact recovery requirements are demonstrably satisfied there.

Keep the originals until an authorized isolated restore drill succeeds using only the proposed retained sources, never the candidates to be retired. Inspect archive paths/types before extraction. Verify the reconstructed file manifest, required Git objects/refs/ancestry, ordered overlay effects, private artifacts, governance and relevant setup/build/test checks against the declared recovery point. For a standalone duplicate code-only backup, demonstrate exact acquisition from origin and the required history/manifest checks in isolation; do not demand unrelated private input or application tests outside its declared scope. Record missing checks honestly and retain any backup whose retirement proof depends on them.

Persist the replacement, verification evidence and updated recovery/locating records to their authorized durable destinations. Redirect retained manifests and recipes to the replacement through their owning workflow; do not silently alter profile pins. Preserve historical provenance while distinguishing retired artifacts from live dependencies. Re-inspect the dependency graph and current origin state immediately before retirement. If another retained recovery point still needs an original, retain it or separately establish and verify its replacement. Missing authorization or inability to verify restoration blocks retirement, not independent development.

## Retire only the reviewed scope

Check the exact paths/object versions, ownership, stable hashes, active writers and current deletion authority. A skill-edit request or publication approval is not deletion approval. Obtain the confirmation required for the specific deletion and target; irreversible deletion requires action-time confirmation even with standing approval. Prefer a supported recoverable deletion when authorized, and record its actual recovery window. Merely moving files into another indefinitely retained backup folder is not completed cleanup.

Remove only the reviewed eligible objects using the supported route. Do not prune entire directories, Git objects, provider version history, Trash or remote refs as a shortcut. On uncertain results, inspect state before any retry. Verify retained sources and records remain accessible and consistent, record what was retired and why (identity/hash, replacement/origin evidence, authority, time and recoverability), and report actual storage reclaimed if measurable. Keep private inventories and links private; publish only an authorized sanitized receipt. State retained blockers and remaining cloud-only exposure separately from completed cleanup.

## Decision examples

- A code-only bundle's exact commits and ancestry are reachable at origin, isolated acquisition verifies its declared scope, no retained recipe needs it, and recoverable deletion is authorized: retire that bundle and retain the receipt.
- Origin contains the same final tree in a new commit, but the bundle holds original unpublished commits: retain required original history; tree equivalence is insufficient.
- A published-code archive also contains the sole private extract, garage AGENTS.md and source manifest: retain it until an authorized replacement preserves those items and passes the isolated drill.
- Overlay C depends on B and base A, although C contains the newest code: keep A and B until all retained dependents are redirected to a verified compatible replacement.
- A replacement has a matching upload checksum, but its restore is untested or uses files from A: keep A; integrity alone does not demonstrate independent restoration.
- A backup is still receiving a writer's changes, has an unreadable manifest, or origin was force-moved after verification: stop its retirement and re-establish stable evidence.
- A fully redundant backup has no deletion permission, or the service only supports permanent deletion: report the exact candidate and request the applicable confirmation; do not delete it during a skill update.
- Retention policy requires an old checkpoint's audit record: preserve that record and its required evidence even when all code is published.
