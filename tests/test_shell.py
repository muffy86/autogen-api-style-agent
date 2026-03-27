import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from nanoclaw_bot.handlers.shell import shell_handler, BLOCKED_PATTERNS


def _make_mocks(text, user_id=12345678, owner_id=12345678):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()
    
    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    context.bot_data = {"config": config}
    
    return update, context


@pytest.mark.asyncio
async def test_shell_no_args():
    update, context = _make_mocks("/shell")
    await shell_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Usage" in call_args


@pytest.mark.asyncio
async def test_shell_blocked_command():
    update, context = _make_mocks("/shell rm -rf /")
    await shell_handler(update, context)
    # Should have 2 calls: none for "Running..." since it's blocked before execution
    call_args = update.message.reply_text.call_args[0][0]
    assert "Blocked" in call_args


@pytest.mark.asyncio
async def test_shell_successful_command():
    update, context = _make_mocks("/shell echo hello")
    await shell_handler(update, context)
    # Should have 2 calls: "Running..." and then the result
    assert update.message.reply_text.call_count == 2
    result_call = update.message.reply_text.call_args_list[1][0][0]
    assert "hello" in result_call
    assert "Exit code: `0`" in result_call
