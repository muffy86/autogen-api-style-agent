import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot.security import owner_only

logger = logging.getLogger("nanoclaw_bot.logs")


def _tail(file_path: Path, lines: int = 30) -> str:
    """Read the last N lines of a file."""
    try:
        with open(file_path) as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:]
            return "".join(tail_lines).rstrip()
    except FileNotFoundError:
        return ""


@owner_only
async def logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View recent bot log entries."""
    log_file: Path | None = context.bot_data.get("log_file")

    if not log_file or not log_file.exists():
        await update.message.reply_text("📋 No log file found.")
        return

    # Parse optional line count: /logs or /logs 50
    text = update.message.text
    parts = text.split()
    lines = 30  # default
    if len(parts) > 1:
        try:
            lines = int(parts[1])
            lines = min(lines, 100)  # cap at 100 lines
            lines = max(lines, 1)
        except ValueError:
            await update.message.reply_text(
                "Usage: `/logs [N]`\n\nExample: `/logs 50` (default: 30, max: 100)",
                parse_mode="Markdown",
            )
            return

    content = _tail(log_file, lines)

    if not content:
        await update.message.reply_text("📋 Log file is empty.")
        return

    # Truncate for Telegram
    if len(content) > 3900:
        content = content[-3900:]

    await update.message.reply_text(
        f"📋 *Bot Logs* (last {lines} lines):\n\n```\n{content}\n```", parse_mode="Markdown"
    )
