import os
import sys
import asyncio
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from nanoclaw_bot.security import owner_only

logger = logging.getLogger("nanoclaw_bot.update")


async def _run_cmd(cmd: str, cwd: str | None = None) -> tuple[str, str, int]:
    """Run a shell command asynchronously. Returns (stdout, stderr, exit_code)."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
    return (
        stdout.decode(errors="replace").rstrip(),
        stderr.decode(errors="replace").rstrip(),
        proc.returncode,
    )


def _find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")


@owner_only
async def update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pull latest code from GitHub, reinstall deps, and restart the bot."""
    await update.message.reply_text("🔄 Starting update...")

    try:
        project_root = _find_project_root()
    except FileNotFoundError as e:
        await update.message.reply_text(f"❌ {e}")
        return

    cwd = str(project_root)

    # Step 1: git pull
    await update.message.reply_text("📥 Pulling latest from GitHub...")
    stdout, stderr, code = await _run_cmd("git pull origin main", cwd=cwd)

    if code != 0:
        await update.message.reply_text(
            f"❌ Git pull failed (exit {code}):\n```\n{stderr or stdout}\n```",
            parse_mode="Markdown"
        )
        logger.error(f"Update failed: git pull exit={code}: {stderr}")
        return

    git_output = stdout

    # Check if already up to date
    if "Already up to date" in git_output:
        await update.message.reply_text("✅ Already up to date. No restart needed.")
        return

    # Step 2: pip install
    await update.message.reply_text("📦 Installing dependencies...")
    stdout, stderr, code = await _run_cmd("pip install -e .", cwd=cwd)

    if code != 0:
        await update.message.reply_text(
            f"❌ pip install failed (exit {code}):\n```\n{stderr[:1000]}\n```",
            parse_mode="Markdown"
        )
        logger.error(f"Update failed: pip install exit={code}: {stderr}")
        return

    # Step 3: Report success and restart
    if len(git_output) > 1000:
        git_output = git_output[:1000] + "\n..."

    await update.message.reply_text(
        f"✅ *Update complete!*\n\n"
        f"```\n{git_output}\n```\n\n"
        f"🔄 Restarting bot in 2 seconds...",
        parse_mode="Markdown"
    )

    logger.info(f"Update successful. Restarting bot process...")

    # Give Telegram time to deliver the message
    await asyncio.sleep(2)

    # Restart: replace current process with fresh Python invocation
    os.execv(sys.executable, [sys.executable, "-m", "nanoclaw_bot"])
