# NanoClaw Bot

Telegram bot for remote AI agent configuration and management. Designed for Termux (Android) and Linux.

## Quick Start

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather)
2. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
3. Clone and install:

```bash
git clone https://github.com/muffy86/autogen-api-style-agent.git
cd autogen-api-style-agent
pip install -e .
```

4. Configure:

```bash
cp .env.example .env
# Edit .env with your bot token and chat ID
```

5. Run:

```bash
python -m nanoclaw_bot
```

6. Message your bot: `/configure OPENAI_API_KEY=sk-...`

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome + quick-start instructions |
| `/configure KEY=val ...` | Set API keys securely |
| `/keys` | View configured keys (masked) |
| `/status` | System health check |
| `/help` | Full command reference |
