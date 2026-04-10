from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot.config import ConfigManager
from nanoclaw_bot.security import owner_only


@owner_only
async def keys_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all configured API keys with masked values."""
    config: ConfigManager = context.bot_data["config"]
    api_keys = config.get_all_api_keys()

    if not api_keys:
        await update.message.reply_text(
            "🔑 No API keys configured yet.\n\nUse `/configure KEY=value` to set keys.",
            parse_mode="Markdown",
        )
        return

    lines = [f"• `{k}` = `{config.mask_value(v)}`" for k, v in api_keys.items()]
    await update.message.reply_text(
        f"🔑 *Configured API Keys* ({len(api_keys)}):\n\n" + "\n".join(lines), parse_mode="Markdown"
    )
