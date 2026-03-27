# Elysium AI OS

A browser-based AI workspace with a desktop OS interface. Multi-model AI chat with support for OpenAI, Anthropic, Google, xAI, and Groq.

> ⚠️ **Alpha Software** — Many features shown in the UI are under active development and not yet functional.

## Stack

- **Frontend:** SvelteKit 2, Svelte 5, Tailwind CSS 4
- **AI:** Vercel AI SDK v6 (OpenAI, Anthropic, Google, xAI, Groq)
- **Deployment:** Vercel

## Quick Start

```bash
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
pnpm install
cp .env.example .env  # Add your API keys
pnpm dev
```

## Environment Variables

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_GENERATIVE_AI_API_KEY=...
XAI_API_KEY=...
GROQ_API_KEY=gsk_...
```

## What Works

- ✅ Multi-model AI chat with streaming (7 models, 5 providers)
- ✅ Desktop window manager (drag, resize, minimize, maximize)
- ✅ Conversation management with model selection
- ✅ Markdown rendering with syntax highlighting

## Under Development

- 🚧 File management (currently static mockup)
- 🚧 Terminal (currently static mockup)
- 🚧 Search (UI only, no backend)
- 🚧 Settings — API Keys, Privacy, Models sections
- 🚧 Dashboard automations and workflows
- 🚧 Real integrations (GitHub, Notion, Slack, etc.)
- 🚧 Authentication and user accounts
- 🚧 Database persistence (currently localStorage only)

## NanoClaw Bot (Telegram)

A separate Python Telegram bot for remote agent management lives in `src/nanoclaw_bot/`. See [NanoClaw Bot docs](docs/nanoclaw-bot.md) for setup instructions.

## License

MIT
