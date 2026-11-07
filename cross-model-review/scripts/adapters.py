"""Native, fresh-session reviewer commands. No shell evaluation or fallback."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess


DEFAULT_MODELS = {
    "muse": "muse-wonder-full-1.0",
    "codex": "gpt-6-astra",
    "claude": "claude-opus-5-5",
}
DEFAULT_EFFORT = "max"


class AdapterError(ValueError):
    def __init__(self, message, notes=()):
        super().__init__(message)
        self.details = {"configuration_notes": list(notes)}


def environment():
    # Git overrides could make packet capture and the review use different repos.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", MUSE_NO_AUTO_UPDATE="1", NO_COLOR="1")
    return env


def note(notes, inspection, limitation, **facts):
    # Only caller-supplied labels and known facts, never raw config or stderr.
    notes.append({"inspection": inspection, "limitation": limitation, **facts})


def probe(argv, root, env, notes, label):
    try:
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                                timeout=30, check=False)
    except subprocess.TimeoutExpired:
        note(notes, label, "inspection timed out")
        return None
    except OSError as exc:
        note(notes, label, "inspection unavailable", errno=exc.errno)
        return None
    if result.returncode:
        note(notes, label, "inspection exited unsuccessfully", exit_code=result.returncode)
        return None
    try:
        return result.stdout.decode("utf-8", "strict")
    except UnicodeError:
        note(notes, label, "inspection output is not UTF-8")
        return None


def inspect_json(raw, notes, label):
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        note(notes, label, "inspection output is not valid JSON")
        return None


def muse_config(path, notes, label):
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    except OSError as exc:
        note(notes, label, "local configuration could not be read", errno=exc.errno)
        return
    except (ValueError, UnicodeError):
        raise AdapterError(f"Malformed Muse {label}; expected a JSON object", notes) from None
    if not isinstance(config, dict):
        raise AdapterError(f"Malformed Muse {label}; expected a JSON object", notes)
    keys = {"hooks", "managed_hooks_path", "mcp_servers", "mcpServers", "plugins"}
    if any(config.get(key) for key in keys):
        raise AdapterError(f"Muse {label} contains hook, MCP or plugin configuration requiring resolution", notes)
    if set(config) - keys:
        note(notes, label, "other configuration fields were not assessed")


def muse_preflight(executable, root, env, notes):
    status = probe([executable, "config", "status"], root, env, notes, "muse-config-status")
    if status is not None:
        sources = [line for line in status.splitlines() if "source_class=" in line]
        if not sources or any("state=absent" not in line for line in sources):
            note(notes, "muse-config-status", "configuration sources are present or not fully described")
    settings = Path(env.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "muse/settings.json"
    muse_config(settings, notes, "user-settings")
    for name, label in ((".muse/hooks.json", "project-hooks"), (".muse/settings.json", "project-settings")):
        muse_config(root / name, notes, label)
    raw = probe([executable, "plugins", "list", "--json"], root, env, notes, "muse-plugins")
    plugins = inspect_json(raw, notes, "muse-plugins")
    if isinstance(plugins, dict) and isinstance(plugins.get("plugins"), list):
        if plugins["plugins"]:
            raise AdapterError("Muse installed plugins require isolation resolution", notes)
    elif raw is not None:
        note(notes, "muse-plugins", "plugin list is unavailable in the inspection output")


def build(tool, model, effort, root, packet, report, env):
    notes = []
    executable = shutil.which(tool, path=env.get("PATH"))
    if not executable:
        raise AdapterError(f"Reviewer CLI is unavailable: {tool}")
    if tool == "claude":
        # Safe mode skips customizations, plugins and hooks; the tools allowlist
        # leaves only file inspection. Bare mode would change authentication.
        return [executable, "--print", "--model", model, "--effort", effort,
                "--safe-mode", "--restricted", "--no-session-persistence", "--output-format", "text",
                "--tools", "Read,Glob,Grep", "--allowedTools", "Read,Glob,Grep",
                "--disallowedTools", "mcp__*", "--permission-mode", "dontAsk",
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}'], notes
    if tool == "muse":
        muse_preflight(executable, root, env, notes)
        command = [executable, "exec", "--model", model, "--reasoning-effort", effort,
                "--preset", "native-basic", "--disable-write", "--disable-shell",
                "--disable-web-tools", "--disable-reminders", "--disable-request-user-input",
                "--no-foreign-personal-context", "--no-session-log",
                "--approval-mode", "never", "--approval-judge", "off",
                "-c", 'run.toolset=["read_file"]',
                "-c", "hooks={}", "-c", "managed_hooks_path=null",
                "--workspace", str(root), "--prompt-file", str(packet)]
        # The local echo provider validates this preset/tool registry without
        # sending a packet or consuming a reviewer exchange.
        probe([*command[:2], *command[6:-2], "--provider", "echo",
               "review adapter configuration probe"], root, env, notes, "muse-echo")
        return command, notes
    if tool == "codex":
        disabled = ("apps", "plugins", "hooks", "multi_agent", "computer_use",
                    "browser_use", "in_app_browser", "image_generation")
        flags = [item for name in disabled for item in ("--disable", name)]
        flags += ["-c", 'approval_policy="never"', "-c", 'sandbox_mode="read-only"',
                  "-c", 'web_search="disabled"']
        # Read back the same config layers the execution uses. In particular,
        # mcp_servers={} merges rather than clears an existing server map.
        raw = probe([executable, *flags, "mcp", "list", "--json"], root, env, notes, "codex-mcp-inventory")
        servers = inspect_json(raw, notes, "codex-mcp-inventory")
        if (not isinstance(servers, list) or any(not isinstance(s, dict)
                or not isinstance(s.get("name"), str) or not s["name"].strip() for s in servers)):
            raise AdapterError("Codex MCP inventory is unavailable or unusable; cannot construct required exact-name disable overrides", notes)
        if servers:
            entries = ",".join(json.dumps(s["name"]) + "={enabled=false}" for s in servers)
            flags += ["-c", "mcp_servers={" + entries + "}"]
        raw = probe([executable, *flags, "mcp", "list", "--json"], root, env, notes, "codex-mcp-readback")
        observed = inspect_json(raw, notes, "codex-mcp-readback")
        names = {s["name"] for s in servers}
        if isinstance(observed, list):
            rows = [s for s in observed if isinstance(s, dict)]
            if any(s.get("enabled") is True for s in rows):
                raise AdapterError("Codex MCP readback reports an enabled server", notes)
            if any(isinstance(s.get("name"), str) and s["name"].strip() and s["name"] not in names for s in rows):
                raise AdapterError("Codex MCP readback reports a server outside the disable map; refresh the inventory", notes)
            if (len(rows) != len(observed) or any(not isinstance(s.get("name"), str)
                    or s["name"] not in names or type(s.get("enabled")) is not bool for s in rows)
                    or {s.get("name") for s in rows if isinstance(s.get("name"), str)} != names):
                note(notes, "codex-mcp-readback", "MCP readback fields are incomplete")
        elif raw is not None:
            note(notes, "codex-mcp-readback", "MCP server list is unavailable in the inspection output")
        raw = probe([executable, *flags, "features", "list"], root, env, notes, "codex-features")
        if raw is not None:
            rows = [p for line in raw.splitlines() if (p := line.split())]
            if any(p[0] in disabled and len(p) >= 2 and p[-1] == "true" for p in rows):
                raise AdapterError("Codex feature readback reports an enabled capability", notes)
            missing = sorted(set(disabled) - {p[0] for p in rows if len(p) >= 2 and p[-1] == "false"})
            if missing:
                note(notes, "codex-features", "feature readback fields are incomplete", features=missing)
        return [executable, "exec", *flags, "--ignore-rules", "--ephemeral",
                "--sandbox", "read-only", "--model", model,
                "-c", 'model_reasoning_effort=' + json.dumps(effort),
                "-C", str(root), "--output-last-message", str(report), "-"], notes
    raise AdapterError(f"Unsupported tool: {tool}")
