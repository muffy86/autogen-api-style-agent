"""MCP Server that exposes the autogen agent system as tools for IDE integration."""

from __future__ import annotations

import asyncio
import base64
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from starlette.requests import Request
from starlette.responses import JSONResponse

from .config import get_config
from .providers import ModelClientFactory
from .teams import create_team
from .utils import extract_final_response

# Lazy-initialized Playwright browser for web browsing MCP tool
_browser_instance = None


async def _get_browser():
    """Get or create a Playwright browser instance."""
    global _browser_instance
    if _browser_instance is None:
        try:
            from playwright.async_api import async_playwright

            pw = await async_playwright().start()
            _browser_instance = await pw.chromium.launch(headless=True)
        except ImportError:
            return None
    return _browser_instance


async def _handle_browse(url: str, wait_for: str | None = None) -> list[TextContent]:
    """Browse a URL and return page content."""
    try:
        browser = await _get_browser()
        if browser is None:
            return [
                TextContent(
                    type="text",
                    text="Error: Playwright not available. Install with: pip install playwright",
                )
            ]

        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=5000)

            content = await page.content()
            # Truncate if too long
            if len(content) > 40000:
                content = content[:40000] + "\n\n... [truncated]"
            return [TextContent(type="text", text=content)]
        finally:
            await page.close()
    except Exception as e:
        return [TextContent(type="text", text=f"Error browsing {url}: {e}")]


async def _handle_screenshot(url: str, full_page: bool = False) -> list[TextContent]:
    """Take a screenshot of a URL."""
    try:
        browser = await _get_browser()
        if browser is None:
            return [
                TextContent(
                    type="text",
                    text="Error: Playwright not available. Install with: pip install playwright",
                )
            ]

        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_timeout(500)  # Let content load

            screenshot_bytes = await page.screenshot(full_page=full_page)
            b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            return [TextContent(type="text", text=f"data:image/png;base64,{b64}")]
        finally:
            await page.close()
    except Exception as e:
        return [TextContent(type="text", text=f"Error taking screenshot: {e}")]


def _handle_read_file(file_path: str) -> list[TextContent]:
    """Read file contents from local filesystem."""
    try:
        from pathlib import Path

        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            return [TextContent(type="text", text=f"Error: File not found: {file_path}")]
        if not p.is_file():
            return [TextContent(type="text", text=f"Error: Not a file: {file_path}")]

        content = p.read_text(encoding="utf-8", errors="replace")
        if len(content) > 50000:
            content = content[:50000] + "\n\n... [truncated]"
        return [TextContent(type="text", text=content)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error reading file: {e}")]


def _handle_list_directory(dir_path: str = ".") -> list[TextContent]:
    """List directory contents."""
    try:
        from pathlib import Path

        p = Path(dir_path).expanduser().resolve()
        if not p.exists():
            return [TextContent(type="text", text=f"Error: Directory not found: {dir_path}")]
        if not p.is_dir():
            return [TextContent(type="text", text=f"Error: Not a directory: {dir_path}")]

        entries = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        lines = []
        for entry in entries[:50]:
            prefix = "📁 " if entry.is_dir() else "📄 "
            name = entry.name
            lines.append(f"{prefix}{name}")

        result = "\n".join(lines)
        if len(entries) > 50:
            result += f"\n\n... and {len(entries) - 50} more"
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error listing directory: {e}")]


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
                "Review code using the code review agent team (coder + reviewer + architect)."
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
                "Research a topic using the research agent team (researcher + writer + architect)."
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
        Tool(
            name="browse",
            description=(
                "Navigate to a URL and return the page content. "
                "Uses headless browser for JS-heavy sites."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_for": {
                        "type": "string",
                        "description": "Optional CSS selector to wait for before returning",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="screenshot",
            description="Take a screenshot of a URL and return base64-encoded image.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to capture"},
                    "full_page": {
                        "type": "boolean",
                        "default": False,
                        "description": "Capture full page",
                    },
                },
                "required": ["url"],
            },
        ),
        Tool(
            name="read_file",
            description="Read the contents of a file from the local filesystem.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"},
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="list_directory",
            description="List files and directories at the given path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "default": ".",
                        "description": "Directory path to list",
                    },
                },
            },
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
                f"Review this {lang} code. Focus: {focus}.\n\n```{lang}\n{arguments['code']}\n```"
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

        if name == "browse":
            url = arguments.get("url")
            wait_for = arguments.get("wait_for")
            return await _handle_browse(url, wait_for)

        if name == "screenshot":
            url = arguments.get("url")
            full_page = arguments.get("full_page", False)
            return await _handle_screenshot(url, full_page)

        if name == "read_file":
            file_path = arguments.get("path")
            return _handle_read_file(file_path)

        if name == "list_directory":
            dir_path = arguments.get("path", ".")
            return _handle_list_directory(dir_path)

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


async def run_mcp_stdio() -> None:
    """Run MCP server over stdio transport."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def run_mcp_sse(host: str = "0.0.0.0", port: int = 3000) -> None:
    """Run MCP server over SSE transport with a Starlette HTTP wrapper."""
    import uvicorn
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.types import Receive, Scope, Send

    try:
        from mcp.server.sse import SseServerTransport
    except ImportError as exc:
        raise RuntimeError(
            "Installed mcp package does not provide SseServerTransport. "
            "Upgrade the mcp dependency to use SSE transport."
        ) from exc

    server = create_mcp_server()
    sse = SseServerTransport("/messages/")

    class SSEEndpoint:
        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            async with sse.connect_sse(scope, receive, send) as streams:
                await server.run(
                    streams[0],
                    streams[1],
                    server.create_initialization_options(),
                )

    class MessageEndpoint:
        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            await sse.handle_post_message(scope, receive, send)

    async def handle_health(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    app = Starlette(
        routes=[
            Route("/sse", endpoint=SSEEndpoint()),
            Route("/messages/", endpoint=MessageEndpoint(), methods=["POST"]),
            Route("/health", endpoint=handle_health),
        ]
    )

    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


def main() -> None:
    """Entry point for MCP server."""
    asyncio.run(run_mcp_stdio())


if __name__ == "__main__":
    main()
