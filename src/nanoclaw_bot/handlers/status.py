import sys
import time
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot import __version__
from nanoclaw_bot.config import ConfigManager
from nanoclaw_bot.security import owner_only


@owner_only
async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system health and status information."""
    config: ConfigManager = context.bot_data["config"]

    uptime_seconds = int(time.time() - context.bot_data["start_time"])
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
    ]

    try:
        from nanoclaw_bot.agents import AgentManager

        mgr = AgentManager()
        agent_count = len(mgr.list_sessions())
        status_lines.append(f"• *Agents:* {agent_count} running")
    except Exception:
        status_lines.append("• *Agents:* N/A")

    status_lines.extend(
        [
            f"• *Config file:* `{config.env_path}`",
        ]
    )

    await update.message.reply_text("\n".join(status_lines), parse_mode="Markdown")
