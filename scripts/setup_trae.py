"""Auto-configure Trae IDE for this project."""
import json
import os
import sys
from pathlib import Path


def find_trae_config_dir() -> Path | None:
    """Detect Trae config location by platform."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "Trae" / "User"
    elif sys.platform == "win32":
        appdata = os.environ.get("APPDATA", "")
        base = Path(appdata) / "Trae" / "User" if appdata else None
    else:
        base = Path.home() / ".config" / "Trae" / "User"

    if base and base.exists():
        return base
    return None


def setup_trae() -> None:
    """Detect Trae config location and install MCP settings."""
    project_root = Path(__file__).resolve().parent.parent
    trae_mcp = project_root / ".trae" / "mcp_settings.json"

    if not trae_mcp.exists():
        print("❌ .trae/mcp_settings.json not found")
        return

    mcp_config = json.loads(trae_mcp.read_text())

    env_resolved: dict[str, dict] = {}
    for server_name, server_config in mcp_config.get("mcpServers", {}).items():
        resolved = dict(server_config)
        if "env" in resolved:
            new_env = {}
            for k, v in resolved["env"].items():
                if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                    env_var = v[2:-1]
                    new_env[k] = os.environ.get(env_var, v)
                else:
                    new_env[k] = v
            resolved["env"] = new_env

        args = resolved.get("args", [])
        resolved["args"] = [
            a.replace("${workspaceFolder}", str(project_root)) if isinstance(a, str) else a
            for a in args
        ]
        env_resolved[server_name] = resolved

    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    vscode_mcp = vscode_dir / "mcp.json"
    vscode_mcp.write_text(json.dumps({"servers": env_resolved}, indent=2) + "\n")

    print(f"✅ Trae MCP config written to {vscode_mcp}")
    print(f"✅ {len(env_resolved)} MCP servers configured")

    trae_config_dir = find_trae_config_dir()
    if trae_config_dir:
        global_mcp = trae_config_dir / "globalMcpSettings.json"
        existing = {}
        if global_mcp.exists():
            try:
                existing = json.loads(global_mcp.read_text())
            except json.JSONDecodeError:
                pass

        global_servers = {}
        for name, cfg in mcp_config.get("mcpServers", {}).items():
            global_cfg = dict(cfg)
            if "args" in global_cfg and any(
                isinstance(a, str) and "${workspaceFolder}" in a
                for a in global_cfg["args"]
            ):
                continue
            global_servers[name] = global_cfg

        servers = existing.get("mcpServers", {})
        servers.update(global_servers)
        existing["mcpServers"] = servers
        global_mcp.write_text(json.dumps(existing, indent=2) + "\n")
        print(f"✅ Global Trae config updated: {global_mcp}")
        if global_servers != mcp_config.get("mcpServers", {}):
            print("   ℹ️  Skipped project-specific servers (${workspaceFolder}) in global config")
    else:
        print("ℹ️  Trae IDE config directory not found (Trae not installed or first run)")
        print("   Project-level .vscode/mcp.json will be used when Trae opens this folder")

    print("\nConfigured servers:")
    for name, config in env_resolved.items():
        desc = config.get("description", "No description")
        print(f"  • {name}: {desc}")


if __name__ == "__main__":
    setup_trae()
