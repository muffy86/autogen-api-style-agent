import logging
from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only
from nanoclaw_bot.agents import AgentManager

logger = logging.getLogger("nanoclaw_bot.notify")

POLL_INTERVAL = 30  # seconds


async def check_agents_job(context: ContextTypes.DEFAULT_TYPE):
    """Periodic job that checks if watched agents are still running."""
    watched = context.bot_data.get("watched_agents", {})
    if not watched:
        return

    try:
        manager = AgentManager()
    except RuntimeError:
        return  # tmux not available

    config = context.bot_data.get("config")
    if not config:
        return

    try:
        owner_id = config.get_owner_chat_id()
    except ValueError:
        return

    for name, info in list(watched.items()):
        session = manager._session_name(name)
        if not manager.is_session_running(session):
            autorestart = context.bot_data.get("notify_autorestart", False)

            if autorestart and info.get("command"):
                manager.start_agent(name, info["command"], info.get("working_dir"))
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"⚠️ Agent `{name}` crashed!\n🔄 Auto-restarted with: `{info['command']}`",
                    parse_mode="Markdown",
                )
                logger.warning(f"Agent {name} crashed, auto-restarted")
            else:
                await context.bot.send_message(
                    chat_id=owner_id,
                    text=f"🚨 Agent `{name}` has stopped!\nRestart with: `/agents start {name} {info.get('command', '<cmd>')}`",
                    parse_mode="Markdown",
                )
                del watched[name]
                logger.warning(f"Agent {name} crashed, removed from watch list")


@owner_only
async def notify_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage agent crash monitoring."""
    text = update.message.text
    parts = text.split()
    subcommand = parts[1].lower() if len(parts) > 1 else "status"

    if subcommand == "on":
        if context.bot_data.get("notify_enabled"):
            await update.message.reply_text("🔔 Monitoring already enabled.")
            return

        if "watched_agents" not in context.bot_data:
            context.bot_data["watched_agents"] = {}

        job = context.application.job_queue.run_repeating(
            check_agents_job,
            interval=POLL_INTERVAL,
            first=5,
            name="agent_monitor",
        )
        context.bot_data["notify_enabled"] = True
        context.bot_data["notify_job"] = job

        await update.message.reply_text(
            f"🔔 Agent monitoring *enabled* (checking every {POLL_INTERVAL}s).\n"
            f"Auto-restart: {'✅ on' if context.bot_data.get('notify_autorestart') else '❌ off'}\n\n"
            f"Agents started via `/agents start` will be automatically watched.",
            parse_mode="Markdown",
        )

    elif subcommand == "off":
        job = context.bot_data.get("notify_job")
        if job:
            job.schedule_removal()
        context.bot_data["notify_enabled"] = False
        context.bot_data["notify_job"] = None
        await update.message.reply_text(
            "🔕 Agent monitoring *disabled*.", parse_mode="Markdown"
        )

    elif subcommand == "autorestart":
        arg = parts[2].lower() if len(parts) > 2 else ""
        if arg == "on":
            context.bot_data["notify_autorestart"] = True
            await update.message.reply_text(
                "🔄 Auto-restart *enabled*. Crashed agents will be restarted automatically.",
                parse_mode="Markdown",
            )
        elif arg == "off":
            context.bot_data["notify_autorestart"] = False
            await update.message.reply_text(
                "🔄 Auto-restart *disabled*.", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "Usage: `/notify autorestart on|off`", parse_mode="Markdown"
            )

    elif subcommand == "status":
        enabled = context.bot_data.get("notify_enabled", False)
        autorestart = context.bot_data.get("notify_autorestart", False)
        watched = context.bot_data.get("watched_agents", {})

        lines = [
            "🔔 *Notification Status*\n",
            f"• *Monitoring:* {'✅ enabled' if enabled else '❌ disabled'}",
            f"• *Auto-restart:* {'✅ on' if autorestart else '❌ off'}",
            f"• *Watched agents:* {len(watched)}",
        ]
        if watched:
            for name, info in watched.items():
                lines.append(f"  — `{name}`: `{info.get('command', 'unknown')}`")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    else:
        await update.message.reply_text(
            "Usage:\n"
            "• `/notify on` — Enable monitoring\n"
            "• `/notify off` — Disable monitoring\n"
            "• `/notify status` — Show status\n"
            "• `/notify autorestart on|off` — Toggle auto-restart",
            parse_mode="Markdown",
        )
