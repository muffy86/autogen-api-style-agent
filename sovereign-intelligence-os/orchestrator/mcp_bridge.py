from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPServer:
    name: str
    command: str
    args: list[str]
    env: dict[str, str]
    transport: str = "stdio"


def load_mcp_config(path: Path) -> list[MCPServer]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    servers: list[MCPServer] = []
    for name, spec in raw.get("mcpServers", {}).items():
        servers.append(
            MCPServer(
                name=name,
                command=spec.get("command", ""),
                args=list(spec.get("args", [])),
                env=dict(spec.get("env", {})),
                transport=spec.get("transport", "stdio"),
            )
        )
    return servers
