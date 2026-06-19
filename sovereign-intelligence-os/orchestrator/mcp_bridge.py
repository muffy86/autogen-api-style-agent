from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPServer:
    name: str
    command: str
    args: list[str]
    env: dict[str, str]
    transport: str = "stdio"


def _expand(value: str) -> str:
    return os.path.expanduser(os.path.expandvars(value))


def load_mcp_config(path: Path) -> list[MCPServer]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    servers: list[MCPServer] = []
    for name, spec in raw.get("mcpServers", {}).items():
        servers.append(
            MCPServer(
                name=name,
                command=_expand(spec.get("command", "")),
                args=[_expand(arg) for arg in spec.get("args", [])],
                env={key: _expand(value) for key, value in spec.get("env", {}).items()},
                transport=spec.get("transport", "stdio"),
            )
        )
    return servers
