# Durable event register

Python 3.10 or later; standard library SQLite only. Run from this directory:

```sh
python3 -m unittest discover -s tests -v
```

`store.py` is the library, `tests/` supplies its behavior checks, and `REQUEST.md` defines the review scope. Tests use temporary databases and close their connections. `check.py` can preserve complete command receipts. Keep any added methods under `verification/` and retained reports under the named evidence/report directories.
