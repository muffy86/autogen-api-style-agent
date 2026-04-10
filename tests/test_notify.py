from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nanoclaw_bot.handlers.notify import check_agents_job, notify_handler


def _make_mocks(text="/notify", user_id=12345678, owner_id=12345678):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    context.bot_data = {"config": config}
    context.application.job_queue.run_repeating = MagicMock()

    return update, context


@pytest.mark.asyncio
async def test_notify_status_default():
    update, context = _make_mocks("/notify")
    await notify_handler(update, context)
    call_args = update.message.reply_text.call_args[0][0]
    assert "disabled" in call_args.lower()


@pytest.mark.asyncio
async def test_notify_on():
    update, context = _make_mocks("/notify on")
    await notify_handler(update, context)
    assert context.bot_data["notify_enabled"] is True
    context.application.job_queue.run_repeating.assert_called_once()


@pytest.mark.asyncio
async def test_notify_off():
    update, context = _make_mocks("/notify off")
    mock_job = MagicMock()
    context.bot_data["notify_job"] = mock_job
    context.bot_data["notify_enabled"] = True
    await notify_handler(update, context)
    assert context.bot_data["notify_enabled"] is False
    mock_job.schedule_removal.assert_called_once()


@pytest.mark.asyncio
async def test_notify_autorestart_on():
    update, context = _make_mocks("/notify autorestart on")
    await notify_handler(update, context)
    assert context.bot_data["notify_autorestart"] is True


@pytest.mark.asyncio
async def test_check_agents_job_detects_crash():
    """When a watched agent disappears, sends alert."""
    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = 12345678
    context.bot_data = {
        "config": config,
        "watched_agents": {"myagent": {"command": "python bot.py"}},
        "notify_autorestart": False,
    }
    context.bot.send_message = AsyncMock()

    with patch("nanoclaw_bot.handlers.notify.AgentManager") as mock_mgr:
        mgr_instance = mock_mgr.return_value
        mgr_instance._session_name.return_value = "nanoclaw_agent_myagent"
        mgr_instance.is_session_running.return_value = False

        await check_agents_job(context)

    context.bot.send_message.assert_called_once()
    call_args = context.bot.send_message.call_args
    assert "stopped" in call_args.kwargs.get("text", call_args[1].get("text", "")).lower()
