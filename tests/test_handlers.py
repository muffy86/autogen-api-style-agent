import pytest
from unittest.mock import AsyncMock, MagicMock

from nanoclaw_bot.handlers.configure import configure_handler


def _make_mocks(text, user_id=12345678, owner_id=12345678):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    context.bot_data = {"config": config}

    return update, context, config


@pytest.mark.asyncio
async def test_configure_valid_keys():
    update, context, config = _make_mocks(
        "/configure OPENAI_API_KEY=sk-123 MISTRAL_API_KEY=xm-456"
    )
    await configure_handler(update, context)
    config.set_many.assert_called_once_with(
        {"OPENAI_API_KEY": "sk-123", "MISTRAL_API_KEY": "xm-456"}
    )


@pytest.mark.asyncio
async def test_configure_no_args():
    update, context, config = _make_mocks("/configure")
    await configure_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Usage" in call_args
    config.set_many.assert_not_called()


@pytest.mark.asyncio
async def test_configure_invalid_key_name():
    update, context, config = _make_mocks("/configure lowercase_key=val")
    await configure_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "UPPER_SNAKE_CASE" in call_args
    config.set_many.assert_not_called()


@pytest.mark.asyncio
async def test_configure_missing_value():
    update, context, config = _make_mocks("/configure OPENAI_API_KEY=")
    await configure_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Empty value" in call_args
    config.set_many.assert_not_called()


@pytest.mark.asyncio
async def test_configure_no_equals():
    update, context, config = _make_mocks("/configure OPENAI_API_KEY")
    await configure_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "Invalid format" in call_args
    config.set_many.assert_not_called()
