from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only


@owner_only
async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detailed help for all commands."""
    await update.message.reply_text(
        "🦎 *NanoClaw Bot — Command Reference*\n\n"
        "*🚀 /start*\n"
        "Show welcome message and quick-start guide.\n\n"
        "*🔑 /configure KEY=value ...*\n"
        "Set one or more API keys. Keys must be UPPER\\_SNAKE\\_CASE.\n"
        "Example: `/configure OPENAI_API_KEY=sk-abc123`\n"
        "Multiple: `/configure OPENAI_API_KEY=sk-... MISTRAL_API_KEY=xm-...`\n\n"
        "*🔐 /keys*\n"
        "View all configured API keys with masked values.\n"
        "Only the last 4 characters are shown.\n\n"
        "*📊 /status*\n"
        "Show bot version, Python version, platform (Termux/Linux),\n"
        "uptime, and number of configured API keys.\n\n"
        "*❓ /help*\n"
        "Show this help message.\n\n"
        "*Security:*\n"
        "All commands are restricted to the configured owner chat ID.\n"
        "API keys are stored in a `.env` file with 0600 permissions.",
        parse_mode="Markdown"
    )
