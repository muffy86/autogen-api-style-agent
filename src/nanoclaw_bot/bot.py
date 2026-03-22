from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import Application
from nanoclaw_bot.config import ConfigManager
from nanoclaw_bot.handlers import register_handlers


def create_bot(env_path: Path | None = None) -> Application:
    """Create and configure the Telegram bot application."""
    load_dotenv(env_path)

    config = ConfigManager(env_path)
    token = config.get_bot_token()

    app = Application.builder().token(token).build()

    app.bot_data["config"] = config

    register_handlers(app)

    return app


def run_bot(app: Application):
    """Start the bot polling loop."""
    print("🤖 NanoClaw Bot starting...")
    print(f"   Owner chat ID: {app.bot_data['config'].get_owner_chat_id()}")
    print("   Send /start to your bot in Telegram to begin.")
    app.run_polling(drop_pending_updates=True)
