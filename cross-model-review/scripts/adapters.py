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
    pass


def environment():
    # Git overrides could make packet capture and the review use different repos.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", MUSE_NO_AUTO_UPDATE="1", NO_COLOR="1")
    return env


def probe(argv, root, env):
    result = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                            timeout=30, check=False)
    if result.returncode:
        raise AdapterError(f"Configuration inspection failed: {argv[0]} {' '.join(argv[1:3])}\n"
                           + result.stderr.decode("utf-8", "replace"))
    return result.stdout.decode("utf-8", "strict")


def muse_preflight(executable, root, env):
    """Refuse configuration planes we cannot reliably disable in Muse 1.4."""
    status = probe([executable, "config", "status"], root, env)
    sources = [line for line in status.splitlines() if "source_class=" in line]
    if not sources or any("state=absent" not in line for line in sources):
        raise AdapterError("A Muse config-status source is active or unknown; cannot verify isolation")
    settings = Path(env.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "muse/settings.json"
    config = json.loads(settings.read_text()) if settings.exists() else {}
    if not isinstance(config, dict):
        raise AdapterError("Unrecognized Muse user configuration")
    if config.get("hooks") or config.get("managed_hooks_path"):
        raise AdapterError("Muse user hooks require a separately qualified isolation setup")
    if config.get("mcp_servers") or config.get("mcpServers"):
        raise AdapterError("Muse MCP configuration requires a separately qualified isolation setup")
    plugins = json.loads(probe([executable, "plugins", "list", "--json"], root, env))
    if not isinstance(plugins, dict) or plugins.get("plugins") != []:
        raise AdapterError("Muse installed plugins require a separately qualified isolation setup")
    # Project hooks can run independently of the model's tool allowlist.
    for name in (".muse/hooks.json", ".muse/settings.json"):
        if (root / name).exists():
            raise AdapterError(f"Muse project configuration requires isolation review: {name}")


def build(tool, model, effort, root, packet, report, env):
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
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    if tool == "muse":
        muse_preflight(executable, root, env)
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
               "review adapter configuration probe"], root, env)
        return command
    if tool == "codex":
        disabled = ("apps", "plugins", "hooks", "multi_agent", "computer_use",
                    "browser_use", "in_app_browser", "image_generation")
        flags = [item for name in disabled for item in ("--disable", name)]
        flags += ["-c", 'approval_policy="never"', "-c", 'sandbox_mode="read-only"',
                  "-c", 'web_search="disabled"']
        # Read back the same config layers the execution uses. In particular,
        # mcp_servers={} merges rather than clears an existing server map.
        servers = json.loads(probe([executable, *flags, "mcp", "list", "--json"], root, env))
        if not isinstance(servers, list) or any(not isinstance(s, dict) or not isinstance(s.get("name"), str) for s in servers):
            raise AdapterError("Unrecognized Codex MCP inventory")
        if servers:
            entries = ",".join(json.dumps(s["name"]) + "={enabled=false}" for s in servers)
            flags += ["-c", "mcp_servers={" + entries + "}"]
        observed = json.loads(probe([executable, *flags, "mcp", "list", "--json"], root, env))
        if not isinstance(observed, list) or any(not isinstance(s, dict) or s.get("enabled") is not False for s in observed):
            raise AdapterError("Codex MCP isolation could not be established")
        features = {p[0]: p[-1] for line in probe([executable, *flags, "features", "list"], root, env).splitlines()
                    if (p := line.split())}
        if any(features.get(name) != "false" for name in disabled):
            raise AdapterError("Codex feature isolation could not be established")
        return [executable, "exec", *flags, "--ignore-rules", "--ephemeral",
                "--sandbox", "read-only", "--model", model,
                "-c", 'model_reasoning_effort=' + json.dumps(effort),
                "-C", str(root), "--output-last-message", str(report), "-"]
    raise AdapterError(f"Unsupported tool: {tool}")
