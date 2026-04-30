# Phased build roadmap

See also: [repo structure](./04-repo-structure.md), [free-model config](./06-free-models-config.md), [security](./07-security-threat-model.md).

Sizing legend: **S** = single focused task, **M** = 1-2 days of implementation, **L** = multi-day but still a single build task if tightly scoped.

## Phase 0 (P0): Cleanup

Goal: stabilize the current repo before new subsystems land.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P0.1 open PR triage | audit open/stale PRs, close superseded work, note merge candidates | none | S | none |
| P0.2 dependency lock audit | freeze Python/Node dependency versions, re-resolve lockfiles only if required | none | S | none |
| P0.3 CI lint repair | make `ruff`, tests, and frontend checks green on main branch | none | M | P0.2 |
| P0.4 container reproducibility pass | verify `docker-compose.yml` images, healthchecks, and `.env.example` are coherent | none | S | P0.2 |

## Phase 1: Sovereign Agent Hub

Goal: upgrade the existing repo into a durable, observable, free-first control plane.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P1.1 add LiteLLM proxy service | compose service, env wiring, base config, health endpoint | BerriAI/litellm | M | P0 |
| P1.2 add free-provider alias set | configure Google, Groq, Cerebras, Cloudflare, OpenRouter, HF, Mistral, Ollama aliases | none | M | P1.1 |
| P1.3 wrap AutoGen teams in LangGraph | create graph entrypoints around current team flows | langchain-ai/langgraph | L | P0 |
| P1.4 add Langfuse tracing | emit traces from API, tool calls, and router callbacks | langfuse/langfuse, open-telemetry/opentelemetry-collector | M | P1.1 |
| P1.5 add Mem0 memory service | extracted memory on task completion and retrieval hooks on task start | mem0ai/mem0 | M | P1.3 |
| P1.6 add MCP registry + local tool catalog | local metadata service for approved MCP servers and policies | modelcontextprotocol/registry, modelcontextprotocol/servers | M | P0 |
| P1.7 add selective Composio adapter | OAuth-heavy SaaS tool path with explicit opt-in and policy wrapping | ComposioHQ/composio | M | P1.6 |
| P1.8 expand compose stack | compose profiles for agent hub, router, tracing, memory, and tool gateway | none | S | P1.1, P1.4, P1.5 |

## Phase 2: Custom agentic browser shell

Goal: ship the sovereign browser UX.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P2.1 bootstrap Electron shell | main/preload processes, point at existing SvelteKit UI | electron/electron | M | P1 |
| P2.2 add persistent profile/session model | named profiles, tab persistence, per-agent session partitions | electron/electron | M | P2.1 |
| P2.3 build persistent agent sidebar | threads, agent list, approvals, live status | assistant-ui/assistant-ui | M | P2.1 |
| P2.4 add tab orchestration broker | open/close/inspect/share tab context, agent-to-tab mapping | microsoft/playwright-mcp | L | P2.2 |
| P2.5 build multi-agent canvas | shared artifact workspace for docs/code/tables/diagrams | assistant-ui/assistant-ui, PySpur-Dev/pyspur | L | P2.3 |
| P2.6 add background task tray | resume/pause/retry/inspect Temporal jobs in the browser shell | temporalio/temporal | M | P1.3 |
| P2.7 add optional extension bridge | load unpacked extensions or shim required APIs only if needed | ramboxapp/electron-chrome-extensions | M | P2.2 |

## Phase 3: IDE bridges

Goal: make the agent hub reachable from editors without bespoke prompts.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P3.1 ship Zed MCP config pack | documented settings + approved server templates | zed-industries/zed, zed-industries/extensions | S | P1.6 |
| P3.2 build Zed extension | package sovereign-agent MCP server and prompts inside Zed | zed-industries/extensions | M | P3.1 |
| P3.3 add opencode bridge | native config and tool wiring for opencode | anomalyco/opencode | S | P1.6 |
| P3.4 polish VS Code / Continue / Cline configs | tested presets for MCP, remote auth, and traces | microsoft/vscode, continuedev/continue, cline/cline | M | P1.6 |
| P3.5 add coding-agent wrappers | standard entrypoints for Aider and Plandex under the hub | Aider-AI/aider, plandex-ai/plandex | M | P1.3 |

## Phase 4: Desktop and filesystem integration

Goal: make agents effective beyond the browser.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P4.1 harden MCP filesystem access | allowlists, audit logs, write confirmation, path sandboxing | modelcontextprotocol/servers | M | P1.6 |
| P4.2 add file watch/reindex pipeline | watcher-driven memory/index updates for shared workspaces | paulmillr/chokidar | S | P4.1 |
| P4.3 ship macOS desktop bridge | AppleScript / `osascript` wrapper with policy approval flow | none | M | P2 |
| P4.4 ship Linux desktop bridge | AT-SPI / D-Bus semantic control adapter | none | M | P2 |
| P4.5 ship Windows desktop bridge | pywinauto first, AutoHotkey fallback | pywinauto/pywinauto, AutoHotkey/AutoHotkey | M | P2 |
| P4.6 prototype shared-workspace mount | optional mounted agent workspace with clear ownership semantics | rclone/rclone | M | P4.1 |

## Phase 5: Zero-trust hardening

Goal: make the platform safe enough for real local and team usage.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P5.1 secrets control plane | Infisical deployment, CLI bootstrap, local dev flow | Infisical/infisical, FiloSottile/age, getsops/sops | M | P1 |
| P5.2 SSO and MFA | Authentik deployment and role mapping to browser/admin surfaces | goauthentik/authentik | M | P1 |
| P5.3 network hardening | Tailscale admin path and optional Cloudflare Tunnel/Pangolin ingress patterns | tailscale/tailscale, cloudflare/cloudflared, fosrl/pangolin | M | P5.2 |
| P5.4 add sensitivity tagger | classify prompts/files and gate cloud routing | microsoft/presidio | M | P1.2 |
| P5.5 tool policy gateway | allow/deny/rate-limit tool calls and approvals | none | L | P5.4 |
| P5.6 tiered sandbox execution | rootless Docker default, gVisor medium risk, Firecracker high risk | google/gvisor, firecracker-microvm/firecracker, moby/moby | L | P5.5 |
| P5.7 audit pipeline | send prompt/tool/file events to Langfuse + Loki/Grafana | grafana/loki, grafana/grafana, langfuse/langfuse | M | P1.4 |

## Phase 6: 24/7 workflow runtime

Goal: make long-running workflows first-class.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P6.1 Temporal workflow definitions | recurring research, inbox triage, watch-and-alert flows | temporalio/temporal | M | P1.3 |
| P6.2 scheduler UI | browser tray screens for scheduled jobs, SLAs, retries, pause/resume | temporalio/temporal | M | P2.6 |
| P6.3 alerting and escalation | email/webhook/desktop alerts for failed workflows | none | S | P6.1 |
| P6.4 artifact retention policy | control lifetime of outputs, screenshots, downloads, and traces | none | M | P5.7 |
| P6.5 human-in-the-loop checkpoints | approval tasks for high-risk side effects | none | M | P5.5, P6.1 |

## Phase 7: Decentralized inference experiments

Goal: test whether decentralized inference adds resilience without degrading UX.

| task title | scope | repos to fork/vendor | est. effort | dependencies |
| --- | --- | --- | --- | --- |
| P7.1 Akash routing spike | add Akash-compatible OpenAI endpoint as an experimental LiteLLM provider | none | S | P1.2 |
| P7.2 Hyperspace experiment | validate latency, availability, and auth surface | hyperspaceai/hyperspace-node | M | P7.1 |
| P7.3 Bittensor subnet spike | test verifiable inference for non-interactive batch tasks only | inference-labs-inc/subnet-2 | M | P7.1 |
| P7.4 production-readiness review | keep, sandbox, or remove decentralized providers based on SLOs | none | S | P7.2, P7.3 |

## Recommended next 3 PRs

1. **PR 1 — LiteLLM + Langfuse + Mem0 + compose expansion**
2. **PR 2 — LangGraph wrapper around current AutoGen teams**
3. **PR 3 — Electron shell bootstrap with persistent sidebar and tab model**
