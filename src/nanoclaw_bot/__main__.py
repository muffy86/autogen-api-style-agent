import sys
import time
import logging
from nanoclaw_bot.logging_config import setup_logging
from nanoclaw_bot.bot import create_bot, run_bot

logger = logging.getLogger("nanoclaw_bot")

MAX_RETRIES = 5
BACKOFF_BASE = 5  # seconds


def main():
    log_file = setup_logging()
    logger.info("NanoClaw Bot initializing...")
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            app = create_bot()
            # Store log_file path so /logs handler can access it
            app.bot_data["log_file"] = log_file
            logger.info("Bot created successfully, starting polling...")
            run_bot(app)
            # Clean exit (e.g., Ctrl+C handled by python-telegram-bot)
            logger.info("Bot stopped cleanly.")
            break
        except ValueError as e:
            logger.critical(f"Configuration error: {e}")
            print(f"Configuration error: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (KeyboardInterrupt).")
            break
        except Exception as e:
            retries += 1
            wait = BACKOFF_BASE * (2 ** (retries - 1))  # 5s, 10s, 20s, 40s, 80s
            logger.error(
                f"Bot crashed: {e}. Restarting in {wait}s... "
                f"(attempt {retries}/{MAX_RETRIES})",
                exc_info=True
            )
            try:
                time.sleep(wait)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user during restart backoff.")
                break
    else:
        logger.critical(f"Bot failed after {MAX_RETRIES} retries. Exiting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
