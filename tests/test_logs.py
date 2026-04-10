from unittest.mock import AsyncMock, MagicMock

import pytest

from nanoclaw_bot.handlers.logs import _tail, logs_handler


def _make_mocks(text, user_id=12345678, owner_id=12345678, log_file=None):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    context.bot_data = {"config": config, "log_file": log_file}

    return update, context


def test_tail_reads_last_lines(tmp_path):
    f = tmp_path / "test.log"
    f.write_text("line1\nline2\nline3\nline4\nline5\n")
    result = _tail(f, lines=3)
    assert "line3" in result
    assert "line4" in result
    assert "line5" in result
    assert "line1" not in result


def test_tail_missing_file(tmp_path):
    result = _tail(tmp_path / "nonexistent.log")
    assert result == ""


@pytest.mark.asyncio
async def test_logs_no_file():
    update, context = _make_mocks("/logs", log_file=None)
    await logs_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "No log file" in call_args


@pytest.mark.asyncio
async def test_logs_with_content(tmp_path):
    log_file = tmp_path / "bot.log"
    log_file.write_text("2026-03-22 INFO: Bot started\n2026-03-22 INFO: Command received\n")
    update, context = _make_mocks("/logs", log_file=log_file)
    await logs_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Bot started" in call_args


@pytest.mark.asyncio
async def test_logs_custom_line_count(tmp_path):
    log_file = tmp_path / "bot.log"
    lines = [f"line {i}\n" for i in range(50)]
    log_file.write_text("".join(lines))
    update, context = _make_mocks("/logs 5", log_file=log_file)
    await logs_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "last 5 lines" in call_args
