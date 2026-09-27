# Free-first models and `litellm_config.yaml`

See also: [component survey](./02-component-survey.md), [architecture](./03-architecture.md).

## 1. Strategy

Use a **self-hosted LiteLLM proxy** as the only model endpoint the browser shell and agent hub talk to.

Reasons:

- one OpenAI-compatible endpoint for every caller
- provider fallback and cooldown logic in one place
- easy separation between public-cloud, local-only, and experimental decentralized routes
- policy hooks for sensitivity tagging, spend caps, and observability

## 2. Routing policy

### Pools

- **Pool A: free cloud fast path** — Gemini Flash, Groq, Cerebras, Cloudflare, OpenRouter free pool, Hugging Face routed credits, Mistral experiment tier
- **Pool B: local protected path** — Ollama or llama.cpp for restricted/local-only prompts
- **Pool C: local server path** — vLLM on a home server or workstation for higher-throughput private tasks
- **Pool D: experimental decentralized path** — Akash / Hyperspace / Bittensor only behind a feature flag

### Sensitivity gates

| data class | default route |
| --- | --- |
| public web content | free cloud pool |
| internal notes / code without secrets | free cloud pool if allowed by org policy, else local |
| secrets / credentials / tokens / password-manager context | local only |
| personal mail, calendar, desktop state | local only unless user elevates explicitly |
| regulated or enterprise-private documents | local only or approved private endpoint |

### Provider stance

- **Google AI Studio**: best first fast path while free quota remains
- **Groq**: best overflow for low-latency text/code
- **Cerebras**: strong overflow for large fast open models
- **Cloudflare Workers AI**: useful global backup, especially for modest-volume tasks
- **OpenRouter free**: opportunistic pool only; the available model set is fluid
- **Hugging Face**: experimentation and burst backup, not the primary serving path
- **Mistral experiment tier**: useful but rate-limited; do not depend on it for heavy throughput
- **Together**: do not model it as free-forever in 2026 public planning

## 3. Key rotation and quota handling

### Key rotation rules

- one env var per provider key; never share raw keys with the renderer
- if an org legitimately has multiple approved keys for the same provider, encode them as separate LiteLLM aliases (`gemini_free_a`, `gemini_free_b`) and let the router distribute traffic
- do **not** treat consumer multi-account farming as a supported strategy

### Quota tracking rules

- store provider usage counters in Redis
- mark an alias unavailable once daily or per-minute quota is hit
- cool down and retry lower-priority aliases before falling back to local
- export provider and alias exhaustion into Langfuse/Loki/Grafana
- keep hard monthly cost caps even for supposedly free providers, because free programs change

## 4. Example `litellm_config.yaml`

```yaml
model_list:
  - model_name: fast-free-primary
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GEMINI_API_KEY
      rpm: 10
      tpm: 250000
      timeout: 30

  - model_name: fast-free-overflow-groq
    litellm_params:
      model: groq/openai/gpt-oss-120b
      api_key: os.environ/GROQ_API_KEY
      rpm: 30
      tpm: 8000
      timeout: 20

  - model_name: fast-free-overflow-cerebras
    litellm_params:
      model: cerebras/gpt-oss-120b
      api_key: os.environ/CEREBRAS_API_KEY
      rpm: 30
      tpm: 60000
      timeout: 20

  - model_name: fast-free-overflow-cloudflare
    litellm_params:
      model: cloudflare/@cf/meta/llama-3.3-70b-instruct-fp8-fast
      api_key: os.environ/CLOUDFLARE_API_KEY
      api_base: os.environ/CLOUDFLARE_API_BASE
      timeout: 30

  - model_name: fast-free-overflow-openrouter
    litellm_params:
      model: openrouter/openai/gpt-oss-20b:free
      api_key: os.environ/OPENROUTER_API_KEY
      extra_headers:
        HTTP-Referer: https://sovereign-browser.local
        X-Title: Sovereign Agentic Browser OS
      timeout: 30

  - model_name: fast-free-overflow-hf
    litellm_params:
      model: huggingface/meta-llama/Llama-3.3-70B-Instruct
      api_key: os.environ/HUGGINGFACE_API_KEY
      timeout: 45

  - model_name: fast-free-overflow-mistral
    litellm_params:
      model: mistral/mistral-small-latest
      api_key: os.environ/MISTRAL_API_KEY
      timeout: 30

  - model_name: local-private-ollama
    litellm_params:
      model: ollama/qwen2.5:14b-instruct
      api_base: http://ollama:11434
      timeout: 90

  - model_name: local-private-llamacpp
    litellm_params:
      model: openai/local-llama.cpp
      api_base: http://llamacpp:8080/v1
      api_key: dummy
      timeout: 90

  - model_name: local-private-vllm
    litellm_params:
      model: openai/Qwen/Qwen2.5-32B-Instruct
      api_base: http://vllm:8000/v1
      api_key: dummy
      timeout: 60

litellm_settings:
  set_verbose: false
  json_logs: true
  drop_params: true
  success_callback: ["langfuse_otel"]
  failure_callback: ["langfuse_otel"]
  redact_user_api_key_info: true

router_settings:
  routing_strategy: usage-based-routing-v2
  num_retries: 1
  timeout: 45
  allowed_fails: 2
  cooldown_time: 120
  enable_pre_call_checks: true
  fallbacks:
    - fast-free-primary:
        [
          fast-free-overflow-groq,
          fast-free-overflow-cerebras,
          fast-free-overflow-cloudflare,
          fast-free-overflow-openrouter,
          fast-free-overflow-hf,
          fast-free-overflow-mistral,
          local-private-ollama,
          local-private-llamacpp
        ]
  context_window_fallbacks:
    - fast-free-primary:
        [local-private-vllm, local-private-ollama]

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  store_prompts_in_spend_logs: false
  background_health_checks: true
  infer_model_from_keys: true
```

## 5. Suggested logical aliases exposed to the rest of the system

| alias | intended use | fallback chain |
| --- | --- | --- |
| `browser-fast` | quick browsing, DOM summarization, tab triage | Gemini → Groq → Cerebras → Cloudflare → OpenRouter free → Ollama |
| `browser-vision` | screenshot/UI understanding | Gemini / Cloudflare / local vision model |
| `planner-balanced` | task decomposition and orchestration | Gemini → Cerebras → local vLLM |
| `research-deep` | report synthesis and multi-doc analysis | Gemini → OpenRouter free reasoning-capable model → local vLLM |
| `local-private` | any restricted prompt or file-bound task | Ollama → llama.cpp → vLLM |

## 6. Operational rules

- every route logs provider, latency, prompt token estimate, outcome, and sensitivity tag
- provider failures never bubble straight to the UI; the user sees alias-level status instead
- browser shell users choose **policy profiles**, not raw providers
- local-only mode disables all cloud aliases at the router layer, not just in the UI
- decentralized providers are isolated behind aliases that no default policy profile uses

## 7. Official source list

- [OpenRouter free models router](https://openrouter.ai/docs/guides/routing/routers/free-models-router)
- [Groq rate limits](https://console.groq.com/docs/rate-limits)
- [Cloudflare Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing)
- [Cerebras pricing](https://inference-docs.cerebras.ai/support/pricing)
- [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits)
- [Mistral experiment tier](https://docs.mistral.ai/admin/user-management-finops/tier)
- [Hugging Face inference pricing](https://huggingface.co/docs/api-inference/pricing)
- [Akash managed AI inference](https://akash.network/blog/akashml-managed-ai-inference-on-the-decentralized-supercloud)
