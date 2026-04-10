from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nanoclaw_bot.handlers.update import _find_project_root, update_handler


def _make_mocks(text="/update", user_id=12345678, owner_id=12345678):
    update = MagicMock()
    update.effective_user.id = user_id
    update.message.text = text
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    config = MagicMock()
    config.get_owner_chat_id.return_value = owner_id
    context.bot_data = {"config": config}

    return update, context


def test_find_project_root():
    """_find_project_root should find the directory containing pyproject.toml."""
    root = _find_project_root()
    assert (root / "pyproject.toml").exists()


@pytest.mark.asyncio
async def test_update_already_up_to_date():
    """When git reports 'Already up to date', skip pip install and restart."""
    update_obj, context = _make_mocks()

    async def mock_run_cmd(cmd, cwd=None):
        if "git pull" in cmd:
            return ("Already up to date.", "", 0)
        return ("", "", 0)

    with patch("nanoclaw_bot.handlers.update._run_cmd", side_effect=mock_run_cmd):
        await update_handler(update_obj, context)

    calls = [c[0][0] for c in update_obj.message.reply_text.call_args_list]
    assert any("Already up to date" in c for c in calls)


@pytest.mark.asyncio
async def test_update_git_pull_failure():
    """When git pull fails, report error and don't continue."""
    update_obj, context = _make_mocks()

    async def mock_run_cmd(cmd, cwd=None):
        if "git pull" in cmd:
            return ("", "fatal: not a git repository", 128)
        return ("", "", 0)

    with patch("nanoclaw_bot.handlers.update._run_cmd", side_effect=mock_run_cmd):
        await update_handler(update_obj, context)

    calls = [c[0][0] for c in update_obj.message.reply_text.call_args_list]
    assert any("failed" in c.lower() for c in calls)


@pytest.mark.asyncio
async def test_update_success_triggers_restart():
    """Successful update should call os.execv to restart."""
    update_obj, context = _make_mocks()

    call_count = {"git": 0, "pip": 0}

    async def mock_run_cmd(cmd, cwd=None):
        if "git pull" in cmd:
            call_count["git"] += 1
            return ("Updating abc123..def456\n1 file changed", "", 0)
        if "pip install" in cmd:
            call_count["pip"] += 1
            return ("Successfully installed nanoclaw-bot", "", 0)
        return ("", "", 0)

    with (
        patch("nanoclaw_bot.handlers.update._run_cmd", side_effect=mock_run_cmd),
        patch("nanoclaw_bot.handlers.update.asyncio.sleep", new_callable=AsyncMock),
        patch("nanoclaw_bot.handlers.update.os.execv") as mock_execv,
    ):
        await update_handler(update_obj, context)

    assert call_count["git"] == 1
    assert call_count["pip"] == 1
    mock_execv.assert_called_once()
