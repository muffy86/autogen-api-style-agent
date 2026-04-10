from unittest.mock import AsyncMock, MagicMock

import pytest

from nanoclaw_bot.handlers.keyboard import (
    agents_menu_keyboard,
    callback_handler,
    main_menu_keyboard,
)


def test_main_menu_has_buttons():
    kb = main_menu_keyboard()
    # Flatten all buttons
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    labels = [b.text for b in buttons]
    assert "📊 Status" in labels
    assert "🔑 Keys" in labels
    assert "🤖 Agents" in labels
    assert "❓ Help" in labels


def test_agents_menu_has_back():
    kb = agents_menu_keyboard()
    buttons = [btn for row in kb.inline_keyboard for btn in row]
    data_values = [b.callback_data for b in buttons]
    assert "menu_main" in data_values  # Back button


@pytest.mark.asyncio
async def test_callback_unauthorized():
    """Non-owner callback should be rejected."""
    query = MagicMock()
    query.answer = AsyncMock()
    query.from_user.id = 99999999
    query.data = "menu_status"
    query.edit_message_text = AsyncMock()

    update = MagicMock()
    update.callback_query = query

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = 12345678
    context.bot_data = {"config": config}

    await callback_handler(update, context)
    call_args = query.edit_message_text.call_args[0][0]
    assert "Unauthorized" in call_args


@pytest.mark.asyncio
async def test_callback_menu_main():
    """Menu main callback should show main menu."""
    query = MagicMock()
    query.answer = AsyncMock()
    query.from_user.id = 12345678
    query.data = "menu_main"
    query.edit_message_text = AsyncMock()

    update = MagicMock()
    update.callback_query = query

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = 12345678
    context.bot_data = {"config": config}

    await callback_handler(update, context)
    query.edit_message_text.assert_called_once()
    kwargs = query.edit_message_text.call_args
    assert kwargs[1].get("reply_markup") is not None  # Has keyboard
