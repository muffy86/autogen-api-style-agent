from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only


@owner_only
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with quick-start instructions."""
    await update.message.reply_text(
        "🦎 *NanoClaw Bot* — Remote Agent Control Panel\n\n"
        "Available commands:\n"
        "• /configure KEY=val KEY=val — Set API keys\n"
        "• /keys — View configured keys (masked)\n"
        "• /status — System health check\n"
        "• /help — Full help\n\n"
        "Quick start:\n"
        "`/configure OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-...`",
        parse_mode="Markdown"
    )
