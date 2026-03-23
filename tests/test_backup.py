import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from nanoclaw_bot.handlers.backup import backup_handler


def _make_mocks(text="/backup", user_id=12345678, owner_id=12345678):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    config.get_all_api_keys.return_value = {"OPENAI_API_KEY": "sk-test", "MISTRAL_API_KEY": "xm-test"}
    config.env_path = "/home/.env"
    context.bot_data = {
        "config": config,
        "start_time": 1000000.0,
        "watched_agents": {"mybot": {"command": "python bot.py"}},
        "notify_enabled": True,
        "notify_autorestart": False,
    }

    return update, context


@pytest.mark.asyncio
async def test_backup_sends_document():
    """Backup should send a JSON document via Telegram."""
    update, context = _make_mocks()

    with patch("nanoclaw_bot.agents.AgentManager") as MockMgr:
        MockMgr.return_value.list_sessions.return_value = []
        await backup_handler(update, context)

    update.message.reply_document.assert_called_once()
    call_kwargs = update.message.reply_document.call_args
    assert "nanoclaw_backup_" in call_kwargs.kwargs.get("filename", call_kwargs[1].get("filename", ""))


@pytest.mark.asyncio
async def test_backup_no_secrets():
    """Backup JSON should contain key names but NOT values."""
    update, context = _make_mocks()
    captured_data = {}

    original_dump = json.dump
    def capture_dump(data, f, **kwargs):
        captured_data.update(data)
        return original_dump(data, f, **kwargs)

    with patch("nanoclaw_bot.agents.AgentManager") as MockMgr, \
         patch("nanoclaw_bot.handlers.backup.json.dump", side_effect=capture_dump):
        MockMgr.return_value.list_sessions.return_value = []
        await backup_handler(update, context)

    # Should have key names
    assert "OPENAI_API_KEY" in captured_data.get("api_keys_configured", [])
    # Should NOT have key values anywhere in the JSON string
    json_str = json.dumps(captured_data)
    assert "sk-test" not in json_str
    assert "xm-test" not in json_str
