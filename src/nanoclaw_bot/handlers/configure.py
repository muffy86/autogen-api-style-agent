import re
from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only
from nanoclaw_bot.config import ConfigManager

VALID_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')


@owner_only
async def configure_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse and save API keys from message."""
    config: ConfigManager = context.bot_data["config"]
    text = update.message.text

    args_text = text.split(None, 1)[1] if len(text.split(None, 1)) > 1 else ""

    if not args_text:
        await update.message.reply_text(
            "Usage: `/configure KEY=value KEY=value`\n\n"
            "Example:\n"
            "`/configure OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-...`",
            parse_mode="Markdown"
        )
        return

    keys = {}
    errors = []
    for part in args_text.split():
        if "=" not in part:
            errors.append(f"Invalid format: `{part}` (expected KEY=value)")
            continue
        key, value = part.split("=", 1)
        if not VALID_KEY_PATTERN.match(key):
            errors.append(f"Invalid key name: `{key}` (use UPPER_SNAKE_CASE)")
            continue
        if not value:
            errors.append(f"Empty value for: `{key}`")
            continue
        keys[key] = value

    if errors:
        await update.message.reply_text("⚠️ Errors:\n" + "\n".join(errors), parse_mode="Markdown")
        if not keys:
            return

    config.set_many(keys)

    lines = [f"✅ `{k}` = `{config.mask_value(v)}`" for k, v in keys.items()]
    await update.message.reply_text(
        f"🔑 Configured {len(keys)} key(s):\n" + "\n".join(lines),
        parse_mode="Markdown"
    )
