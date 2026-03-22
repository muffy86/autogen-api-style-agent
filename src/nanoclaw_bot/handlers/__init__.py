from telegram.ext import Application, CommandHandler
from nanoclaw_bot.handlers.start import start_handler
from nanoclaw_bot.handlers.configure import configure_handler
from nanoclaw_bot.handlers.keys import keys_handler
from nanoclaw_bot.handlers.status import status_handler
from nanoclaw_bot.handlers.help import help_handler


def register_handlers(app: Application):
    """Register all command handlers."""
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("configure", configure_handler))
    app.add_handler(CommandHandler("keys", keys_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("help", help_handler))
