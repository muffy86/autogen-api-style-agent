# CLAUDE.md — Claude Code Configuration

This is an AutoGen multi-agent productivity system with 6+ LLM providers.

## Project Structure
- `src/autogen_api_agent/` — Main package
  - `providers/` — LLM provider clients (OpenAI, Together, OpenRouter, Google, Kimi, Mistral)
  - `agents/` — 8 specialized agents (orchestrator, coder, reviewer, researcher, architect, tester, writer, devops)
  - `teams/` — Team compositions (productivity, code_review, research, quick)
  - `tools/` — Agent tools (file ops, web search, GitHub, shell, code analysis)
  - `server.py` — FastAPI HTTP server
  - `cli.py` — Typer CLI
  - `mcp_server.py` — MCP server for IDE integration

## Development Commands
- `pip install -e ".[dev]"` — Install with dev deps
- `agent serve` — Start HTTP API on :8000
- `agent chat "message"` — CLI chat
- `agent interactive` — REPL mode
- `agent mcp-serve` — Start MCP server
- `pytest` — Run tests
- `ruff check src/` — Lint

## Key Patterns
- All providers use `OpenAIChatCompletionClient` with custom `base_url` (except Google which uses native `GeminiChatCompletionClient`)
- Agents are created via factory functions in `agents/` modules
- Teams are composed in `teams/` modules using AutoGen's `SelectorGroupChat`, `RoundRobinGroupChat`, etc.
- Config loaded from `.env` via `pydantic-settings`

## When Modifying
- Add new providers in `providers/` + update `factory.py` + `config.py`
- Add new agents in `agents/` + register in team compositions
- Add new tools in `tools/` + assign to relevant agents
- Add new API endpoints in `server.py` + CLI commands in `cli.py`
