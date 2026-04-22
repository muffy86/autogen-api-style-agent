# Sovereign Intelligence OS

Private Termux-hosted companion subsystem for Galaxy Fold 7 class Android devices. It exposes a local FastAPI orchestrator, persistent ChromaDB memory, declarative MCP server configuration, an optional OpenCV screen-awareness bridge, and a Kivy APK thin client.

Status: self-contained under `sovereign-intelligence-os/`. It does not change the root project's Python dependency graph.

Quick start — Termux / on-device (recommended on Galaxy Fold 7):

```bash
cd sovereign-intelligence-os
bash install-termux-phase1.sh
cp .env.example .env  # edit and set SOVEREIGN_TRIGGER_TOKEN
bash scripts/launch-os.sh
bash scripts/post-install.sh
```

Quick start — desktop / dev:

```bash
cd sovereign-intelligence-os
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # edit and set SOVEREIGN_TRIGGER_TOKEN
pytest -q
```

Architecture: Kivy APK or Tasker sends HTTP requests into a local FastAPI orchestrator running in Termux/proot; the orchestrator routes prompts via LiteLLM, stores recall in ChromaDB, and exposes declarative MCP server inventory for GitHub, Google Drive, and filesystem integrations.

Docs:
- `docs/architecture.md`
- `docs/security-considerations.md`
- `docs/fold7-setup.md`
- `kivy-apk/README.md`
- `tasker/README.md`

Environment highlights:
- `SOVEREIGN_MEMORY_PATH` defaults to `~/.sovereign-os/memory`
- `SOVEREIGN_IDENTITY_PATH` defaults to `~/.sovereign-os/identity.md`
- `SOVEREIGN_TRIGGER_TOKEN` protects mutating endpoints
- `SOVEREIGN_MCP_SERVERS_CONFIG` points at `./configs/mcp_servers.json`

Component status:

| Component | Status | Notes |
|---|---|---|
| FastAPI orchestrator | Real | `orchestrator/main.py` serves `/health`, `/trigger`, and memory endpoints. |
| ChromaDB memory | Real | Persistent path is configurable by `SOVEREIGN_MEMORY_PATH`. |
| LiteLLM router | Real | Uses async `litellm.acompletion` only. |
| MCP bridge | Real | Reads declared servers from JSON config; does not spawn them from Python. |
| GitHub / Google Drive / filesystem MCP configs | Real | Declared in `configs/mcp_servers.json`; launcher scripts can start them externally. |
| OpenClaw integration | Declarative only | Referenced operationally via external tooling; not imported into Python. |
| OpenCV screen-awareness bridge | Real, optional | `orchestrator/cv_bridge.py` works when installed with `[cv]`. |
| Browser bridge | Real, optional | `orchestrator/browser_bridge.js` requires system Chromium and Node `playwright-core` (`npm i -g playwright-core`). |
| Kivy APK client | Real | Thin HTTP client only; heavy inference dependencies stay in Termux. |
| WebSocket streaming | Phase 2 — not yet implemented | HTTP request/response only today. |
| Voice pipeline | Phase 2 — not yet implemented | Tasker and clipboard triggers only today. |

Notes:
- The official Google Drive MCP package is `@modelcontextprotocol/server-gdrive`.
- OpenClaw is pinned to `openclaw@>=2026.3.22` in the Termux bootstrap because compromised releases shipped in Feb–Mar 2026.
- No Python module hardcodes Android `/sdcard/...` paths.
