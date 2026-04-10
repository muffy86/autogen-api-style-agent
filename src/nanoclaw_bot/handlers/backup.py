import json
import logging
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot import __version__
from nanoclaw_bot.config import ConfigManager
from nanoclaw_bot.security import owner_only

logger = logging.getLogger("nanoclaw_bot.backup")


@owner_only
async def backup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export bot configuration summary as a JSON file."""
    config: ConfigManager = context.bot_data["config"]

    # Gather data
    api_keys = config.get_all_api_keys()

    # Get agent sessions
    agent_sessions = []
    try:
        from nanoclaw_bot.agents import AgentManager

        mgr = AgentManager()
        for s in mgr.list_sessions():
            agent_sessions.append({"name": s.name, "running": s.running})
    except Exception:
        pass

    watched_agents = {}
    for name, info in context.bot_data.get("watched_agents", {}).items():
        watched_agents[name] = {"command": info.get("command", "unknown")}

    backup_data = {
        "backup_timestamp": datetime.now(timezone.utc).isoformat(),
        "bot": {
            "version": __version__,
            "python": sys.version.split()[0],
            "platform": "Termux" if Path("/data/data/com.termux").exists() else "Linux",
            "uptime_seconds": int(time.time() - context.bot_data.get("start_time", time.time())),
            "env_path": str(config.env_path),
        },
        "api_keys_configured": list(api_keys.keys()),  # Names only, NOT values
        "agent_sessions": agent_sessions,
        "watched_agents": watched_agents,
        "notify": {
            "enabled": context.bot_data.get("notify_enabled", False),
            "autorestart": context.bot_data.get("notify_autorestart", False),
        },
    }

    # Write to temp file and send as document
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="nanoclaw_backup_", delete=False
    ) as f:
        json.dump(backup_data, f, indent=2)
        temp_path = f.name

    try:
        with open(temp_path, "rb") as document:
            await update.message.reply_document(
                document=document,
                filename=f"nanoclaw_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                caption="📦 *NanoClaw Bot Backup*\n\nContains config summary (no secrets).",
                parse_mode="Markdown",
            )
        logger.info("Backup exported successfully")
    finally:
        Path(temp_path).unlink(missing_ok=True)
