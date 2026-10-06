# AutoGen API Style Agent

[![CI](https://github.com/muffy86/autogen-api-style-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/muffy86/autogen-api-style-agent/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AutoGen 0.7.5](https://img.shields.io/badge/AutoGen-0.7.5-purple.svg)](https://github.com/microsoft/autogen)

> Multi-agent AI productivity system powered by [Microsoft AutoGen](https://github.com/microsoft/autogen) with 6 LLM providers, 8 specialized agents, and first-class IDE integration.

---

## Features

- **6 LLM Providers** — OpenAI, Together.ai, OpenRouter, Google Gemini, Kimi (Moonshot), Mistral — hot-swap between them
- **8 Specialized Agents** — Orchestrator, Coder, Reviewer, Researcher, Architect, Tester, Writer, DevOps
- **4 Team Compositions** — Productivity (full 8), Code Review (3), Research (3), Quick (1)
- **Multi-Interface** — FastAPI HTTP API, Typer CLI, MCP server for IDEs
- **IDE Integration** — Trae.ai custom agents + MCP, Claude Code, Cursor, VS Code
- **Zero-Config Bootstrap** — One command to install on Unix or Windows
- **Docker Ready** — Multi-stage build with docker-compose for API + MCP services
- **CI/CD** — GitHub Actions with lint, multi-version test matrix, Docker build

---

## Quick Start

```bash
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
bash scripts/bootstrap.sh
```

The bootstrap script will:
1. Verify Python 3.10+ and Node.js
2. Create a virtual environment
3. Install all dependencies
4. Set up `.env` from template
5. Auto-detect API keys from your environment
6. Install MCP servers for IDE integration

---

## Installation

### From Source (Recommended)

```bash
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp configs/.env.example .env
# Edit .env with your API keys
```

### With Docker

```bash
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
cp configs/.env.example .env
# Edit .env with your API keys
docker-compose up
```

### Windows (PowerShell)

```powershell
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
.\scripts\bootstrap.ps1
```

---

## Configuration

Copy the example environment file and add at least one provider API key:

```bash
cp configs/.env.example .env
```

### Provider API Keys

| Provider | Env Variable | Get a Key |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Together.ai | `TOGETHER_API_KEY` | [api.together.xyz](https://api.together.xyz/settings/api-keys) |
| OpenRouter | `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| Google Gemini | `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| Kimi (Moonshot) | `MOONSHOT_API_KEY` | [platform.moonshot.cn](https://platform.moonshot.cn/console/api-keys) |
| Mistral | `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/api-keys/) |

Only one provider key is required. The system automatically detects available providers and falls back gracefully.

### Server Configuration

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | API server bind address |
| `PORT` | `8000` | API server port |
| `LOG_LEVEL` | `info` | Logging level (debug, info, warning, error) |
| `DEFAULT_PROVIDER` | `openai` | Default LLM provider |
| `SESSION_TTL_SECONDS` | `3600` | Session timeout |
| `MAX_SESSIONS` | `100` | Maximum concurrent sessions |

---

## Usage

### CLI

```bash
# Check available providers
agent providers

# Quick chat (uses default provider)
agent chat "Explain Python decorators"

# Chat with specific provider
agent chat "Write a REST API" --provider together

# Interactive REPL
agent interactive

# Code review from file
agent review src/autogen_api_agent/server.py

# Research a topic
agent research "AutoGen vs CrewAI comparison" --depth thorough

# Start servers
agent serve              # HTTP API on :8000
agent serve --reload     # With hot-reload for development
agent mcp-serve          # MCP server for IDE integration
```

### HTTP API

Start the server:

```bash
agent serve
# or
make serve
```

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions |
| `POST` | `/v1/agent/chat` | Multi-agent team chat |
| `POST` | `/v1/agent/review` | Code review with review team |
| `POST` | `/v1/agent/research` | Research with research team |
| `GET` | `/v1/providers` | List available providers |
| `GET` | `/v1/teams` | List available teams |
| `GET` | `/v1/agents` | List available agents |
| `GET` | `/health` | Health check |

#### Examples

```bash
# OpenAI-compatible chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# Multi-agent team chat
curl -X POST http://localhost:8000/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a FastAPI CRUD app",
    "team": "productivity",
    "provider": "openai"
  }'

# Code review
curl -X POST http://localhost:8000/v1/agent/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b): return a + b",
    "language": "python"
  }'

# Research
curl -X POST http://localhost:8000/v1/agent/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "LLM fine-tuning best practices",
    "depth": "thorough"
  }'
```

### MCP Server

The MCP (Model Context Protocol) server exposes agent capabilities to compatible IDEs:

```bash
agent mcp-serve
```

**Exposed tools:**
- `agent_chat` — Send messages to agent teams
- `agent_code_review` — Review code with the review team
- `agent_research` — Research topics with the research team

---

## IDE Integration

### Trae.ai

The project includes pre-configured Trae IDE integration in `.trae/`:

1. **Open the project in Trae** — MCP servers auto-configure from `.trae/mcp_settings.json`
2. **Use custom agents** — Four pre-built agents appear in the Trae agent panel:
   - **🎯 Smart Orchestrator** — Auto-routes to the right team
   - **🚀 Full Productivity Team** — Full 8-agent team for complex tasks
   - **🔍 Code Reviewer** — Focused code review with the 3-agent review team
   - **📚 Research Agent** — Research with web access and GitHub integration

To auto-configure Trae settings:

```bash
python scripts/setup_trae.py
# or
make setup-trae
```

### Claude Code

The project includes a `CLAUDE.md` file that automatically provides Claude Code with project context. Just open the project and Claude Code will understand the architecture, commands, and patterns.

### Cursor / VS Code

The MCP configuration in `.vscode/mcp.json` (created by `setup_trae.py`) works with any VS Code-compatible editor. Run:

```bash
python scripts/setup_trae.py
```

---

## Teams

| Team | Agents | Best For |
|---|---|---|
| **productivity** | All 8 agents | Complex multi-step tasks, full project work |
| **code_review** | Coder, Reviewer, Architect | Code review, bug finding, refactoring |
| **research** | Researcher, Writer, Architect | Topic research, documentation, analysis |
| **quick** | Orchestrator only | Simple questions, quick lookups |

---

## Agents

| Agent | Role | Specialization |
|---|---|---|
| **Orchestrator** | Team lead | Routes tasks, coordinates agents, manages workflow |
| **Coder** | Developer | Writes code, implements features, fixes bugs |
| **Reviewer** | Quality | Reviews code for bugs, security, performance, style |
| **Researcher** | Analyst | Researches topics, finds solutions, gathers data |
| **Architect** | Designer | System design, architecture decisions, patterns |
| **Tester** | QA | Writes tests, validates behavior, edge cases |
| **Writer** | Docs | Documentation, README files, API docs, tutorials |
| **DevOps** | Ops | CI/CD, Docker, deployment, infrastructure |

---

## Providers

All providers use a unified interface. The system auto-detects which providers have valid API keys.

| Provider | Models | Protocol | Notes |
|---|---|---|---|
| **OpenAI** | GPT-4o, GPT-4o-mini, o1, o3 | OpenAI native | Default provider |
| **Together.ai** | Llama 3.1, Mixtral, Qwen | OpenAI-compatible | Fast inference, open models |
| **OpenRouter** | Claude, GPT-4, Llama, 200+ | OpenAI-compatible | Model aggregator, best variety |
| **Google Gemini** | Gemini 2.0 Flash, Pro | Google AI SDK | Native integration |
| **Kimi (Moonshot)** | Kimi K2.5 | OpenAI-compatible | Long context (200K tokens) |
| **Mistral** | Mistral Large, Codestral | OpenAI-compatible | Strong code + multilingual |

### Provider Architecture

```
Request → Provider Factory → Model Client → LLM API
                                ↓
              OpenAIChatCompletionClient (most providers)
              GeminiChatCompletionClient (Google only)
```

All OpenAI-compatible providers use `OpenAIChatCompletionClient` with a custom `base_url` and `model_info` dict. Google Gemini uses the native `GeminiChatCompletionClient`.

---

## MCP Tools Reference

When connected via MCP (IDE or `agent mcp-serve`), these tools are available:

| Tool | Parameters | Description |
|---|---|---|
| `agent_chat` | `message`, `team?`, `provider?` | Chat with an agent team |
| `agent_code_review` | `code`, `language?`, `focus?` | Review code with the review team |
| `agent_research` | `topic`, `depth?` | Research a topic (quick / thorough) |
| `browse` | `url`, `wait_for?` | Navigate to URL and extract content |
| `screenshot` | `url`, `full_page?` | Capture screenshot as base64 PNG |
| `read_file` | `path` | Read file contents from filesystem |
| `list_directory` | `path?` | List files in directory |
| `list_providers` | — | List available LLM providers |
| `list_teams` | — | List available agent teams |

### Web Browser Control

The MCP server includes Playwright-based web browsing for JS-heavy pages:

```bash
# Requires Playwright
pip install playwright
playwright install chromium
```

### Filesystem Access

The MCP server provides local filesystem access for reading files and listing directories. All paths are resolved relative to the user's home directory.

---

## Docker

### Build and Run

```bash
# Build image
docker build -t autogen-agent .

# Run API server
docker run -p 8000:8000 --env-file .env autogen-agent

# Or use docker-compose (API + MCP server)
docker-compose up -d
```

### Services

| Service | Port | Description |
|---|---|---|
| `agent-api` | 8000 | FastAPI HTTP API server |
| `agent-mcp` | 3000 | MCP server (SSE transport) |

Both services include health checks and auto-restart.

---

## Development

### Setup

```bash
pip install -e ".[dev]"
```

### Commands

```bash
make test          # Run tests
make lint          # Check linting
make format        # Auto-format code
make serve         # Start API server with hot-reload
make mcp           # Start MCP server
make clean         # Remove build artifacts
```

### Running Tests

```bash
pytest -v                      # All tests
pytest tests/test_providers.py # Provider tests only
pytest -k "test_chat"          # Filter by name
pytest --cov=autogen_api_agent # With coverage
```

### Project Structure

```
src/autogen_api_agent/
├── __init__.py          # Package root, version
├── config.py            # Settings via pydantic-settings
├── server.py            # FastAPI HTTP API
├── cli.py               # Typer CLI
├── mcp_server.py        # MCP server for IDE integration
├── providers/
│   ├── __init__.py
│   ├── factory.py       # ModelClientFactory — unified provider interface
│   ├── openai.py        # OpenAI client
│   ├── together.py      # Together.ai client
│   ├── openrouter.py    # OpenRouter client
│   ├── google.py        # Google Gemini client
│   ├── kimi.py          # Kimi/Moonshot client
│   └── mistral.py       # Mistral client
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py  # Task routing and coordination
│   ├── coder.py         # Code generation and editing
│   ├── reviewer.py      # Code review and quality
│   ├── researcher.py    # Research and analysis
│   ├── architect.py     # System design
│   ├── tester.py        # Test generation
│   ├── writer.py        # Documentation
│   └── devops.py        # CI/CD and infrastructure
├── teams/
│   ├── __init__.py
│   ├── registry.py      # Team factory and registry
│   ├── productivity.py  # Full 8-agent team
│   ├── code_review.py   # 3-agent review team
│   ├── research.py      # 3-agent research team
│   └── quick.py         # Single-agent quick team
└── tools/
    ├── __init__.py
    ├── file_ops.py      # File read/write/search
    ├── web_search.py    # Web search and fetch
    ├── github.py        # GitHub API operations
    ├── shell.py         # Shell command execution
    └── code_analysis.py # AST parsing, linting
```

### Adding a New Provider

1. Create `src/autogen_api_agent/providers/newprovider.py`
2. Implement the client using `OpenAIChatCompletionClient` with custom `base_url`
3. Add config fields to `src/autogen_api_agent/config.py`
4. Register in `src/autogen_api_agent/providers/factory.py`
5. Add env vars to `configs/.env.example`
6. Add tests in `tests/test_providers.py`

### Adding a New Agent

1. Create `src/autogen_api_agent/agents/newagent.py` with a factory function
2. Define the agent's system prompt and tool assignments
3. Register in relevant team compositions under `teams/`
4. Add tests in `tests/test_agents.py`

### Adding a New Tool

1. Create an async function in `src/autogen_api_agent/tools/`
2. Add a clear docstring (AutoGen uses it as the tool description)
3. Assign to relevant agents in their factory functions
4. Add to MCP server if it should be IDE-accessible

---

## CI/CD

GitHub Actions runs on every push and PR to `main`:

1. **Lint** — `ruff check` and `ruff format --check`
2. **Test** — `pytest` across Python 3.10, 3.11, 3.12
3. **Docker** — Verify the image builds successfully

---

## License

[MIT](LICENSE) — see [LICENSE](LICENSE) for details.
---

## Sovereign Intelligence OS (Termux + Fold 7)

A companion subsystem lives under [`sovereign-intelligence-os/`](sovereign-intelligence-os/README.md).
It bundles a Termux-hosted FastAPI orchestrator, ChromaDB memory, MCP bridges (GitHub + Google
Drive + filesystem), a Kivy APK thin client, and Tasker gesture integration for Android.

Quick start on a Termux device:

```bash
bash sovereign-intelligence-os/install-termux-phase1.sh
bash sovereign-intelligence-os/scripts/launch-os.sh
bash sovereign-intelligence-os/scripts/post-install.sh
```

See the subsystem's [README](sovereign-intelligence-os/README.md) and
[security notes](sovereign-intelligence-os/docs/security-considerations.md) before running.
