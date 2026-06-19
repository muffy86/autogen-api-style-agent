# Sovereign Agentic Browser OS

See also: [Comet analysis](./01-perplexity-comet-analysis.md), [component survey](./02-component-survey.md), [architecture](./03-architecture.md), [roadmap](./05-roadmap.md), [security](./07-security-threat-model.md).

## Executive summary

Build the system as an extension of this repo, not as a greenfield rewrite.
The existing substrate already exposes:

- an OpenAI-compatible FastAPI chat API in [`../../src/autogen_api_agent/server.py`](../../src/autogen_api_agent/server.py)
- an MCP server with local filesystem and Playwright browse/screenshot tools in [`../../src/autogen_api_agent/mcp_server.py`](../../src/autogen_api_agent/mcp_server.py)
- containerized `agent-api` and `agent-mcp` services in [`../../docker-compose.yml`](../../docker-compose.yml)
- a SvelteKit desktop-style UI skeleton in [`../../src/routes/+page.svelte`](../../src/routes/+page.svelte)

The blueprint therefore keeps `src/autogen_api_agent/` as the agent-orchestration substrate and adds five layers around it:

1. a sovereign browser shell
2. a durable orchestration/runtime layer
3. a free-first model router with local fallback
4. a zero-trust tool/security perimeter
5. IDE and desktop bridges

## Vision statement

Ship a fully owned alternative to Perplexity Comet / Comet Max for a technical power user or small team:

- multiple agents collaborate continuously, not one chat thread at a time
- the browser is the primary workspace, but not the only one
- agents can work across tabs, files, MCP servers, IDEs, and desktop apps
- cloud models are optional and policy-gated; local models remain a first-class fallback
- every privileged action is attributable, inspectable, rate-limited, and reversible where possible

## Recommended stack snapshot

| Layer | Primary choice | Why this is the default |
| --- | --- | --- |
| Browser shell | [Electron](https://github.com/electron/electron) (MIT, 121.1k★, last commit 2026-04-30) | Fastest path to a custom Chromium shell with strong desktop integration, persistent sessions, IPC, and packaging |
| Agent collaboration core | Existing [`../../src/autogen_api_agent/`](../../src/autogen_api_agent/) + [AutoGen](https://github.com/microsoft/autogen) (CC-BY-4.0, 57.6k★, 2026-04-06) | Already implemented here; do not replace |
| Durable orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) (MIT, 30.9k★, 2026-04-30) around AutoGen | Gives checkpoints, resumability, HITL hooks, and deterministic graph edges AutoGen alone lacks |
| Model routing | [LiteLLM](https://github.com/BerriAI/litellm) (license `NOASSERTION`, 45.3k★, 2026-04-30) | Self-hostable, provider-agnostic, good fallback/budget surface, works with local and remote models |
| Observability | [Langfuse](https://github.com/langfuse/langfuse) (license `NOASSERTION`, 26.4k★, 2026-04-30) + [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) (Apache-2.0, 6.9k★, 2026-04-30) | Best OSS-first tracing/evals path for 24/7 agents |
| Memory | [Mem0](https://github.com/mem0ai/mem0) (Apache-2.0, 54.5k★, 2026-04-29) | Practical extraction/retrieval memory without replacing the whole orchestration stack |
| Durable background jobs | [Temporal](https://github.com/temporalio/temporal) (MIT, 20.0k★, 2026-04-30) | Strongest long-running reliability story for scheduled/retriable agent work |
| Tool fabric | MCP first via [modelcontextprotocol/modelcontextprotocol](https://github.com/modelcontextprotocol/modelcontextprotocol) (`NOASSERTION`, 8.0k★, 2026-04-30) + selective [Composio](https://github.com/ComposioHQ/composio) (MIT, 28.0k★, 2026-04-30) | Keep local/open tools sovereign; use Composio only where managed auth materially lowers cost |
| Secrets | [Infisical](https://github.com/Infisical/infisical) (`NOASSERTION` repo-wide; MIT-expat for OSS core per repo/docs, 26.4k★, 2026-04-30) + [age](https://github.com/FiloSottile/age) (BSD-3-Clause, 22.1k★, 2026-03-20) + [sops](https://github.com/getsops/sops) (MPL-2.0, 21.7k★, 2026-04-27) | Easier self-hosting than Vault for day-1; keep Git-tracked bootstrap secrets encrypted |
| Sandboxing | [Docker rootless](https://github.com/moby/moby) (Apache-2.0, 71.5k★, 2026-04-30) + [gVisor](https://github.com/google/gvisor) (Apache-2.0, 18.2k★, 2026-04-30) + [Firecracker](https://github.com/firecracker-microvm/firecracker) (Apache-2.0, 34.1k★, 2026-04-30) | Tiered isolation by risk: default, medium-risk, and high-risk |
| Identity and network | [Authentik](https://github.com/goauthentik/authentik) (`NOASSERTION`, 21.3k★, 2026-04-30) + [Tailscale](https://github.com/tailscale/tailscale) (BSD-3-Clause, 31.1k★, 2026-04-30) | Good self-host/operator UX for SSO, MFA, private admin access |

## Success criteria

The blueprint is successful if follow-up build tasks can implement the system without new architecture research.
Specifically:

- the browser-shell recommendation is explicit and justified
- every major component choice names a real upstream project and its fork/use posture
- orchestration, routing, memory, observability, security, and UX boundaries are diagrammed
- the free-model plan is concrete enough to be encoded in `litellm_config.yaml`
- phase plans are small enough to execute as independent build tasks
- security/privacy decisions are explicit enough for a production-minded threat review

## Non-goals

This blueprint does **not** attempt to:

- replace the existing AutoGen substrate with a totally different framework
- promise perfect Chrome-extension parity on day 1
- build a new browser engine from scratch
- rely on proprietary hosted control planes as the critical path
- optimize for consumer-polished onboarding before core sovereignty and reliability work

## Design principles

### 1. Reuse before fork; fork before rewrite

Use the current repo as the control plane. Add wrappers around proven projects instead of reproducing them.

### 2. MCP first, SaaS second

Prefer local MCP servers, open registries, and self-hosted tools. Use managed tool catalogs only when auth and maintenance costs justify them.

### 3. Split interactive UI from headless work

The visible browser shell and the 24/7 automation runtime should share memory, policy, and observability, but run in separate processes and profiles.

### 4. Route by sensitivity before routing by price

Public web summarization may use free cloud models. Local files, enterprise documents, secrets, and desktop state should default to local models or explicitly approved remote routes.

### 5. Security boundaries are product features

Per-agent profiles, policy prompts, rate limits, audit logs, and kill switches are core UX, not afterthoughts.

## What this means for the current repo

The repo should evolve into a monorepo-shaped control plane centered on `src/autogen_api_agent/`:

- `src/autogen_api_agent/` remains the API/MCP/orchestrator substrate
- the current SvelteKit UI becomes the renderer foundation for the browser shell
- new services are added alongside it for routing, tracing, memory, and durable workflows
- browser automation runtimes become pluggable adapters instead of being embedded into one agent loop

Detailed layout: [04-repo-structure.md](./04-repo-structure.md)

## Glossary

- **Agent hub**: the existing FastAPI + AutoGen + MCP substrate in this repo.
- **Browser shell**: the desktop app that owns tabs, profiles, sidebar, permissions, and local IPC.
- **Canvas**: the multi-agent shared workspace for composing outputs.
- **Durable workflow**: a task that survives process restarts, user disconnects, and retries.
- **MCP**: Model Context Protocol; standard tool/data interface for local and remote tools.
- **Sensitivity tagger**: a classifier/policy layer that decides whether a prompt/tool/file can leave the machine.
- **Tool gateway**: the policy-enforcing layer in front of MCP, Composio, and desktop actions.
- **Work profile**: a browser/storage partition bound to an agent, workflow, or trust level.

## Reading order

1. [Perplexity Comet analysis](./01-perplexity-comet-analysis.md)
2. [Component survey](./02-component-survey.md)
3. [Final architecture](./03-architecture.md)
4. [Repo structure](./04-repo-structure.md)
5. [Roadmap](./05-roadmap.md)
6. [Free-model config](./06-free-models-config.md)
7. [Security threat model](./07-security-threat-model.md)
