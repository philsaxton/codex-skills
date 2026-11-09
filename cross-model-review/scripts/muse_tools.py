"""Observe the tools Muse would offer on an exec request without calling a model."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import secrets
import subprocess
import threading


def tool_names(request):
    if not isinstance(request.get("input"), list) or not request.get("model"):
        raise ValueError("unexpected Responses request")
    tools = request.get("tools", [])
    if not isinstance(tools, list):
        raise ValueError("unexpected tools")
    # Muse 1.4.14 can group its functions into a Responses namespace.
    if len(tools) == 1 and tools[0].get("type") == "namespace" and tools[0].get("name") == "muse":
        tools = tools[0]["tools"]
        if not isinstance(tools, list):
            raise ValueError("unexpected namespace")
    names = [tool["name"] for tool in tools if tool["type"] == "function"]
    if len(names) != len(tools) or not all(isinstance(n, str) and n for n in names):
        raise ValueError("unrecognized tool")
    return names


def offered_tools(command, root, env):
    offers = []
    key = secrets.token_hex(16)

    class Receiver(BaseHTTPRequestHandler):
        timeout = 3

        def log_message(self, *args):
            pass

        def do_POST(self):
            try:
                if self.path != "/responses" or self.headers.get("Authorization") != "Bearer " + key:
                    raise ValueError("unexpected path")
                length = int(self.headers["Content-Length"])
                if not 0 < length <= 4 * 1024 * 1024:
                    raise ValueError("unexpected request size")
                offers.append(tool_names(json.loads(self.rfile.read(length))))
            except (ValueError, KeyError, TypeError, AttributeError):
                offers.append(None)
            # Never return model output or log headers, request content or CLI diagnostics.
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"Local configuration probe","type":"invalid_request_error"}}')

    with HTTPServer(("127.0.0.1", 0), Receiver) as server:
        worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        worker.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}"
            run = subprocess.run([*command, "--base-url", url, "--api-key-stdin",
                                  "Configuration check only."], input=(key + "\n").encode(),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 cwd=root, env={**env, "NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"},
                                 timeout=30, check=False)
        finally:
            server.shutdown()
            worker.join()
    if run.returncode == 0 or not offers or any(names is None or names != offers[0] for names in offers):
        raise ValueError("no consistent tool list on a rejected local Responses request")
    return offers[0]
