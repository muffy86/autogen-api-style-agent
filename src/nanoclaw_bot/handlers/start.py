from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot.handlers.keyboard import main_menu_keyboard
from nanoclaw_bot.security import owner_only


@owner_only
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with inline keyboard menu."""
    await update.message.reply_text(
        "🦎 *NanoClaw Bot* — Remote Agent Control Panel\n\n"
        "Tap a button below or use text commands:\n\n"
        "• `/configure KEY=val` — Set API keys\n"
        "• `/agents start <name> <cmd>` — Start agents\n"
        "• `/shell <cmd>` — Run shell commands\n"
        "• `/notify on` — Enable crash alerts\n"
        "• `/update` — Self-update from GitHub\n"
        "• `/backup` — Export config backup\n"
        "• `/help` — Full command reference",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown",
    )
