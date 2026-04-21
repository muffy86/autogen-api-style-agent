# Architecture

Sovereign Intelligence OS keeps heavy orchestration inside Termux/proot and keeps the APK lightweight. The Android client layer only handles operator interaction and local HTTP dispatch.

```mermaid
flowchart LR
  subgraph Fold7["Galaxy Fold 7 (Android)"]
    Kivy["Kivy APK (thin client)"]
    Tasker["Tasker + Termux:Tasker"]
    subgraph Termux["Termux + proot Ubuntu 24.04"]
      Orch["FastAPI orchestrator"]
      LL["LiteLLM router"]
      CDB["ChromaDB persistent memory"]
      Ollama["Ollama (optional local)"]
      MCP1["MCP server: github"]
      MCP2["MCP server: gdrive"]
      MCP3["MCP server: filesystem"]
    end
  end
  Cloud["Cloud LLM via OpenRouter/etc"]
  Kivy -->|POST /trigger| Orch
  Tasker -->|curl POST| Orch
  Orch --> LL
  LL --> Ollama
  LL --> Cloud
  Orch --> CDB
  Orch -.->|stdio MCP| MCP1
  Orch -.->|stdio MCP| MCP2
  Orch -.->|stdio MCP| MCP3
```

Design notes:
- Termux is the trust boundary. The orchestrator binds to `127.0.0.1` by default and should stay local.
- The Python MCP bridge is intentionally declarative. It lists configured servers but does not spawn or supervise them.
- ChromaDB persists recall under `SOVEREIGN_MEMORY_PATH`, defaulting to `~/.sovereign-os/memory`.
- The optional OpenCV bridge uses `termux-screencap` when available.
- The Kivy APK is intentionally thin because `chromadb`, LiteLLM, and OpenCV are poor fits for python-for-android packaging.

Fold 7 considerations:
- Use multi-window mode for a side-by-side cockpit: Kivy UI on one pane, Termux logs or browser on the other.
- Prefer HTTP-triggered workflows over long-running UI automation inside the APK.
- Keep filesystem work rooted in `~/sovereign-workspace` so Termux, MCP filesystem access, and proot tooling share a predictable workspace.
