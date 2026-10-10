# Paid invoice report

Requires Python 3.10 or later, with no third-party packages. Run commands from this project directory.

```sh
python3 -m unittest discover -s tests -v
```

The existing suite checks the report's observable JSON and exit/error behavior. A normal manual invocation is:

```sh
mkdir -p scratch
python3 report.py --input data/invoices.csv --output scratch/report.json
cat scratch/report.json
```

`REQUEST.md` contains the current requirements. `report.py` is product code; `data/` and `tests/` are supplied project inputs. Verification additions belong in `verification/`. Put temporary reports under your own `scratch/`, and direct `TMPDIR`, `TMP`, and `TEMP` there when supported. Keep evidence that will be cited in `verification/`, outside disposable scratch. No service or external access is needed.
