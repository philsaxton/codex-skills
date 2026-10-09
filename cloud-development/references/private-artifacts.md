# Private artifacts and fallback

Use when important project material is outside the verified code checkpoint, or an approved private copy is the fallback for a blocked publication route.

## Inventory only the relevant scope

Inspect important untracked, ignored and generated work, workspace governance/tooling, private inputs and uncommitted code. Record relative path or safe identifier, role/provenance, byte size and SHA-256 for selected stable files; whether a verified durable source exists; and whether the item is unique or regenerable from a pinned recipe. Avoid collecting secrets or unrelated home/system data. Do not dismiss unique evidence because Git ignores it.

Keep sensitive names, inventories, links and provenance in the private record. A publishable receipt may use opaque artifact IDs and a sanitized rebuild recipe, but must not leak private package links or contents. Record deliberately excluded or unavailable inputs and their impact. A planned destination or accessible historical copy is not proof that the current bytes are protected.

## Establish the copy's authority and meaning

Use only the approved material, destination, audience and purpose through a supported transfer route. Apply current confirmation requirements to source data and upload. A one-time Dropbox or other private copy does not authorize recurring transfers, broader contents, a substitute destination or persistent credential setup. If publication is blocked, an approved Git bundle or source archive may preserve work privately; it does not make the origin branch published. Check the selected fallback preserves the history level the task needs.

Choose the smallest recoverable package and declare its kind:

- **Full snapshot of declared scope:** contains everything in that explicit selected scope without an earlier artifact package. External prerequisites, including the selected code checkpoint when not embedded, toolchains and deliberately excluded inputs, remain explicit. Never label it a whole workspace backup merely because the filename says “full.”
- **Incremental overlay:** records exact immutable base and every intervening dependency by identity/hash, application order, intended additions/replacements/deletions, and resulting inventory. It is not standalone. Do not assume an overlay contains unchanged files or that a latest filename supplies its prerequisites.

For either kind, bind compatible repository/commit/tree, profile/governance identities, source artifact versions and restore recipe. For a Git bundle, verify its prerequisites and intended refs/history; a patch or file archive alone is not a Git-history backup. Do not include credentials, authentication stores, OS images or dependency caches as a substitute for reproducible setup.

## Prepare and verify a stable copy

Coordinate with writers to capture a stable selected version. Use a supported snapshot mechanism or quiesce authorized writers; compare source identity/hashes before and after packaging. Changed files require a fresh stable capture or an explicit exclusion/gap. Never silently claim later edits are covered by an older archive.

Review the package file list and exclusions before the approved upload. Retain prior versions and use a distinct versioned destination; do not overwrite unique evidence. Include a manifest with each selected file's SHA-256/size and a minimal restore recipe. Record archive SHA-256/size separately from per-file hashes, and distinguish the provider's hash algorithm from SHA-256. Preserve the package's required chain and the receipt needed to find it outside the ephemeral workspace, within the same authorized scope.

Verify the returned destination object/version and retrieve/read back its exact bytes through a supported route to an isolated location, or use an independently verifiable provider checksum with the same algorithm and exact version binding. Compare archive SHA-256/size and selected contents against the source manifest. A provider acknowledgement, title, size-only match or proprietary content hash is not a SHA-256 read-back. If exact bytes/checksums are unavailable, report **uploaded, integrity unverified**. Missing/mismatched dependencies block the corresponding recovery claim even when the newest archive verifies.

Do not extract arbitrary archives over live work. Inspect relative paths and entry types first; refuse traversal, absolute paths, unsafe links and unexpected files. Use a fresh approved restore location, preserve survivors and apply only the selected verified chain. Deletions belong only to the reconstructed target, never to unrelated survivors. A restore drill needs its own applicable authority and tool prerequisites; successful upload/integrity checking is not a drill.

## Report what remains exposed

Keep publication and private-copy outcomes independent. Report the verified version/scope/time, actual restore test (or not run), absent dependencies and new or excluded cloud-only work. Keep cloud originals and prior durable copies until the [backup retirement](backup-retirement.md) checks and applicable deletion authorization are satisfied; a successful transfer does not authorize deletion. If upload fails or is canceled, retain stable local material, inspect uncertain remote state, and report the last verified private point without substituting a new destination or silently retrying cancellation.
