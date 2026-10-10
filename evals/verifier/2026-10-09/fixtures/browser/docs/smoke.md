# Local preview smoke check

Start the server using the README, then run this from the project directory:

```sh
python3 - <<'PYCODE'
from pathlib import Path
from urllib.request import urlopen
port = int(Path("scratch/server.port").read_text())
with urlopen(f"http://127.0.0.1:{port}/") as response:
    page = response.read().decode()
    assert response.status == 200
    assert "<title>Receipt preferences</title>" in page
print("Preview served")
PYCODE
```

This confirms that the preview is served. It does not interact with the page or check browser storage.
