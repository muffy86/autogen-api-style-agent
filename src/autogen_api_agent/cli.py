"""Typer CLI application for the AutoGen API Style Agent."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="agent",
    help="AutoGen API Style Agent — Multi-agent productivity system",
    no_args_is_help=True,
)
console = Console()


@app.command()
def chat(
    message: str = typer.Argument(..., help="Message to send to the agent team"),
    team: str = typer.Option("productivity", "--team", "-t", help="Team to use"),
    provider: str = typer.Option("auto", "--provider", "-p", help="LLM provider"),
    stream: bool = typer.Option(True, "--stream/--no-stream", help="Stream output"),
):
    """Send a message to an agent team and get a response."""
    from .config import get_config
    from .providers import ModelClientFactory
    from .teams import create_team
    from .utils import extract_final_response, extract_message_text

    config = get_config()
    factory = ModelClientFactory(config)
    prov = None if provider == "auto" else provider

    try:
        team_obj = create_team(team_name=team, factory=factory, provider=prov)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    async def _run():
        if stream:
            async for msg in team_obj.run_stream(task=message):
                text = extract_message_text(msg)
                if text:
                    console.print(text, end="")
            console.print()
        else:
            result = await team_obj.run(task=message)
            console.print(extract_final_response(result))

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/dim]")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload", "-r"),
):
    """Start the FastAPI server."""
    import uvicorn

    console.print(f"[bold green]Starting server on {host}:{port}[/bold green]")
    uvicorn.run("autogen_api_agent.server:app", host=host, port=port, reload=reload)


@app.command()
def providers():
    """List available LLM providers and their status."""
    from .config import get_config
    from .providers import ModelClientFactory

    config = get_config()
    factory = ModelClientFactory(config)
    available = factory.list_available()
    all_providers = ["openai", "together", "openrouter", "google", "kimi", "mistral"]

    table = Table(title="LLM Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Default Model", style="yellow")

    for p in all_providers:
        if p in available:
            table.add_row(p, "Ready", available[p])
        else:
            table.add_row(p, "No API key", "-")

    console.print(table)


@app.command()
def teams():
    """List available agent teams."""
    table = Table(title="Agent Teams")
    table.add_column("Name", style="cyan")
    table.add_column("Agents", style="green")
    table.add_column("Description")

    table.add_row(
        "productivity",
        "8",
        "Full team: orchestrator, coder, reviewer, researcher, architect, tester, writer, devops",
    )
    table.add_row("code_review", "3", "Code review: coder, reviewer, architect")
    table.add_row("research", "3", "Research: researcher, writer, architect")
    table.add_row("quick", "1", "Single agent with all tools")

    console.print(table)


@app.command()
def config():
    """Show current configuration (API keys masked)."""
    from .config import get_config

    cfg = get_config()

    def _mask(value: str | None) -> str:
        if not value:
            return "[dim]not set[/dim]"
        if len(value) <= 8:
            return "****"
        return value[:4] + "..." + value[-4:]

    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("host", cfg.host)
    table.add_row("port", str(cfg.port))
    table.add_row("debug", str(cfg.debug))
    table.add_row("default_provider", cfg.default_provider)
    table.add_row("default_team", cfg.default_team)
    table.add_row("max_turns", str(cfg.max_turns))
    table.add_row("timeout_seconds", str(cfg.timeout_seconds))
    table.add_row("session_ttl_minutes", str(cfg.session_ttl_minutes))

    console.print(table)
    console.print()

    keys_table = Table(title="API Keys")
    keys_table.add_column("Provider", style="cyan")
    keys_table.add_column("Key", style="yellow")
    keys_table.add_column("Model", style="green")

    pc = cfg.providers
    keys_table.add_row("openai", _mask(pc.openai_api_key), pc.openai_model)
    keys_table.add_row("together", _mask(pc.together_api_key), pc.together_model)
    keys_table.add_row("openrouter", _mask(pc.openrouter_api_key), pc.openrouter_model)
    keys_table.add_row("google", _mask(pc.google_api_key), pc.google_model)
    keys_table.add_row("kimi", _mask(pc.moonshot_api_key), pc.kimi_model)
    keys_table.add_row("mistral", _mask(pc.mistral_api_key), pc.mistral_model)

    console.print(keys_table)


@app.command()
def interactive(
    team: str = typer.Option("quick", "--team", "-t"),
    provider: str = typer.Option("auto", "--provider", "-p"),
):
    """Start an interactive chat session (REPL)."""
    from .config import get_config
    from .providers import ModelClientFactory
    from .teams import create_team
    from .utils import extract_message_text

    console.print(Panel("AutoGen Interactive Mode", subtitle="Type /help for commands"))

    cfg = get_config()
    factory = ModelClientFactory(cfg)
    current_team = team
    current_provider = provider

    while True:
        try:
            user_input = console.input("[bold cyan]you>[/bold cyan] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input == "/quit":
            break

        if user_input == "/help":
            console.print("/quit          - exit")
            console.print("/team <name>   - switch team")
            console.print("/provider <n>  - switch provider")
            console.print("/teams         - list teams")
            console.print("/providers     - list providers")
            continue

        if user_input.startswith("/team "):
            current_team = user_input.split(" ", 1)[1].strip()
            console.print(f"[green]Switched to team: {current_team}[/green]")
            continue

        if user_input.startswith("/provider "):
            current_provider = user_input.split(" ", 1)[1].strip()
            console.print(f"[green]Switched to provider: {current_provider}[/green]")
            continue

        if user_input == "/teams":
            teams()
            continue

        if user_input == "/providers":
            providers()
            continue

        prov = None if current_provider == "auto" else current_provider

        try:
            team_obj = create_team(team_name=current_team, factory=factory, provider=prov)
        except Exception as exc:
            console.print(f"[bold red]Error creating team:[/bold red] {exc}")
            continue

        async def _run(t, msg):
            async for m in t.run_stream(task=msg):
                text = extract_message_text(m)
                if text:
                    console.print(f"[bold green]agent>[/bold green] {text}")

        try:
            asyncio.run(_run(team_obj, user_input))
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
        except Exception as exc:
            console.print(f"[bold red]Error:[/bold red] {exc}")

    console.print("[dim]Goodbye![/dim]")


@app.command(name="mcp-serve")
def mcp_serve(
    transport: str = typer.Option("stdio", "--transport", help="MCP transport: stdio or sse"),
    port: int = typer.Option(3000, "--port", "-p", help="Port for SSE transport"),
):
    """Start the MCP server for IDE integration (Trae.ai, Cursor, Claude Code)."""
    if transport == "stdio":
        console.print("[bold green]Starting MCP server (stdio)...[/bold green]")
        from .mcp_server import run_mcp_stdio

        asyncio.run(run_mcp_stdio())
    else:
        console.print(f"[bold green]Starting MCP server (SSE on port {port})...[/bold green]")
        from .mcp_server import run_mcp_sse

        asyncio.run(run_mcp_sse(port=port))
