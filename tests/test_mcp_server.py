from __future__ import annotations

from mcp.server import Server

from autogen_api_agent.mcp_server import _build_tools, create_mcp_server


def test_build_tools_returns_nine_tools_with_correct_names() -> None:
    tools = _build_tools()

    assert len(tools) == 9
    assert [tool.name for tool in tools] == [
        "agent_chat",
        "agent_code_review",
        "agent_research",
        "list_providers",
        "list_teams",
        "browse",
        "screenshot",
        "read_file",
        "list_directory",
    ]


def test_create_mcp_server_returns_server_instance() -> None:
    server = create_mcp_server()

    assert isinstance(server, Server)


def test_tool_schemas_have_required_fields() -> None:
    tools = {tool.name: tool for tool in _build_tools()}

    assert tools["agent_chat"].inputSchema["required"] == ["message"]
    assert tools["agent_code_review"].inputSchema["required"] == ["code"]
    assert tools["agent_research"].inputSchema["required"] == ["topic"]
    assert tools["list_providers"].inputSchema["type"] == "object"
    assert tools["list_teams"].inputSchema["type"] == "object"
    assert tools["browse"].inputSchema["required"] == ["url"]
    assert tools["screenshot"].inputSchema["required"] == ["url"]
    assert tools["read_file"].inputSchema["required"] == ["path"]
