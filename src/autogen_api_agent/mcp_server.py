"""MCP Server that exposes the autogen agent system as tools for IDE integration.

Supports Trae.ai, Cursor, Claude Code, and any other MCP-compatible client.
Primary transport is stdio; SSE can be added later.
"""
from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import get_config
from .providers import ModelClientFactory
from .teams import create_team
from .utils import extract_final_response


def _build_tools() -> list[Tool]:
    """Return the static list of tools exposed by this MCP server."""
    return [
        Tool(
            name="agent_chat",
            description=(
                "Send a task to the multi-agent productivity team. "
                "Returns the team's collaborative response."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The task or question",
                    },
                    "team": {
                        "type": "string",
                        "enum": ["productivity", "code_review", "research", "quick"],
                        "default": "quick",
                    },
                    "provider": {
                        "type": "string",
                        "description": (
                            "LLM provider (auto, openai, together, openrouter, "
                            "google, kimi, mistral)"
                        ),
                        "default": "auto",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="agent_code_review",
            description=(
                "Review code using the code review agent team "
                "(coder + reviewer + architect)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to review",
                    },
                    "language": {"type": "string", "default": "python"},
                    "focus": {
                        "type": "string",
                        "description": "Review focus: security, performance, style, all",
                        "default": "all",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="agent_research",
            description=(
                "Research a topic using the research agent team "
                "(researcher + writer + architect)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to research",
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["quick", "thorough"],
                        "default": "quick",
                    },
                },
                "required": ["topic"],
            },
        ),
        Tool(
            name="list_providers",
            description="List available LLM providers and their connection status.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_teams",
            description="List available agent teams and their capabilities.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


def create_mcp_server() -> Server:
    """Create and configure the MCP server with all tool handlers."""
    server = Server("autogen-agent")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return _build_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        config = get_config()
        factory = ModelClientFactory(config)

        if name == "agent_chat":
            prov = arguments.get("provider")
            if prov == "auto":
                prov = None
            team_obj = create_team(
                team_name=arguments.get("team", "quick"),
                factory=factory,
                provider=prov,
            )
            result = await team_obj.run(task=arguments["message"])
            response = extract_final_response(result)
            return [TextContent(type="text", text=response)]

        if name == "agent_code_review":
            team_obj = create_team("code_review", factory)
            lang = arguments.get("language", "python")
            focus = arguments.get("focus", "all")
            prompt = (
                f"Review this {lang} code. Focus: {focus}.\n\n"
                f"```{lang}\n{arguments['code']}\n```"
            )
            result = await team_obj.run(task=prompt)
            return [TextContent(type="text", text=extract_final_response(result))]

        if name == "agent_research":
            team_obj = create_team("research", factory)
            depth = arguments.get("depth", "quick")
            prompt = f"Research this topic ({depth} analysis): {arguments['topic']}"
            result = await team_obj.run(task=prompt)
            return [TextContent(type="text", text=extract_final_response(result))]

        if name == "list_providers":
            available = factory.list_available()
            return [TextContent(type="text", text=json.dumps(available, indent=2))]

        if name == "list_teams":
            teams_info = {
                "productivity": (
                    "Full 8-agent team (orchestrator, coder, reviewer, "
                    "researcher, architect, tester, writer, devops)"
                ),
                "code_review": "3-agent code review team (coder, reviewer, architect)",
                "research": "3-agent research team (researcher, writer, architect)",
                "quick": "Single agent with all tools",
            }
            return [TextContent(type="text", text=json.dumps(teams_info, indent=2))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


async def run_mcp_stdio() -> None:
    """Run MCP server over stdio transport."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def main() -> None:
    """Entry point for MCP server."""
    asyncio.run(run_mcp_stdio())


if __name__ == "__main__":
    main()
