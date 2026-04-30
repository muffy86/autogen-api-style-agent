# Perplexity Comet and Enterprise analysis

See also: [overview](./00-overview.md), [architecture](./03-architecture.md), [security](./07-security-threat-model.md).

> Note: several Perplexity marketing/help pages serve bot mitigation to automated fetchers. Facts below are restricted to official Perplexity pages, help-center snippets, and accessible docs captured on 2026-04-30.

## Bottom line

Official Perplexity materials describe Comet as a **Chromium-based AI browser** with:

- Chrome extension compatibility
- an assistant available in the browser/new-tab context
- cross-tab and longer-running task execution
- enterprise controls delivered through MDM/browser policies
- a separate Perplexity MCP server for Perplexity APIs, but no documented public Comet-local automation SDK/CLI

The practical implication for this blueprint: copy the interaction model, not the hosted dependency model.

## 1. What Comet officially appears to be

| Topic | Official signal | Engineering implication |
| --- | --- | --- |
| Browser core | Perplexity Enterprise says Comet is built on Chromium and works with existing Chrome extensions, enterprise policies, web apps, and SSO systems. | Competing seriously with Comet means starting from a Chromium-compatible surface, not an extension-only add-on. |
| Enterprise manageability | Perplexity help docs say Comet supports 500+ Chromium browser policies and can be managed through MDM by replacing `com.google.Chrome` with `ai.perplexity.comet`. | Comet behaves like a managed browser product, not a thin overlay. |
| Data handling posture | Enterprise blog/help material says browsing history, search queries, and AI interactions are stored locally on user devices with encryption for enterprise deployments. | The product message is privacy-aware, but the orchestration plane remains Perplexity-operated. A sovereign alternative should push both data and control local. |

Official sources:

- [Introducing Comet](https://www.perplexity.ai/hub/blog/introducing-comet)
- [Comet landing page](https://www.perplexity.ai/comet/)
- [Comet Enterprise](https://www.perplexity.ai/enterprise/comet)
- [Comet policies and controls](https://www.perplexity.ai/help-center/en/articles/13529668-comet-policies-and-controls)

## 2. Officially documented assistant capabilities

| Capability | What Perplexity says | What this means for our blueprint |
| --- | --- | --- |
| Page-native questioning | Launch blog and product pages say users can ask questions anywhere on the web without leaving the current page. | Persistent sidebar + contextual tab bindings are mandatory. |
| Whole-session browsing help | Launch material says Comet can conduct browsing sessions, compare sites, and brief the user. | Need explicit task/session objects spanning many tabs and steps. |
| Agentic actions | Perplexity says the assistant can book meetings, send emails, buy things, and do busywork, with permission prompts. | Tool execution must be policy-gated and auditable. |
| Cross-tab context | Later Comet assistant materials say the assistant can work across tabs and summarize across them. | Shared tab registry + DOM/context broker are core browser primitives. |
| Longer-horizon tasks | Perplexity says the new assistant can handle more complex jobs over longer periods and has improved permission prompts. | Requires durable workflows, not a single request/response loop. |
| Voice | Mobile Comet materials mention voice mode. | Open-source voice mode should be first-class but decoupled from browser core. |

Official sources:

- [Introducing Comet](https://www.perplexity.ai/hub/blog/introducing-comet)
- [The new Comet Assistant](https://www.perplexity.ai/hub/blog) (official blog listing and linked announcement)
- [Comet product page](https://www.perplexity.ai/comet/)
- [Enterprise overview](https://www.perplexity.ai/enterprise)

## 3. Feature gates: Pro, Max, Enterprise Pro, Enterprise Max

Perplexity's public pages split capabilities across consumer and enterprise plans. The important distinctions are below.

| Plan | Publicly stated price | Feature gates relevant to this blueprint |
| --- | --- | --- |
| Free / Pro consumer | Free / $20 mo | Basic browser/search usage; advanced model access and higher usage limits sit above free. |
| **Max (consumer)** | **$200/mo** or $2000/yr | Highest model access, Max Assistant in Comet, highest browser-agent query limits, 10,000 monthly `Computer` credits, early access to new features including Comet, priority support. |
| **Enterprise Pro** | Enterprise pricing page shows mid-tier per-seat pricing | SSO/SCIM, private Spaces collaboration, org file search, file/app integrations, admin controls, configurable memory permissions, Comet Assistant, enterprise privacy guarantees. |
| **Enterprise Max** | Higher per-seat tier than Enterprise Pro | All Enterprise Pro features plus expanded model access, higher research/query/file limits, premium security features available with even one Max seat, and stronger admin visibility. |

Important official details:

- Perplexity's Max help page explicitly prices **Max at $200/month** and ties it to **Max Assistant on Comet** plus **Computer** credits.
- Enterprise pricing/help pages place **audit logs, SCIM, and data-retention controls** behind enterprise plans, with some controls unlocked only for larger orgs or orgs containing at least one Enterprise Max seat.
- Enterprise pricing/help pages make **Spaces**, internal file/app search, and admin-governed sharing central to enterprise value.

Official sources:

- [Perplexity Max help article](https://www.perplexity.ai/help-center/en/articles/11680686-perplexity-max)
- [Introducing Perplexity Max](https://www.perplexity.ai/hub/blog/introducing-perplexity-max)
- [Perplexity Enterprise pricing](https://www.perplexity.ai/enterprise/pricing)
- [Which plan is right for you?](https://www.perplexity.ai/help-center/en/articles/11187416-which-perplexity-subscription-plan-is-right-for-you)
- [What is Enterprise Max?](https://www.perplexity.ai/help-center/en/articles/12310544-what-is-enterprise-max)
- [Comet for Enterprise](https://www.perplexity.ai/help-center/en/articles/12781449-comet-for-enterprise)

## 4. Enterprise controls that matter technically

| Control plane item | Official statement | Sovereign counter-design |
| --- | --- | --- |
| SSO / SCIM | Enterprise pricing and help docs advertise SSO + SCIM. | Use self-hosted IdP plus local policy engine. |
| Audit logs | Enterprise pricing exposes audit logs for login attempts, data modifications, and config changes. | Emit local audit logs for prompts, tool calls, approvals, and file mutations. |
| Browser policies | Help docs say 500+ Chromium policies are supported via MDM. | Expose a browser policy file plus per-agent profile policies. |
| Domain and extension control | Enterprise pages mention block domains, browser approvals, and extension controls. | Need URL allow/deny lists, tool allow/deny lists, and extension governance. |
| Prompt-injection protection | Enterprise pages explicitly market prompt-injection protection. | Build prompt-injection handling into the tool gateway and tab trust model. |
| Analytics / insights | Enterprise pricing exposes insights dashboards. | Provide self-hosted traces, metrics, and org usage dashboards. |

Official sources:

- [Comet Enterprise](https://www.perplexity.ai/enterprise/comet)
- [Comet policies and controls](https://www.perplexity.ai/help-center/en/articles/13529668-comet-policies-and-controls)
- [SSO integration getting started](https://www.perplexity.ai/help-center/en/articles/11200832-sso-integration-getting-started)
- [Enterprise pricing](https://www.perplexity.ai/enterprise/pricing)

## 5. Extension / API / automation surface

### What is officially public

- Perplexity publishes a public **Perplexity MCP server** for the **Perplexity API platform**, with tools such as `perplexity_search`, `perplexity_ask`, `perplexity_research`, and `perplexity_reason` for clients like Claude, Cursor, VS Code, and Windsurf.
- Enterprise help pages document browser policy configuration and deployment, not a browser-local automation API.

### What is not officially documented

As of 2026-04-30, no official Perplexity page found during this research exposes:

- a public Comet CLI
- a local Comet SDK for tab automation
- a documented extension API beyond Chromium compatibility
- a public workflow/scheduler API for long-running browser jobs

### Blueprint implication

Treat Comet as a **managed product with strong admin surfaces but limited public browser programmability**. Our sovereign alternative should invert that: local-first browser control, explicit APIs, and user-owned scheduling.

Official sources:

- [Perplexity MCP server guide](https://docs.perplexity.ai/guides/mcp-server)
- [Comet Enterprise](https://www.perplexity.ai/enterprise/comet)
- [Comet for Enterprise](https://www.perplexity.ai/help-center/en/articles/12781449-comet-for-enterprise)

## 6. Background workflows and long-running jobs

Official Perplexity materials imply, but do not fully specify, a durable job model:

| Signal | Official evidence | Confidence |
| --- | --- | --- |
| Longer-lived assistant tasks | Comet Assistant material says it can handle more complex jobs over longer periods. | High |
| Credit-metered computer use | Max help docs say `Computer` uses a monthly credit system with spend limits and task-complexity-based consumption. | High |
| Browser-agent query limits | Max help docs refer to the highest weekly limit on browser-agent queries. | High |
| Scheduling / cron / autonomous recurring jobs | No official scheduling API or recurring-task UI found. | Low / undocumented |
| Multi-tab orchestration | Official materials explicitly mention working across tabs. | High |
| File uploads and org repositories | Enterprise pages document file uploads, repositories, and file-app search. | High |

Blueprint implication: we should assume Comet is moving toward durable, credit-metered computer use, but the official public surface still looks like a product UX, not a developer automation platform.

## 7. What to imitate vs. what to reject

### Patterns worth cloning

- assistant-on-every-tab
- cross-tab task execution
- strict permission prompts
- enterprise browser policies
- audit and analytics surfaces
- collaboration spaces for shared research artifacts

### Patterns to reject

- hosted orchestration as the default trust assumption
- opaque pricing/credit accounting for computer-use jobs
- closed automation surfaces
- enterprise-only access to critical governance primitives

## 8. Delta to the sovereign blueprint

| Comet trait | Sovereign answer |
| --- | --- |
| Chromium browser with assistant | Electron-based sovereign browser shell with first-party agent sidebar |
| Managed AI/browser backend | Self-hosted agent hub + LiteLLM + LangGraph + Temporal |
| Enterprise-only governance | Governance is local by default; remote access is additive |
| Public Perplexity MCP for API only | Open MCP-first tool plane for browser, IDE, filesystem, desktop, and SaaS |
| Credit-metered computer use | Transparent quota accounting across providers and runtimes |

## Source list

- [Introducing Comet](https://www.perplexity.ai/hub/blog/introducing-comet)
- [Comet](https://www.perplexity.ai/comet/)
- [Perplexity Enterprise](https://www.perplexity.ai/enterprise)
- [Comet Enterprise](https://www.perplexity.ai/enterprise/comet)
- [Enterprise pricing](https://www.perplexity.ai/enterprise/pricing)
- [Comet for Enterprise](https://www.perplexity.ai/help-center/en/articles/12781449-comet-for-enterprise)
- [Comet policies and controls](https://www.perplexity.ai/help-center/en/articles/13529668-comet-policies-and-controls)
- [SSO integration getting started](https://www.perplexity.ai/help-center/en/articles/11200832-sso-integration-getting-started)
- [Perplexity Max](https://www.perplexity.ai/help-center/en/articles/11680686-perplexity-max)
- [What is Enterprise Max?](https://www.perplexity.ai/help-center/en/articles/12310544-what-is-enterprise-max)
- [Which plan is right for you?](https://www.perplexity.ai/help-center/en/articles/11187416-which-perplexity-subscription-plan-is-right-for-you)
- [Perplexity MCP server guide](https://docs.perplexity.ai/guides/mcp-server)
