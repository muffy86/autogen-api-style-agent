from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only
from nanoclaw_bot.eliza import ElizaOSIntegration


def _get_eliza(context: ContextTypes.DEFAULT_TYPE) -> ElizaOSIntegration:
    """Get or create the ElizaOSIntegration instance."""
    if "eliza" not in context.bot_data:
        context.bot_data["eliza"] = ElizaOSIntegration()
    return context.bot_data["eliza"]


@owner_only
async def eliza_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI personality engine with conversation memory."""
    text = update.message.text
    parts = text.split(None, 2)

    subcommand = parts[1].lower() if len(parts) > 1 else "status"
    args = parts[2] if len(parts) > 2 else ""

    eliza = _get_eliza(context)
    chat_id = update.effective_chat.id

    if subcommand == "set":
        name = args.strip().lower()
        if not name:
            await update.message.reply_text(
                "Usage: `/eliza set <personality>`\n\n"
                "Available: assistant, therapist, creative, technical",
                parse_mode="Markdown"
            )
            return
        if eliza.set_personality(chat_id, name):
            p = eliza.get_personality(chat_id)
            await update.message.reply_text(
                f"{p['emoji']} Personality switched to *{p['name']}*\n\n"
                f"_{p['system_prompt']}_",
                parse_mode="Markdown"
            )
        else:
            available = ", ".join(ElizaOSIntegration.PERSONALITIES.keys())
            await update.message.reply_text(
                f"⚠️ Unknown personality `{name}`.\n\nAvailable: {available}",
                parse_mode="Markdown"
            )

    elif subcommand == "list":
        lines = ["🧬 *Available Personalities*\n"]
        for key, p in ElizaOSIntegration.PERSONALITIES.items():
            lines.append(f"{p['emoji']} *{p['name']}* (`{key}`)")
            lines.append(f"  _{p['system_prompt']}_\n")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    elif subcommand == "clear":
        eliza.clear_memory(chat_id)
        await update.message.reply_text("🧹 Conversation memory cleared.")

    elif subcommand == "status":
        p = eliza.get_personality(chat_id)
        p_name = eliza.get_personality_name(chat_id)
        mem_size = eliza.get_memory_size(chat_id)
        available = ", ".join(
            f"{v['emoji']}{v['name']}" for v in ElizaOSIntegration.PERSONALITIES.values()
        )

        await update.message.reply_text(
            f"🧬 *Eliza Status*\n\n"
            f"• *Personality:* {p['emoji']} {p['name']} (`{p_name}`)\n"
            f"• *Memory:* {mem_size} messages\n"
            f"• *Available:* {available}\n\n"
            f"Use `/eliza set <mode>` to switch.\n"
            f"Use `/eliza <prompt>` to enhance a prompt.",
            parse_mode="Markdown"
        )

    else:
        prompt_text = text.split(None, 1)[1] if len(text.split(None, 1)) > 1 else ""
        if not prompt_text:
            await update.message.reply_text(
                "Usage: `/eliza <prompt>` to enhance a prompt.",
                parse_mode="Markdown"
            )
            return

        ctx = eliza.enhance(chat_id, prompt_text)
        p = eliza.get_personality(chat_id)

        recent = ctx['messages'][-5:]
        context_lines = []
        for msg in recent:
            role_label = "👤 User" if msg['role'] == 'user' else "🤖 Assistant"
            content = msg['content']
            if len(content) > 200:
                content = content[:200] + "..."
            context_lines.append(f"  {role_label}: {content}")

        context_block = "\n".join(context_lines) if context_lines else "  (empty)"

        await update.message.reply_text(
            f"{p['emoji']} *{p['name']}* — Enhanced Prompt\n\n"
            f"*System Prompt:*\n_{ctx['system_prompt']}_\n\n"
            f"*Conversation Context ({len(ctx['messages'])} msgs):*\n{context_block}\n\n"
            f"*Your Input:*\n`{prompt_text}`\n\n"
            f"_Ready to send to any LLM API._",
            parse_mode="Markdown"
        )
