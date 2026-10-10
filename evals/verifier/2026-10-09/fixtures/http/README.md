# Local quote API

Requires Python 3.10 or later, with no third-party packages. Commands run from this directory. The API is local only and needs no credentials or network service.

`data/catalog.json` is required runtime input supplied by the shop; do not invent replacement prices if it is absent. `api.json` supplies the current `quote_path`. Both files are read on startup. The server exits 78 before opening a socket when these prerequisites cannot be loaded.

Existing input-shape check:

```sh
python3 checks/check_catalog.py
```

Start the service on an available local port:

```sh
mkdir -p scratch
python3 server.py --port 0 --port-file scratch/server.port
```

The process stays in the foreground and prints its actual URL. `scratch/server.port` contains the selected port. `--port N` can request a fixed port; the default is 0. Stop the server with Ctrl-C, or terminate only the process you started. A new run should use a fresh scratch directory or remove its own stale port file first.

GET the configured quote path with URL query parameters `sku` and `quantity`. Responses are JSON. `REQUEST.md` is the behavior authority. `checks/check_catalog.py` checks catalog structure only; it does not start or query the service.

`server.py` is product code. Save reusable verification additions and evidence in `verification/`; keep disposable ports, temporary data, and transient processes under your own `scratch/`. Set `TMPDIR`, `TMP`, and `TEMP` to that directory where supported. Retain useful logs or observations before cleaning scratch.
