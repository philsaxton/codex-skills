# Receipt preferences

A local static page served by Python 3.10 or later. No npm packages or external services are required. Commands run from this directory.

```sh
mkdir -p scratch
python3 serve.py --port 0 --port-file scratch/server.port
```

The server prints an `http://127.0.0.1:PORT/` URL, and writes the chosen port to `scratch/server.port`. Open that exact URL in any available supported browser tool. Keep the server running while checking the page. `--port N` requests a fixed port; the default is 0. Stop the foreground server with Ctrl-C, or terminate only the process you started.

The page stores preferences in local browser storage for its origin. The visible Restore defaults button resets this demo's stored preferences and can establish a clean starting state. The controls are Email receipts, Save, Cancel, and Restore defaults. Reload means an actual browser page reload at the same URL.

`REQUEST.md` contains the current behavior requirements. `docs/smoke.md` is an existing serving check. `serve.py`, `index.html`, `app.js`, and `style.css` are product files. Save verification additions and retained evidence under `verification/`. Keep your port file and disposable data in `scratch/`, with `TMPDIR`, `TMP`, and `TEMP` directed there when supported. Use a new port file for a new process and retain useful logs/screenshots before scratch cleanup.
