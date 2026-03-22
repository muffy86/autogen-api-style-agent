import sys
import time
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot import __version__
from nanoclaw_bot.security import owner_only
from nanoclaw_bot.config import ConfigManager


@owner_only
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system health and status information."""
    config: ConfigManager = context.bot_data["config"]

    if "start_time" not in context.bot_data:
        context.bot_data["start_time"] = time.time()

    uptime_seconds = int(time.time() - context.bot_data.get("start_time", time.time()))
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    api_keys = config.get_all_api_keys()

    is_termux = Path("/data/data/com.termux").exists()
    platform = "Termux (Android)" if is_termux else "Linux"

    status_lines = [
        "📊 *NanoClaw Bot Status*\n",
        f"• *Version:* `{__version__}`",
        f"• *Python:* `{sys.version.split()[0]}`",
        f"• *Platform:* {platform}",
        f"• *Uptime:* {uptime_str}",
        f"• *API Keys:* {len(api_keys)} configured",
        f"• *Config file:* `{config.env_path}`",
    ]

    await update.message.reply_text("\n".join(status_lines), parse_mode="Markdown")
