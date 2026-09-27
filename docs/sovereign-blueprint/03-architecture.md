# Final architecture

See also: [component survey](./02-component-survey.md), [repo structure](./04-repo-structure.md), [security](./07-security-threat-model.md).

## 1. Selected architecture

### Core decisions

| Concern | Decision | Why |
| --- | --- | --- |
| Browser shell | Electron app wrapping the existing SvelteKit UI | Fastest path to a sovereign custom browser with deep desktop integration |
| Agent substrate | Keep `src/autogen_api_agent/` as the core API + MCP + team system | Already present and aligned with AutoGen 0.7.5 |
| Orchestration | LangGraph wraps AutoGen teams | Durable state and explicit graph edges around existing team collaboration |
| Browser automation | Playwright MCP + browser-use + Stagehand | Mix of deterministic control and higher-level browser-use reasoning |
| Model routing | LiteLLM proxy | Unified routing across free cloud, local, and experimental decentralized providers |
| Memory | Mem0 for extracted memory, short-term task state in LangGraph/Temporal | Practical separation of episodic and durable memory |
| Background runtime | Temporal | Retries, schedules, resumability, observability hooks |
| Tool plane | MCP first, Composio only for high-friction SaaS auth | Keeps sovereignty high and lock-in low |
| Security | Infisical + Authentik + Tailscale + tiered sandboxes | Self-hostable, operator-friendly zero-trust baseline |

### Selected upstreams

| project | repo | license | stars (approx) | last_commit | selected role |
| --- | --- | --- | ---: | --- | --- |
| Electron | <https://github.com/electron/electron> | MIT | 121.1k | 2026-04-30 | browser shell |
| AutoGen | <https://github.com/microsoft/autogen> | CC-BY-4.0 | 57.6k | 2026-04-06 | existing agent substrate |
| LangGraph | <https://github.com/langchain-ai/langgraph> | MIT | 30.9k | 2026-04-30 | durable orchestration |
| LiteLLM | <https://github.com/BerriAI/litellm> | NOASSERTION | 45.3k | 2026-04-30 | model router |
| Mem0 | <https://github.com/mem0ai/mem0> | Apache-2.0 | 54.5k | 2026-04-29 | long-term memory |
| Temporal | <https://github.com/temporalio/temporal> | MIT | 20.0k | 2026-04-30 | 24/7 workflow runtime |
| Langfuse | <https://github.com/langfuse/langfuse> | NOASSERTION | 26.4k | 2026-04-30 | observability/evals |
| Playwright MCP | <https://github.com/microsoft/playwright-mcp> | Apache-2.0 | 31.8k | 2026-04-30 | browser control surface |

## 2. System topology

```mermaid
flowchart TB
    U[User] --> BS[Electron Browser Shell]
    BS --> UI[SvelteKit Renderer<br/>Sidebar / Canvas / Tray / Memory]
    BS --> IPC[Local IPC + Policy Broker]

    IPC --> HUB[Existing Agent Hub<br/>FastAPI + AutoGen + MCP<br/>src/autogen_api_agent]
    HUB --> LG[LangGraph Durable Graph]
    LG --> AT[AutoGen Teams<br/>planner / researcher / coder / reviewer]
    LG --> TM[Temporal Workflows]
    LG --> MEM[Mem0 + session state]

    HUB --> TOOLS[Tool Gateway]
    TOOLS --> MCP[MCP local/remote servers]
    TOOLS --> COMP[Composio adapters]
    TOOLS --> BROWSERS[Browser runtimes<br/>Playwright MCP / browser-use / Stagehand / steel]
    TOOLS --> DESK[Desktop bridges<br/>AppleScript / AT-SPI / pywinauto]
    TOOLS --> FS[Filesystem bridge<br/>MCP FS + watchers + optional FUSE]

    HUB --> ROUTER[LiteLLM Proxy]
    ROUTER --> FREE[Free cloud providers<br/>Google / OpenRouter / Groq / Cerebras / Cloudflare / HF / Mistral]
    ROUTER --> LOCAL[Local inference<br/>Ollama / llama.cpp / vLLM]
    ROUTER --> DECNET[Decentralized R&D<br/>Akash / Hyperspace / Bittensor]

    HUB --> OBS[Observability]
    OBS --> LF[Langfuse]
    OBS --> OTEL[OpenTelemetry Collector]
    OBS --> LGF[Loki + Grafana]

    IPC --> SEC[Security Control Plane]
    SEC --> AUTH[Authentik]
    SEC --> SECRETS[Infisical + age/sops]
    SEC --> NET[Tailscale / optional Cloudflare Tunnel]
    SEC --> SBX[Rootless Docker / gVisor / Firecracker]
```

## 3. Data flow for a multi-agent web task

Example task: "Research three vendors, compare pricing, draft a summary, and file a decision memo."

```mermaid
sequenceDiagram
    participant User
    participant Shell as Browser Shell
    participant Hub as Agent Hub
    participant Graph as LangGraph
    participant Router as LiteLLM
    participant Browser as Browser Runtime
    participant Tools as MCP/Composio/Desktop
    participant Memory as Mem0
    participant Trace as Langfuse

    User->>Shell: Submit task
    Shell->>Hub: Create task + context bundle
    Hub->>Graph: Start durable workflow
    Graph->>Trace: Open trace/span
    Graph->>Router: Ask planner model for decomposition
    Router-->>Graph: Plan
    Graph->>Browser: Open trusted vendor tabs and extract data
    Browser-->>Graph: DOM/screenshots/extractions
    Graph->>Tools: Query files, CRM, calendar, or email if approved
    Tools-->>Graph: Tool results
    Graph->>Memory: Read prior vendor memories
    Memory-->>Graph: Relevant long-term context
    Graph->>Router: Draft summary / decide next steps
    Router-->>Graph: Structured output
    Graph->>Memory: Store distilled lessons
    Graph->>Trace: Close trace + scores
    Hub-->>Shell: Stream artifacts, citations, next actions
    Shell-->>User: Inspectable result + background task status
```

## 4. Browser shell internals

```mermaid
flowchart LR
    subgraph ElectronMain[Electron Main Process]
        SessionMgr[Profile / session manager]
        TabMgr[Tab manager]
        Perm[Permission + approval broker]
        Ext[Optional extension loader]
        Native[Native OS bridge]
        Tray[Background task tray]
    end

    subgraph Renderer[SvelteKit Renderer]
        Sidebar[Persistent agent sidebar]
        Canvas[Multi-agent canvas]
        Tabs[Tab strip + tab inspector]
        MemoryPane[Editable memory pane]
        Voice[Voice I/O controls]
        TracePane[Task trace / approvals / audit]
    end

    subgraph Headless[Detached Worker Processes]
        BW[Browser-use workers]
        SH[Stagehand workers]
        PMCP[Playwright MCP server]
        Desk[Desktop-control workers]
    end

    SessionMgr --> TabMgr
    TabMgr --> Renderer
    Perm --> Renderer
    Native --> Renderer
    Tray --> Renderer
    Renderer --> BW
    Renderer --> SH
    Renderer --> PMCP
    Renderer --> Desk
    Perm --> BW
    Perm --> Desk
```

### Browser UX contract

The shell should expose five always-visible control surfaces:

1. **persistent sidebar**: one thread per agent or workflow
2. **canvas**: shared document/code/table/diagram space across agents
3. **tab orchestration**: visible mapping from agents to tabs, profiles, permissions, and extraction state
4. **background tray**: pause/resume/retry/inspect long-running workflows
5. **memory pane**: short-term context plus editable long-term memory entries

Voice mode is additive: `whisper` for STT and `piper` for TTS, with local-only mode as the default for sensitive work.

## 5. Model-routing layer

```mermaid
flowchart TD
    Req[Prompt / tool task] --> Tag[Sensitivity tagger]
    Tag -->|public or low sensitivity| FreePool[Free cloud pool]
    Tag -->|restricted / local-only| LocalPool[Local inference pool]

    FreePool --> Fast[Fast alias<br/>Gemini Flash]
    Fast --> Fallback1[Groq fast]
    Fallback1 --> Fallback2[Cerebras fast]
    Fallback2 --> Fallback3[Cloudflare / HF / OpenRouter free]
    Fallback3 --> LocalPool

    LocalPool --> Ollama[Ollama small/medium]
    Ollama --> LlamaCpp[llama.cpp fallback]
    Ollama --> VLLM[vLLM cluster if available]

    Req --> Budget[Quota + budget guard]
    Budget --> Retry[Backoff / cooldown]
    Retry --> Trace[Langfuse + metrics]
```

### Routing policy

- default to free cloud models for public-web summarization
- prefer Gemini Flash for low-cost fast reasoning while quota remains
- use Groq/Cerebras as overflow for fast text/code generation
- use OpenRouter free pool only as an opportunistic pool, not a stable primary
- hard-switch to local models for restricted prompts, local files, or secrets-adjacent actions
- optional decentralized inference only behind an explicit experiment flag

## 6. Zero-trust security boundaries

```mermaid
flowchart TB
    subgraph Device[User device]
        Shell[Browser shell]
        Hub[Agent hub]
        Router[LiteLLM]
        Mem[Local memory/cache]
    end

    subgraph TrustedLAN[Private network]
        Auth[Authentik]
        Secrets[Infisical]
        Obs[Langfuse / OTel / Loki]
        Temporal[Temporal]
    end

    subgraph Sandboxes[Execution sandboxes]
        Rootless[Rootless Docker]
        GVisor[gVisor containers]
        Firecracker[Firecracker microVMs]
    end

    subgraph External[External services]
        MCPRemote[Remote MCP servers]
        SaaS[Composio-backed SaaS APIs]
        ModelAPIs[Cloud model providers]
    end

    Shell --> Hub
    Hub --> Router
    Hub --> Mem
    Hub --> Rootless
    Hub --> GVisor
    Hub --> Firecracker
    Hub --> Obs
    Hub --> Temporal
    Hub --> Auth
    Hub --> Secrets
    Router --> ModelAPIs
    Hub --> MCPRemote
    Hub --> SaaS
```

### Boundary rules

- UI renderer never gets raw long-lived provider credentials
- tool execution never talks directly to cloud models; it routes through the agent hub + LiteLLM
- desktop and browser automation run outside the renderer in isolated worker processes
- untrusted code execution goes to Firecracker or gVisor, never the main shell process
- all remote admin access rides over Tailscale or equivalent private mesh

## 7. Orchestration topology by responsibility

| Layer | Primary project | Responsibility |
| --- | --- | --- |
| UX shell | Electron + existing SvelteKit UI | tabs, sidebar, canvas, tray, approvals |
| Interactive API | existing `src/autogen_api_agent/server.py` | streaming/chat entry point |
| Tool protocol | existing `src/autogen_api_agent/mcp_server.py` + MCP | local and remote tool access |
| Team collaboration | AutoGen | multi-agent discussion and specialized roles |
| Durable flow | LangGraph | checkpoints, graph transitions, recovery |
| Background jobs | Temporal | schedules, retries, resumability, alerts |
| Memory | Mem0 | extracted and retrievable long-term memory |
| Observability | Langfuse + OTel + Loki | traces, metrics, audit, evals |
| Model routing | LiteLLM | provider abstraction, fallbacks, budgets |
| Security control plane | Authentik + Infisical + Tailscale + sandboxing | SSO, secrets, network, isolation |

## 8. Why this architecture is executable

- It reuses the current repo for API, MCP, and AutoGen teams.
- Each added concern maps to an existing upstream project instead of a custom subsystem.
- UI and headless workers are separated early, which keeps 24/7 automation from destabilizing the visible browser.
- The model router, tool gateway, and sensitivity tagger make "free-first but safe" practical.
- Security boundaries are explicit enough to test and phase independently.
