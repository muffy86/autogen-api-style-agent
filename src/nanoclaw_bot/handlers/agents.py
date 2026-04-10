from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot.agents import AgentManager
from nanoclaw_bot.security import owner_only


def _get_agent_manager(context: ContextTypes.DEFAULT_TYPE) -> AgentManager:
    """Get or create the AgentManager instance."""
    if "agent_manager" not in context.bot_data:
        context.bot_data["agent_manager"] = AgentManager()
    return context.bot_data["agent_manager"]


@owner_only
async def agents_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage AI agent processes."""
    text = update.message.text
    parts = text.split(None, 2)  # /agents [subcommand] [args...]

    subcommand = parts[1].lower() if len(parts) > 1 else "list"
    args = parts[2] if len(parts) > 2 else ""

    try:
        manager = _get_agent_manager(context)
    except RuntimeError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return

    if subcommand == "list":
        sessions = manager.list_sessions()
        if not sessions:
            await update.message.reply_text(
                "🔌 No agent sessions running.\n\nStart one with: `/agents start <name> <command>`",
                parse_mode="Markdown",
            )
            return
        lines = [f"• `{s.name}` — {'🟢 running' if s.running else '🔴 stopped'}" for s in sessions]
        await update.message.reply_text(
            f"🤖 *Agent Sessions* ({len(sessions)}):\n\n" + "\n".join(lines),
            parse_mode="Markdown",
        )

    elif subcommand == "start":
        # Parse: /agents start <name> <command>
        start_parts = args.split(None, 1)
        if len(start_parts) < 2:
            await update.message.reply_text(
                "Usage: `/agents start <name> <command>`\n\n"
                "Example: `/agents start myagent npm start`",
                parse_mode="Markdown",
            )
            return
        name, command = start_parts
        started = manager.start_agent(name, command)
        if started:
            if "watched_agents" not in context.bot_data:
                context.bot_data["watched_agents"] = {}
            context.bot_data["watched_agents"][name] = {"command": command, "working_dir": None}
            await update.message.reply_text(
                f"✅ Agent `{name}` started.\nCommand: `{command}`",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"⚠️ Agent `{name}` is already running.\n"
                f"Use `/agents restart {name} {command}` to restart.",
                parse_mode="Markdown",
            )

    elif subcommand == "stop":
        name = args.strip()
        if not name:
            await update.message.reply_text("Usage: `/agents stop <name>`", parse_mode="Markdown")
            return
        stopped = manager.stop_agent(name)
        if stopped:
            watched = context.bot_data.get("watched_agents", {})
            watched.pop(name, None)
            await update.message.reply_text(f"🛑 Agent `{name}` stopped.", parse_mode="Markdown")
        else:
            await update.message.reply_text(
                f"⚠️ Agent `{name}` is not running.",
                parse_mode="Markdown",
            )

    elif subcommand == "restart":
        start_parts = args.split(None, 1)
        if len(start_parts) < 2:
            await update.message.reply_text(
                "Usage: `/agents restart <name> <command>`", parse_mode="Markdown"
            )
            return
        name, command = start_parts
        manager.restart_agent(name, command)
        await update.message.reply_text(
            f"🔄 Agent `{name}` restarted.\nCommand: `{command}`",
            parse_mode="Markdown",
        )

    elif subcommand == "logs":
        name = args.strip()
        if not name:
            await update.message.reply_text("Usage: `/agents logs <name>`", parse_mode="Markdown")
            return
        log = manager.get_session_log(name)
        if log is None:
            await update.message.reply_text(
                f"⚠️ Agent `{name}` not found or not running.",
                parse_mode="Markdown",
            )
        elif not log.strip():
            await update.message.reply_text(
                f"📋 Agent `{name}` — no output yet.",
                parse_mode="Markdown",
            )
        else:
            # Truncate if too long for Telegram (4096 char limit)
            if len(log) > 3900:
                log = log[-3900:]
            await update.message.reply_text(
                f"📋 *Agent `{name}` logs:*\n\n```\n{log}\n```",
                parse_mode="Markdown",
            )

    else:
        await update.message.reply_text(
            "Unknown subcommand. Available:\n"
            "• `/agents` — List sessions\n"
            "• `/agents start <name> <cmd>`\n"
            "• `/agents stop <name>`\n"
            "• `/agents restart <name> <cmd>`\n"
            "• `/agents logs <name>`",
            parse_mode="Markdown",
        )
