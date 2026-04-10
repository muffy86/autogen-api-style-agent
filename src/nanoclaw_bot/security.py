from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes


def owner_only(func):
    """Decorator that restricts handler to owner chat ID only."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        config = context.bot_data.get("config")
        if not config:
            await update.message.reply_text("⚠️ Bot misconfigured. Config manager not found.")
            return

        try:
            owner_id = config.get_owner_chat_id()
        except ValueError:
            await update.message.reply_text("🔒 Bot locked. Owner chat ID not configured.")
            return

        if update.effective_user.id != owner_id:
            await update.message.reply_text("🚫 Unauthorized. This bot is private.")
            return

        return await func(update, context)

    return wrapper
