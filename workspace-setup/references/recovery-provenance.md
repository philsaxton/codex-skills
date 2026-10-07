# Bundled recovery dependency provenance

The two modules in `scripts/recovery/` are unchanged bytes from the reviewed `garage-rebuild-20261006` release, packaged on 2026-10-07. They provide the existing exact-source-object validation and bounded streaming-file checks used by the cloud readiness helper. Their original headers and contents are retained. The source utility has no explicit standalone license file; this record does not invent one or establish new redistribution rights.

| Resource | SHA-256 |
| --- | --- |
| `garage_rebuild.py` | `8c0914a2830900989e090c9e904196167a1abd73d8cff3ac47013376a5daf0ef` |
| `garage_workspace.py` | `bdabd09a0d988481c1f296a5ebba95720576ac386308534835dca7d5801b120c` |
| `tests/recovery/test_garage_rebuild.py` | `f9272791370b4dfd0f72ab952508ad260458e47fe1ee1fc3d5084668de0b0309` |
| `tests/recovery/test_connector_workspace.py` | `cb3119573f46dc7e40a257d8957ee22891c7012b4885bcfb6d68fd562cf1da33` |
| `tests/recovery/test_streaming_private.py` | `4edd5715ff1c486bc097580ec72b44b1bc2dc4bb8cac474a63c9fe55e84d6008` |

The authoritative runtime pins remain [recovery-dependency.json](recovery-dependency.json). The readiness helper resolves its default dependency directory relative to its own resource location, validates both modules before loading either, and does not use ambient imports or write bytecode. An explicit alternate directory must match those same pins.

The three original test modules are retained byte-for-byte as repository test resources. Run them from any directory with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 <repository>/tests/run_recovery_tests.py
```

The test-only launcher checks the original test hashes, loads the pinned bundled modules, and binds the two original test-module `SCRIPT` constants to those same bundled files. This is needed because the original tests locate sibling CLI scripts; `PYTHONPATH` alone would not select the relocated CLI. No second implementation copy is maintained. `--list` lists the 79 discovered cases without running them. These are synthetic offline/local-Git tests; some create hundreds of MiB of disposable data, so select suitable permitted temporary storage with `TMPDIR`.

Shipping these resources makes dependency bytes portable. It does not add a new skill mode, grant recovery/transfer authority, acquire private application sources, supply credentials, or expose the dependency's mutation commands as an automatic readiness workflow. Read [cloud setup guidance](cloud.md) for the bounded entry point and remaining acquisition limits. No previous garage governance, private selection manifest or test-output payload is included.
