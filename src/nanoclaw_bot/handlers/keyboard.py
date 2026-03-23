import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from nanoclaw_bot.security import owner_only
from nanoclaw_bot.config import ConfigManager
from nanoclaw_bot import __version__

logger = logging.getLogger("nanoclaw_bot.keyboard")


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data="menu_status"),
            InlineKeyboardButton("🔑 Keys", callback_data="menu_keys"),
        ],
        [
            InlineKeyboardButton("🤖 Agents", callback_data="menu_agents"),
            InlineKeyboardButton("🔔 Notify", callback_data="menu_notify"),
        ],
        [
            InlineKeyboardButton("📋 Logs", callback_data="menu_logs"),
            InlineKeyboardButton("📦 Backup", callback_data="menu_backup"),
        ],
        [
            InlineKeyboardButton("🔄 Update", callback_data="menu_update"),
            InlineKeyboardButton("❓ Help", callback_data="menu_help"),
        ],
        [
            InlineKeyboardButton("🧬 Eliza", callback_data="menu_eliza"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def agents_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the agents sub-menu."""
    keyboard = [
        [
            InlineKeyboardButton("📋 List Agents", callback_data="agents_list"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback

    # Security check — only allow owner
    config = context.bot_data.get("config")
    if not config:
        await query.edit_message_text("⚠️ Bot misconfigured.")
        return
    try:
        owner_id = config.get_owner_chat_id()
    except ValueError:
        await query.edit_message_text("🔒 Bot locked.")
        return
    if query.from_user.id != owner_id:
        await query.edit_message_text("🚫 Unauthorized.")
        return

    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            "🦎 *NanoClaw Bot* — Main Menu\n\nTap a button or use text commands:",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif data == "menu_status":
        # Build status inline
        import sys, time
        from pathlib import Path
        config: ConfigManager = context.bot_data["config"]
        uptime_seconds = int(time.time() - context.bot_data.get("start_time", time.time()))
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        api_keys = config.get_all_api_keys()
        is_termux = Path("/data/data/com.termux").exists()

        text = (
            f"📊 *Status*\n\n"
            f"• *Version:* `{__version__}`\n"
            f"• *Python:* `{sys.version.split()[0]}`\n"
            f"• *Platform:* {'Termux' if is_termux else 'Linux'}\n"
            f"• *Uptime:* {hours}h {minutes}m {seconds}s\n"
            f"• *API Keys:* {len(api_keys)} configured"
        )

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_keys":
        config: ConfigManager = context.bot_data["config"]
        api_keys = config.get_all_api_keys()
        if not api_keys:
            text = "🔑 No API keys configured.\n\nUse `/configure KEY=value` to set keys."
        else:
            lines = [f"• `{k}` = `{config.mask_value(v)}`" for k, v in api_keys.items()]
            text = f"🔑 *API Keys* ({len(api_keys)}):\n\n" + "\n".join(lines)

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_agents":
        await query.edit_message_text(
            "🤖 *Agent Management*\n\nUse buttons below or text commands:",
            reply_markup=agents_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif data == "agents_list":
        try:
            from nanoclaw_bot.agents import AgentManager
            mgr = AgentManager()
            sessions = mgr.list_sessions()
            if not sessions:
                text = "🔌 No agent sessions running.\n\nStart one with:\n`/agents start <name> <command>`"
            else:
                lines = [f"• `{s.name}` — 🟢 running" for s in sessions]
                text = f"🤖 *Agents* ({len(sessions)}):\n\n" + "\n".join(lines)
        except Exception:
            text = "🤖 *Agents:* N/A (tmux not available)"

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_agents")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_notify":
        enabled = context.bot_data.get("notify_enabled", False)
        autorestart = context.bot_data.get("notify_autorestart", False)
        watched = context.bot_data.get("watched_agents", {})

        text = (
            f"🔔 *Notifications*\n\n"
            f"• *Monitoring:* {'✅ on' if enabled else '❌ off'}\n"
            f"• *Auto-restart:* {'✅ on' if autorestart else '❌ off'}\n"
            f"• *Watched:* {len(watched)} agents"
        )

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_logs":
        from nanoclaw_bot.handlers.logs import _tail
        from pathlib import Path
        log_file = context.bot_data.get("log_file")
        if log_file and Path(log_file).exists():
            content = _tail(Path(log_file), lines=15)
            if content:
                if len(content) > 3000:
                    content = content[-3000:]
                text = f"📋 *Recent Logs:*\n\n```\n{content}\n```"
            else:
                text = "📋 Log file is empty."
        else:
            text = "📋 No log file found."

        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_update":
        text = (
            "🔄 *Update Bot*\n\n"
            "To update, use the text command:\n"
            "`/update`\n\n"
            "This will pull latest code, reinstall deps, and restart."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_backup":
        text = (
            "📦 *Backup*\n\n"
            "To export config, use the text command:\n"
            "`/backup`\n\n"
            "Sends a JSON file with key names, agent list, and settings."
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_help":
        text = (
            "❓ *Quick Help*\n\n"
            "• `/configure KEY=val` — Set API keys\n"
            "• `/agents start <n> <cmd>` — Start agent\n"
            "• `/shell <cmd>` — Run command\n"
            "• `/notify on` — Enable crash alerts\n"
            "• `/eliza <prompt>` — AI personality engine\n"
            "• `/update` — Self-update\n\n"
            "Full reference: /help"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif data == "menu_eliza":
        from nanoclaw_bot.eliza import ElizaOSIntegration
        eliza = context.bot_data.get("eliza")
        if not eliza:
            eliza = ElizaOSIntegration()
            context.bot_data["eliza"] = eliza

        chat_id = query.message.chat_id
        p = eliza.get_personality(chat_id)
        p_name = eliza.get_personality_name(chat_id)
        mem_size = eliza.get_memory_size(chat_id)
        available = ", ".join(
            f"{v['emoji']}{v['name']}" for v in ElizaOSIntegration.PERSONALITIES.values()
        )

        text = (
            f"🧬 *Eliza AI Personality Engine*\n\n"
            f"• *Personality:* {p['emoji']} {p['name']} (`{p_name}`)\n"
            f"• *Memory:* {mem_size} messages\n"
            f"• *Available:* {available}\n\n"
            f"*Commands:*\n"
            f"• `/eliza set <mode>` — Switch personality\n"
            f"• `/eliza <prompt>` — Enhance prompt\n"
            f"• `/eliza clear` — Clear memory\n"
            f"• `/eliza list` — List personalities"
        )
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="menu_main")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
