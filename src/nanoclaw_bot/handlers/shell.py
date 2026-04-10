import asyncio
import logging

from telegram import Update
from telegram.ext import ContextTypes

from nanoclaw_bot.security import owner_only

logger = logging.getLogger("nanoclaw_bot.shell")

# Commands that are NEVER allowed — patterns checked via substring match
BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    "> /dev/sd",
    "> /dev/nv",
    "shutdown",
    "reboot",
    "poweroff",
    "init 0",
    "init 6",
    ":(){ :|:",  # fork bomb
]

MAX_TIMEOUT = 30  # seconds


@owner_only
async def shell_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute a shell command and return output."""
    text = update.message.text
    command = text.split(None, 1)[1] if len(text.split(None, 1)) > 1 else ""

    if not command:
        await update.message.reply_text(
            "Usage: `/shell <command>`\n\n"
            "Example: `/shell ls -la`\n"
            "Timeout: 30 seconds\n\n"
            "⚠️ Use with caution.",
            parse_mode="Markdown",
        )
        return

    # Safety check
    cmd_lower = command.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            await update.message.reply_text(
                f"🚫 Blocked: command matches dangerous pattern `{pattern}`", parse_mode="Markdown"
            )
            logger.warning(f"Blocked dangerous command: {command}")
            return

    logger.info(f"Executing shell command: {command}")
    await update.message.reply_text(f"⏳ Running: `{command}`...", parse_mode="Markdown")

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=MAX_TIMEOUT)

        stdout_text = stdout.decode(errors="replace").rstrip()
        stderr_text = stderr.decode(errors="replace").rstrip()
        exit_code = proc.returncode

        # Build response
        parts = [f"$ `{command}`\n"]
        if stdout_text:
            parts.append(f"```\n{stdout_text}\n```")
        if stderr_text:
            parts.append(f"*stderr:*\n```\n{stderr_text}\n```")
        parts.append(f"Exit code: `{exit_code}`")

        response = "\n".join(parts)

        # Truncate for Telegram's 4096 char limit
        if len(response) > 3900:
            response = response[:3900] + "\n\n... _(truncated)_"

        await update.message.reply_text(response, parse_mode="Markdown")
        logger.info(f"Shell command completed: exit={exit_code}")

    except asyncio.TimeoutError:
        proc.kill()
        await update.message.reply_text(
            f"⏱️ Command timed out after {MAX_TIMEOUT}s.\nCommand: `{command}`",
            parse_mode="Markdown",
        )
        logger.warning(f"Shell command timed out: {command}")
