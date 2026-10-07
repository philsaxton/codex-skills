# Bundled recovery dependency provenance

The two modules in `scripts/recovery/` originate from the reviewed `garage-rebuild-20261006` release, initially packaged unchanged on 2026-10-07. They provide the exact-source-object validation and bounded streaming-file checks used by the cloud readiness helper. The source utility has no explicit standalone license file; this record does not invent one or establish new redistribution rights.

## Original packaged identities

These hashes record the original release and test bytes, before the corrections below. They remain historical provenance, not the current pins for revised resources.

| Resource | SHA-256 |
| --- | --- |
| `garage_rebuild.py` | `8c0914a2830900989e090c9e904196167a1abd73d8cff3ac47013376a5daf0ef` |
| `garage_workspace.py` | `bdabd09a0d988481c1f296a5ebba95720576ac386308534835dca7d5801b120c` |
| `tests/recovery/test_garage_rebuild.py` | `f9272791370b4dfd0f72ab952508ad260458e47fe1ee1fc3d5084668de0b0309` |
| `tests/recovery/test_connector_workspace.py` | `cb3119573f46dc7e40a257d8957ee22891c7012b4885bcfb6d68fd562cf1da33` |
| `tests/recovery/test_streaming_private.py` | `4edd5715ff1c486bc097580ec72b44b1bc2dc4bb8cac474a63c9fe55e84d6008` |

## Deliberate 2026-10-07 corrections

PR #2 review identified unbounded shared-tree expansion and two filesystem fixtures that assume case-sensitive storage. The bundled `garage_workspace.py` now permits at most 10,000 expanded directory/file/symlink path occurrences across a complete bundle, checking during traversal before allocating the next path. Standalone source-object validation uses that same maximum; shared trees and repeated paths in separate checkpoints each consume the budget. The two affected `test_garage_rebuild.py` fixtures skip explicitly when their temporary filesystem aliases the differing-case names. Production collision validation is unchanged. The new `test_source_expansion.py` adds budget, shared-tree and filesystem-independent collision regressions.

| Deliberately revised or added resource | Current SHA-256 |
| --- | --- |
| `garage_workspace.py` | `a25aa51f3cb986a2736bd9a833db0f396a3d72d3c41ed2cba55ada4c731c6fc8` |
| `tests/recovery/test_garage_rebuild.py` | `906e6c0d02ec262c178d4abc8252ed1766011d43f22cd64d7555a26c066f8ed5` |
| `tests/recovery/test_source_expansion.py` | `0262ad574cf50cc293e4df73a0e1ffc43afad5a1c2ca0181756148c232b6413c` |

`garage_rebuild.py`, `test_connector_workspace.py` and `test_streaming_private.py` remain byte-identical to their original hashes above. Original headers are retained. The [correction validation record](../../docs/evidence/2026-10-07-cloud-readiness-review-corrections.md) distinguishes new results, inherited failures and synthetic skip-path checks from historical evidence and real host capability.

The authoritative runtime pins remain [recovery-dependency.json](recovery-dependency.json). The readiness helper resolves its default dependency directory relative to its own resource location, validates both modules before loading either, and does not use ambient imports or write bytecode. An explicit alternate directory must match those same pins.

All 79 original cases are retained, with the two case-collision fixtures revised as described above, alongside 10 new source-expansion/collision cases. Run them from any directory with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 <repository>/tests/run_recovery_tests.py
```

The test-only launcher checks every bundled test module's current hash, loads the pinned bundled modules, and binds the two relocated test-module `SCRIPT` constants to those same bundled files. This is needed because the original tests locate sibling CLI scripts; `PYTHONPATH` alone would not select the relocated CLI. No second implementation copy is maintained. `--list` lists the 89 discovered cases without running them. On case-insensitive temporary storage, the two collision fixtures are reported as skips rather than passes; virtual-object tests still exercise production collision refusal on every filesystem. These are synthetic offline/local-Git tests; some create hundreds of MiB of disposable data, so select suitable permitted temporary storage with `TMPDIR`.

Shipping these resources makes dependency bytes portable. It does not add a new skill mode, grant recovery/transfer authority, acquire private application sources, supply credentials, or expose the dependency's mutation commands as an automatic readiness workflow. Read [cloud setup guidance](cloud.md) for the bounded entry point and remaining acquisition limits. No previous garage governance, private selection manifest or test-output payload is included.
