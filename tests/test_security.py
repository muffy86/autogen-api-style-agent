import pytest
from unittest.mock import AsyncMock, MagicMock

from nanoclaw_bot.security import owner_only


@owner_only
async def dummy_handler(update, context):
    await update.message.reply_text("OK")


@pytest.mark.asyncio
async def test_owner_allowed():
    update = MagicMock()
    update.effective_user.id = 12345678
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = 12345678
    context.bot_data = {"config": config}

    await dummy_handler(update, context)
    update.message.reply_text.assert_called_once_with("OK")


@pytest.mark.asyncio
async def test_unauthorized_user():
    update = MagicMock()
    update.effective_user.id = 99999999
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = 12345678
    context.bot_data = {"config": config}

    await dummy_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Unauthorized" in call_args


@pytest.mark.asyncio
async def test_no_owner_configured():
    update = MagicMock()
    update.effective_user.id = 12345678
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.side_effect = ValueError("not set")
    context.bot_data = {"config": config}

    await dummy_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "locked" in call_args.lower()


@pytest.mark.asyncio
async def test_no_config_in_bot_data():
    update = MagicMock()
    update.effective_user.id = 12345678
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    context.bot_data = {}

    await dummy_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "misconfigured" in call_args.lower()
