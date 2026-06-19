from pathlib import Path

from orchestrator.mcp_bridge import load_mcp_config


def test_load_mcp_config_expands_user_and_env(monkeypatch, tmp_path):
    monkeypatch.setenv("FOO_DIR", str(tmp_path / "env-dir"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    config_path = tmp_path / "mcp_servers.json"
    config_path.write_text(
        """
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${FOO_DIR}", "~/workspace"],
      "env": {"ROOT_DIR": "${FOO_DIR}", "CACHE_DIR": "~/cache"}
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    servers = load_mcp_config(config_path)

    assert len(servers) == 1
    server = servers[0]
    assert server.command == "npx"
    assert server.args[2] == str(tmp_path / "env-dir")
    assert server.args[3] == str(Path(tmp_path / "home" / "workspace"))
    assert server.env["ROOT_DIR"] == str(tmp_path / "env-dir")
    assert server.env["CACHE_DIR"] == str(Path(tmp_path / "home" / "cache"))
