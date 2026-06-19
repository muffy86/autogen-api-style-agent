# Component survey

See also: [overview](./00-overview.md), [architecture](./03-architecture.md), [free-model config](./06-free-models-config.md).

All dates/stars are approximate snapshots taken on 2026-04-30. `NOASSERTION` means the GitHub repo metadata did not expose a clean SPDX license; treat those repos as needing manual legal review before vendoring.

## 2. Open-source agentic browser and computer-use projects

| name | repo | license | stars (approx) | last_commit | role_in_stack | fork_or_use | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| browser-use | <https://github.com/browser-use/browser-use> | MIT | 91.4k | 2026-04-26 | high-level Playwright agent loop | Use | Best open Python browser-use loop; strong for tab/task execution, not a browser shell |
| steel-browser | <https://github.com/steel-dev/steel-browser> | Apache-2.0 | 6.9k | 2026-04-29 | self-hosted headless browser API | Use | Good Browserbase-style session service; useful for remote browser pools |
| Stagehand | <https://github.com/browserbase/stagehand> | MIT | 22.4k | 2026-04-30 | deterministic TS browser automation | Use | Strong `act/extract/observe/agent` primitive layer; good TypeScript adapter |
| Skyvern | <https://github.com/Skyvern-AI/skyvern> | AGPL-3.0 | 21.4k | 2026-04-30 | workflow-oriented browser automation | Use selectively | Strong workflow patterns, but AGPL limits vendoring appetite |
| AutoGPT | <https://github.com/Significant-Gravitas/AutoGPT> | NOASSERTION | 183.9k | 2026-04-29 | agent tooling reference | Reference only | Broad ecosystem value; too much surface area for direct reuse |
| Open Interpreter | <https://github.com/OpenInterpreter/open-interpreter> | AGPL-3.0 | 63.4k | 2026-04-27 | local computer-use and shell execution | Use selectively | Good desktop-computer-use patterns; keep isolated because of AGPL |
| E2B | <https://github.com/e2b-dev/E2B> | Apache-2.0 | 12.0k | 2026-04-30 | sandboxed compute/runtime | Use | Strong option for remote code sandboxes; not required for fully local mode |
| Claude quickstarts `computer-use-demo` | <https://github.com/anthropics/claude-quickstarts> | MIT | 16.4k | 2026-02-05 | reference computer-use UX | Reference only | Good prompt/interaction patterns; not a control plane |
| OmniParser | <https://github.com/microsoft/OmniParser> | CC-BY-4.0 | 24.7k | 2025-09-09 | UI element parsing / grounding | Use selectively | Useful for hostile UIs/screenshots; CC-BY makes code-vendoring awkward |
| pyspur | <https://github.com/PySpur-Dev/pyspur> | Apache-2.0 | 5.7k | 2025-07-20 | agent canvas / orchestration UI | Reference only | Strong inspiration for shared canvases and workflow editing |
| agent-zero | <https://github.com/agent0ai/agent-zero> | NOASSERTION | 17.4k | 2026-04-28 | autonomous multi-step agent patterns | Reference only | Replacement for missing `aaronchoi/agent-zero`; useful as orchestration reference |
| Firecrawl | <https://github.com/firecrawl/firecrawl> | AGPL-3.0 | 113.4k | 2026-04-30 | crawl/extract service | Use via API boundary | Valuable web extraction layer; keep out-of-process due AGPL |
| scira | <https://github.com/zaidmukaddam/scira> | AGPL-3.0 | 11.6k | 2026-03-20 | AI search UI patterns | Reference only | Good UI inspiration; not a substrate choice |
| assistant-ui | <https://github.com/assistant-ui/assistant-ui> | MIT | 9.9k | 2026-04-30 | composable chat/canvas UI components | Use | Strong front-end primitive set for sidebar, threads, artifacts |
| aibitat | <https://github.com/wladpaiva/aibitat> | MIT | 151 | 2025-04-11 | lightweight open Comet-style UI | Reference only | Small but relevant proof that browser-native AI shells are forkable |
| Playwright MCP | <https://github.com/microsoft/playwright-mcp> | Apache-2.0 | 31.8k | 2026-04-30 | MCP browser control surface | Use | Best replacement for missing `chat-with-mcp`/other dead browser-MCP repos |

### Browser automation recommendation

Use **browser-use + Stagehand + Playwright MCP** as the primary browser tool chain, with **steel-browser** as the optional remote session pool. Keep Skyvern/Open Interpreter/Firecrawl behind process boundaries for selective use cases.

## 3. Forkable browser bases

| name | repo | license | stars (approx) | last_commit | role_in_stack | fork_or_use | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| Chromium fork reference (Brave) | <https://github.com/brave/brave-browser> | MPL-2.0 | 22.4k | 2026-04-30 | reference for full browser-product path | Reference only | Best signal for what a real Chromium-product fork buys: true browser behaviors, extensions, policies; highest implementation cost |
| Electron | <https://github.com/electron/electron> | MIT | 121.1k | 2026-04-30 | primary browser shell base | **Use** | Best time-to-prototype; full desktop APIs, session partitions, IPC, mature packaging; extension parity is incomplete |
| Tauri 2 | <https://github.com/tauri-apps/tauri> | Apache-2.0 | 106.1k | 2026-04-30 | lightweight native shell | Reference only | Excellent for light desktop apps, but browser-extension support is effectively Windows/WebView2-only |
| Firefox base (Floorp) | <https://github.com/Floorp-Projects/Floorp> | MPL-2.0 | 8.1k | 2026-04-28 | Firefox-derived browser shell | Reference only | Better add-on compatibility than Tauri, but weaker Chromium ecosystem fit for agent/web tooling |
| Electron Chrome extension bridge | <https://github.com/ramboxapp/electron-chrome-extensions> | NOASSERTION | 41 | 2024-11-12 | optional extension-compat shim | Use selectively | Helps Electron approximate more Chrome APIs when needed |

Closed wrapper products such as Arc, Dia, Sidekick, Wavebox, and Sigma OS remain useful UX references, but they are not viable sovereign bases because they are closed-source or do not expose a forkable browser core.

### Primary recommendation

**Choose Electron for Phase 2.**

Why:

- fastest path from this repo's existing SvelteKit UI to a working browser shell
- robust local IPC and desktop integration
- easy split between visible UI process and separate headless browser workers
- packaging/update story is mature
- extension shortcomings are manageable if MCP and first-party tools are the primary integration surface

### Long-term caveat

If exact Chrome extension and enterprise-policy parity becomes existential, the future migration path is a Chromium fork. Do not pay that cost in Phase 2.

## 4. Agent orchestration, memory, runtime, and tool fabric

| name | repo | license | stars (approx) | last_commit | role_in_stack | fork_or_use | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| AutoGen | <https://github.com/microsoft/autogen> | CC-BY-4.0 | 57.6k | 2026-04-06 | existing team collaboration substrate | **Use** | Already present in this repo; do not replace it |
| LangGraph | <https://github.com/langchain-ai/langgraph> | MIT | 30.9k | 2026-04-30 | durable workflow graph around AutoGen | **Use** | Adds checkpoints, graph state, resumability, and HITL |
| CrewAI | <https://github.com/crewAIInc/crewAI> | MIT | 50.4k | 2026-04-30 | alternative role-based agent DSL | Reference only | Useful benchmark; overlaps too much with existing AutoGen teams |
| LangSmith SDK | <https://github.com/langchain-ai/langsmith-sdk> | MIT | 869 | 2026-04-30 | hosted tracing/evals option | Use optionally | Useful if team already lives in LangSmith; not the sovereignty-first default |
| Langfuse | <https://github.com/langfuse/langfuse> | NOASSERTION | 26.4k | 2026-04-30 | self-hosted observability/evals | **Use** | Best OSS-friendly observability control plane |
| Magentic-One pattern | <https://github.com/microsoft/autogen> | CC-BY-4.0 | 57.6k | 2026-04-06 | multi-agent planner/executor pattern | Reference only | Use the pattern inside AutoGen; no separate control plane needed |
| Letta | <https://github.com/letta-ai/letta> | Apache-2.0 | 22.4k | 2026-04-08 | long-horizon memory/agent OS patterns | Use selectively | Strong memory-agent ideas; heavier than needed for day-1 |
| Mem0 | <https://github.com/mem0ai/mem0> | Apache-2.0 | 54.5k | 2026-04-29 | extracted long-term memory | **Use** | Best pragmatic memory layer to bolt on now |
| Temporal | <https://github.com/temporalio/temporal> | MIT | 20.0k | 2026-04-30 | durable 24/7 workflow runtime | **Use** | Strongest reliability story for recurring and resumable tasks |
| Inngest | <https://github.com/inngest/inngest> | NOASSERTION | 5.3k | 2026-04-30 | lighter event/workflow runtime | Reference only | Faster to start, weaker than Temporal for long-lived heavy agent jobs |
| Trigger.dev | <https://github.com/triggerdotdev/trigger.dev> | Apache-2.0 | 14.7k | 2026-04-30 | TS workflow/runtime option | Reference only | Good DX, but less battle-tested for multi-day agents than Temporal |
| Composio | <https://github.com/ComposioHQ/composio> | MIT | 28.0k | 2026-04-30 | managed auth + SaaS tool catalog | Use selectively | Great for OAuth-heavy SaaS tools; cloud dependency means do not make it mandatory |
| MCP spec | <https://github.com/modelcontextprotocol/modelcontextprotocol> | NOASSERTION | 8.0k | 2026-04-30 | open tool protocol | **Use** | This is the main tool boundary |
| MCP server set | <https://github.com/modelcontextprotocol/servers> | NOASSERTION | 84.8k | 2026-04-17 | reference/open MCP servers | **Use** | First stop for filesystem/db/devtool adapters |
| MCP registry | <https://github.com/modelcontextprotocol/registry> | NOASSERTION | 6.8k | 2026-04-30 | official metadata registry | Use | Useful for discovery; do not trust-install blindly |

### Orchestration recommendation

Compose the stack as follows:

- **AutoGen** for intra-team collaboration
- **LangGraph** for durable outer control flow
- **Mem0** for extracted long-term memory
- **Langfuse + OTel** for traces/evals
- **Temporal** for scheduled and resumable background jobs
- **MCP first**, **Composio second** for tool access

## 5. Free-first model routing and inference candidates

| name | repo | license | stars (approx) | last_commit | role_in_stack | fork_or_use | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| LiteLLM | <https://github.com/BerriAI/litellm> | NOASSERTION | 45.3k | 2026-04-30 | primary model router/proxy | **Use** | Best self-hosted routing surface for multi-provider fallback |
| Portkey gateway | <https://github.com/Portkey-AI/gateway> | MIT | 11.5k | 2026-03-25 | hosted/hybrid AI gateway | Reference only | Good product, but adds a hosted control-plane dependency |
| Ollama | <https://github.com/ollama/ollama> | MIT | 170.4k | 2026-04-30 | local model runtime | **Use** | Best local default for developer machines |
| llama.cpp | <https://github.com/ggml-org/llama.cpp> | MIT | 107.6k | 2026-04-30 | local CPU/GPU inference | Use | Excellent fallback for offline or constrained hardware |
| vLLM | <https://github.com/vllm-project/vllm> | Apache-2.0 | 78.7k | 2026-04-30 | high-throughput local/cluster inference | Use later | Better for server deployments than laptops |
| LM Studio | <https://github.com/lmstudio-ai/lms> | MIT | 4.7k | 2026-04-07 | local desktop inference UX | Reference only | Good user-facing local model manager |
| Jan | <https://github.com/janhq/jan> | NOASSERTION | 42.3k | 2026-04-30 | local model desktop UX | Reference only | Useful UX inspiration more than substrate |
| GPT4All | <https://github.com/nomic-ai/gpt4all> | MIT | 77.4k | 2025-05-27 | local model packaging | Reference only | Good offline packaging story; weaker routing/integration fit |
| Akash network | <https://github.com/akash-network/node> | Apache-2.0 | 1.1k | 2026-04-29 | decentralized compute/inference substrate | Use experimentally | Real decentralized GPU supply; managed inference is promising but not core-path mature |
| Petals | <https://github.com/bigscience-workshop/petals> | MIT | 10.1k | 2024-09-07 | distributed community inference | Reference only | Interesting research system; stale for production default |
| Hyperspace | <https://github.com/hyperspaceai/hyperspace-node> | none declared | 283 | 2026-04-30 | decentralized inference network | Use experimentally | Active enough for R&D, not stable enough for core routing |
| Bittensor subnet 2 | <https://github.com/inference-labs-inc/subnet-2> | MIT | 2.1k | 2026-04-08 | verifiable inference experiment | Use experimentally | Treat Bittensor as R&D, not core serving |

### Free-provider routing stance

Use LiteLLM to front:

- Google AI Studio free quota
- OpenRouter free models
- Groq free tier
- Cerebras free tier
- Cloudflare Workers AI free quota
- Hugging Face inference credits
- Mistral experiment tier
- local Ollama/llama.cpp fallback

Do **not** assume Together's historical free credits still exist for the public path; public docs now point users toward paid credits/programs rather than a durable free tier.

## 6. IDE, filesystem, and desktop integration candidates

| name | repo | license | stars (approx) | last_commit | role_in_stack | fork_or_use | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| Zed | <https://github.com/zed-industries/zed> | NOASSERTION | 80.9k | 2026-04-30 | premium IDE bridge target | **Use** | Strong MCP and Agent Panel support; best open editor target after VS Code |
| Zed extensions | <https://github.com/zed-industries/extensions> | none declared | 1.6k | 2026-04-30 | extension packaging surface | Use | Required if we ship native Zed packaging |
| opencode | <https://github.com/anomalyco/opencode> | MIT | 152.6k | 2026-04-30 | terminal-native coding agent bridge | **Use** | Excellent local coding-agent entry point with MCP support |
| VS Code | <https://github.com/microsoft/vscode> | MIT | 184.4k | 2026-04-30 | broadest editor entry point | Use | Official MCP docs make this a must-support client |
| Continue | <https://github.com/continuedev/continue> | Apache-2.0 | 32.9k | 2026-04-17 | IDE extension bridge | **Use** | Good multi-IDE entry point and MCP-friendly config |
| Cline | <https://github.com/cline/cline> | Apache-2.0 | 61.2k | 2026-04-30 | high-autonomy coding agent bridge | Use | Excellent embedded coding-agent surface |
| Aider | <https://github.com/Aider-AI/aider> | Apache-2.0 | 44.2k | 2026-04-25 | headless code-editing agent | Use | Strong CLI coding agent for automation tasks |
| Plandex | <https://github.com/plandex-ai/plandex> | MIT | 15.3k | 2025-10-03 | long-running coding plans | Use selectively | Useful for repo-scale coding workflows |
| MCP filesystem server | <https://github.com/modelcontextprotocol/servers> | NOASSERTION | 84.8k | 2026-04-17 | local file access | **Use** | Default filesystem surface before adding custom bridges |
| chokidar | <https://github.com/paulmillr/chokidar> | MIT | 12.1k | 2026-04-30 | filesystem watches | Use | Good file-change feed into memory/reindexing pipelines |
| rclone | <https://github.com/rclone/rclone> | MIT | 56.9k | 2026-04-30 | optional FUSE mount substrate | Use selectively | Practical way to project remote/local workspaces through a mount layer |
| pywinauto | <https://github.com/pywinauto/pywinauto> | BSD-3-Clause | 6.0k | 2026-04-13 | Windows UI automation | Use | Better semantic Windows control than pure input injection |
| AutoHotkey | <https://github.com/AutoHotkey/AutoHotkey> | GPL-2.0 | 12.3k | 2026-04-26 | Windows desktop scripting | Use selectively | Great escape hatch; GPL means keep it as an external dependency |
| PyAutoGUI | <https://github.com/asweigart/pyautogui> | BSD-3-Clause | 12.5k | 2024-08-20 | cross-platform input injection | Use selectively | Useful fallback where semantic APIs are missing |
| nut.js | <https://github.com/nut-tree/nut.js> | none declared | 2.8k | 2024-05-01 | Node desktop automation | Reference only | Viable for Electron-native experiments, but licensing needs review |

### OS mapping

- **macOS**: AppleScript / `osascript` first; add coordinate-input fallback only where app scripting dictionaries are absent.
- **Linux**: AT-SPI / D-Bus first for GTK/Qt apps; fall back to input injection only when accessibility trees are broken.
- **Windows**: `pywinauto` first, AutoHotkey second, PyAutoGUI only as the last resort.

## Decision summary

- Browser tool chain: **browser-use + Stagehand + Playwright MCP**
- Browser shell: **Electron**
- Orchestration: **AutoGen inside LangGraph**
- Runtime: **Temporal**
- Observability: **Langfuse + OTel**
- Memory: **Mem0**
- Tool plane: **MCP first, Composio selective**
- Model router: **LiteLLM**
- IDE bridges: **Zed, VS Code, Continue, opencode, Cline**
