import sys
from nanoclaw_bot.bot import create_bot, run_bot


def main():
    try:
        app = create_bot()
        run_bot(app)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
