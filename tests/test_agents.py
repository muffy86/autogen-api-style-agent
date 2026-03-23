import subprocess
import pytest
from unittest.mock import patch, MagicMock

from nanoclaw_bot.agents import AgentManager


class TestValidateTmux:
    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_validate_tmux_installed(self, mock_which):
        mgr = AgentManager()
        mock_which.assert_called_once_with("tmux")

    @patch("nanoclaw_bot.agents.shutil.which", return_value=None)
    def test_validate_tmux_missing(self, mock_which):
        with pytest.raises(RuntimeError):
            AgentManager()


class TestSessionName:
    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_session_name(self, mock_which):
        mgr = AgentManager()
        assert mgr._session_name("myagent") == "nanoclaw_agent_myagent"


class TestStartAgent:
    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_start_agent_success(self, mock_which):
        mgr = AgentManager()
        with patch.object(mgr, "is_session_running", return_value=False), \
             patch.object(mgr, "_run") as mock_run:
            result = mgr.start_agent("myagent", "python agent.py")
            assert result is True
            mock_run.assert_called_once()

    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_start_agent_already_running(self, mock_which):
        mgr = AgentManager()
        with patch.object(mgr, "is_session_running", return_value=True):
            result = mgr.start_agent("myagent", "python agent.py")
            assert result is False


class TestStopAgent:
    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_stop_agent_success(self, mock_which):
        mgr = AgentManager()
        with patch.object(mgr, "is_session_running", return_value=True), \
             patch.object(mgr, "_run") as mock_run:
            result = mgr.stop_agent("myagent")
            assert result is True
            mock_run.assert_called_once()

    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_stop_agent_not_running(self, mock_which):
        mgr = AgentManager()
        with patch.object(mgr, "is_session_running", return_value=False):
            result = mgr.stop_agent("myagent")
            assert result is False


class TestListSessions:
    @patch("nanoclaw_bot.agents.shutil.which", return_value="/usr/bin/tmux")
    def test_list_sessions(self, mock_which):
        mgr = AgentManager()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "nanoclaw_agent_openai\n"
            "nanoclaw_agent_mistral\n"
            "my_other_session\n"
            "dev_server\n"
        )
        with patch.object(mgr, "_run", return_value=mock_result):
            sessions = mgr.list_sessions()
            assert len(sessions) == 2
            names = [s.name for s in sessions]
            assert "openai" in names
            assert "mistral" in names
