# Proposed repo structure

See also: [architecture](./03-architecture.md), [roadmap](./05-roadmap.md).

## 1. Strategy

Keep this repository as the primary monorepo. Do not eject `src/autogen_api_agent/`.
Instead, graft new services and apps around it in stages.

## 2. Minimal-change path vs. target end-state

### Minimal-change path (Phase 1-2)

- keep the existing Python package in place
- keep the current SvelteKit app at repo root
- add an Electron wrapper around the existing web UI
- add Docker services for LiteLLM, Langfuse, Mem0, Temporal
- add `packages/` only when shared TypeScript code appears

### Target end-state (after Phase 2)

```text
.
├── apps/
│   ├── browser-shell/
│   │   ├── main/
│   │   ├── preload/
│   │   └── renderer/
│   └── ops-console/
├── docs/
│   └── sovereign-blueprint/
├── packages/
│   ├── agent-ui/
│   ├── browser-runtime-adapters/
│   ├── desktop-bridge/
│   ├── filesystem-bridge/
│   ├── policy-gateway/
│   └── shared-types/
├── services/
│   ├── agent-hub/
│   ├── litellm/
│   ├── langfuse/
│   ├── mem0/
│   ├── temporal/
│   └── otel/
├── src/
│   ├── autogen_api_agent/
│   └── routes/
├── tests/
└── vendor/
```

## 3. Directory-by-directory plan

| Path | Purpose | Upstream project or source | Fork / vendor posture |
| --- | --- | --- | --- |
| `src/autogen_api_agent/` | Existing agent API, MCP server, AutoGen teams, provider factory | Current repo + AutoGen | Keep and extend |
| `src/routes/` | Existing SvelteKit UI; initial renderer foundation | Current repo | Keep through Phase 2; gradually migrate shared UI into `packages/agent-ui/` |
| `apps/browser-shell/main/` | Electron main-process code: windows, sessions, permissions, tray | Electron | New app code using upstream Electron APIs |
| `apps/browser-shell/preload/` | Safe IPC bridge from renderer to native/browser services | Electron | New app code |
| `apps/browser-shell/renderer/` | Browser shell UI if/when root SvelteKit app is moved | Existing SvelteKit UI + assistant-ui | Migrate from root only after shell stabilizes |
| `apps/ops-console/` | Admin/tracing/quota console | SvelteKit + Grafana/Langfuse embeds | New app code |
| `packages/agent-ui/` | Sidebar, canvas, memory pane, task tray, approval components | assistant-ui as pattern/input | Use, not fork unless upstream divergence is large |
| `packages/browser-runtime-adapters/` | Wrappers for Playwright MCP, browser-use, Stagehand, steel | microsoft/playwright-mcp, browser-use, Stagehand, steel-browser | Use as adapters; avoid vendoring unless patching is required |
| `packages/desktop-bridge/` | OS-specific bridges for AppleScript, AT-SPI, pywinauto | OS-native APIs + pywinauto | New glue code |
| `packages/filesystem-bridge/` | MCP filesystem hardening, watchers, optional shared-workspace mount | MCP servers, chokidar, optional rclone | Use existing servers first |
| `packages/policy-gateway/` | Sensitivity tagging, prompt/tool policy, rate limits, approvals | Presidio + custom policy rules | New policy layer |
| `packages/shared-types/` | Cross-process DTOs for tasks, agents, tabs, approvals, traces | Internal | New shared package |
| `services/agent-hub/` | Packaging wrapper around `src/autogen_api_agent/` for compose/deploy | Current repo | Re-export existing substrate |
| `services/litellm/` | Router config, callbacks, budgets, provider health | LiteLLM | Use upstream image, keep repo-local config only |
| `services/langfuse/` | Compose/helm values, bootstrap, dashboards | Langfuse | Use upstream deploy artifacts |
| `services/mem0/` | Memory service config and persistence adapters | Mem0 | Use upstream package/service |
| `services/temporal/` | Workflow definitions and worker bindings | Temporal | Use upstream server, own workflow code |
| `services/otel/` | Collector config and exporters | OpenTelemetry Collector | Use upstream image, local config |
| `vendor/electron-chrome-extensions/` | Optional extension compatibility shim if Electron API gaps block required integrations | ramboxapp/electron-chrome-extensions | Vendor only if needed; keep isolated |

## 4. How the new structure grafts onto the current tree

### Current validated substrate

The following existing files remain the anchors:

- [`../../src/autogen_api_agent/server.py`](../../src/autogen_api_agent/server.py)
- [`../../src/autogen_api_agent/mcp_server.py`](../../src/autogen_api_agent/mcp_server.py)
- [`../../docker-compose.yml`](../../docker-compose.yml)
- [`../../src/routes/+page.svelte`](../../src/routes/+page.svelte)

### Incremental graft plan

1. **Phase 1**: add `services/litellm`, `services/langfuse`, `services/mem0`, `services/otel`, `services/temporal`; keep UI untouched.
2. **Phase 2**: add `apps/browser-shell/` and point it at the existing SvelteKit app in dev/build mode.
3. **Phase 2b**: extract reusable sidebar/canvas components from `src/routes/` into `packages/agent-ui/`.
4. **Phase 3-4**: add `packages/desktop-bridge/`, `packages/filesystem-bridge/`, and editor adapters.
5. **Phase 5+**: add `packages/policy-gateway/` and hard isolation/runtime controls.

## 5. Example ownership boundaries

| Boundary | Owned here | Outsourced to upstream |
| --- | --- | --- |
| Team prompts and orchestration | yes | no |
| Browser shell UX | yes | no |
| Browser engine | no | Electron/Chromium upstream |
| Durable workflow engine | workflow code only | Temporal server |
| Model routing | config/callbacks only | LiteLLM core |
| Memory extraction | integration only | Mem0 core |
| Observability backend | config/deploy only | Langfuse + OTel |
| SaaS auth toolkit | adapter only | Composio |

## 6. Mono-repo vs. multi-repo decision

### Recommendation: stay mono-repo until after Phase 4

Reasons:

- the current repo already mixes Python API, MCP, and SvelteKit UI
- the first shipping increments require tight coupling between browser shell, agent hub, and policy code
- splitting repos early would create CI/release overhead without reducing architecture risk

### Only split later if both are true

- the browser shell becomes release-cadenced independently of the agent hub
- a separate desktop-app team or distribution model appears

## 7. Vendoring rules

Vendor only when one of the following is true:

- upstream is tiny and effectively abandoned but still strategically useful
- a patch is required for Electron-specific integration and upstream will not accept it quickly
- the component is used in a tightly scoped compatibility layer under `vendor/`

Otherwise prefer direct dependency pins plus local adapters.
