import json
from pathlib import Path
c = json.loads(Path("staging.json").read_text())
assert c["log_level"] in {"debug", "info", "warning", "error"}
assert isinstance(c["retention_days"], int) and c["retention_days"] > 0
assert isinstance(c["health_request_logs"], bool)
assert c["access"] in {"team", "oncall"}
print("configuration loads; schema valid")
