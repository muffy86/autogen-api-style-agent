from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from nanoclaw_bot.handlers.start import start_handler
from nanoclaw_bot.handlers.configure import configure_handler
from nanoclaw_bot.handlers.keys import keys_handler
from nanoclaw_bot.handlers.status import status_handler
from nanoclaw_bot.handlers.help import help_handler
from nanoclaw_bot.handlers.agents import agents_handler
from nanoclaw_bot.handlers.shell import shell_handler
from nanoclaw_bot.handlers.logs import logs_handler
from nanoclaw_bot.handlers.update import update_handler
from nanoclaw_bot.handlers.notify import notify_handler
from nanoclaw_bot.handlers.keyboard import callback_handler


def register_handlers(app: Application):
    """Register all command handlers."""
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("configure", configure_handler))
    app.add_handler(CommandHandler("keys", keys_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("agents", agents_handler))
    app.add_handler(CommandHandler("shell", shell_handler))
    app.add_handler(CommandHandler("logs", logs_handler))
    app.add_handler(CommandHandler("update", update_handler))
    app.add_handler(CommandHandler("notify", notify_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
