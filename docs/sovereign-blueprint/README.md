# Sovereign blueprint index

## TL;DR

This blueprint recommends building a sovereign Perplexity Comet alternative by:

- keeping the existing `src/autogen_api_agent/` repo code as the agent hub
- adding an **Electron** browser shell over the current SvelteKit UI
- wrapping current AutoGen teams with **LangGraph** and **Temporal**
- routing all models through **LiteLLM** with free-first fallbacks and local-only safety gates
- using **MCP first** and **Composio selective** for tools
- adding **Langfuse + OTel + Loki/Grafana** for observability
- hardening the system with **Authentik, Infisical, Tailscale, gVisor, and Firecracker**

If executed in order, the first three implementation PRs should be enough to produce a working sovereign agent hub plus the first browser shell.

## Document map

1. [00-overview.md](./00-overview.md) — executive summary, success criteria, glossary
2. [01-perplexity-comet-analysis.md](./01-perplexity-comet-analysis.md) — official Comet / Max / Enterprise analysis
3. [02-component-survey.md](./02-component-survey.md) — project-by-project survey across browser, orchestration, model, IDE, and desktop layers
4. [03-architecture.md](./03-architecture.md) — final architecture and Mermaid diagrams
5. [04-repo-structure.md](./04-repo-structure.md) — proposed repo layout and graft plan
6. [05-roadmap.md](./05-roadmap.md) — phased implementation plan sized for build tasks
7. [06-free-models-config.md](./06-free-models-config.md) — concrete LiteLLM config and routing rules
8. [07-security-threat-model.md](./07-security-threat-model.md) — STRIDE model, data classification, zero-trust design

## Recommended next 3 PRs to ship

- [ ] **PR 1:** `infra(agent-hub): add LiteLLM, Langfuse, Mem0, and compose profiles`
- [ ] **PR 2:** `feat(orchestration): wrap current AutoGen teams with LangGraph and Temporal entrypoints`
- [ ] **PR 3:** `feat(browser): bootstrap Electron shell with persistent sidebar, profile partitions, and tab broker`

## How to use this blueprint

- Start with [00-overview.md](./00-overview.md) and [03-architecture.md](./03-architecture.md).
- Use [02-component-survey.md](./02-component-survey.md) when deciding whether to fork, vendor, or just integrate upstream.
- Treat [05-roadmap.md](./05-roadmap.md) as the implementation backlog.
- Keep [07-security-threat-model.md](./07-security-threat-model.md) open while designing tool access, model routing, and desktop bridges.
