import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AgentStatus:
    """Status of an agent process."""
    name: str
    running: bool
    session_name: str
    pid: int | None = None


class AgentManager:
    """Manages AI agent processes via tmux sessions."""

    SESSION_PREFIX = "nanoclaw_agent_"

    def __init__(self):
        self._validate_tmux()

    def _validate_tmux(self):
        """Check if tmux is installed."""
        if not shutil.which("tmux"):
            raise RuntimeError("tmux is not installed. Install with: pkg install tmux (Termux) or apt install tmux (Linux)")

    def _session_name(self, agent_name: str) -> str:
        """Get the tmux session name for an agent."""
        return f"{self.SESSION_PREFIX}{agent_name}"

    def _run(self, cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a subprocess command."""
        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    def is_session_running(self, session_name: str) -> bool:
        """Check if a tmux session exists."""
        result = self._run(["tmux", "has-session", "-t", session_name], check=False)
        return result.returncode == 0

    def start_agent(self, name: str, command: str, working_dir: str | None = None) -> bool:
        """Start an agent in a new tmux session.

        Args:
            name: Agent name (used for session naming)
            command: Shell command to run (e.g., "npm start", "python agent.py")
            working_dir: Working directory for the agent process

        Returns:
            True if started successfully, False if already running
        """
        session = self._session_name(name)

        if self.is_session_running(session):
            return False  # Already running

        cmd = ["tmux", "new-session", "-d", "-s", session]
        if working_dir:
            cmd.extend(["-c", working_dir])
        cmd.append(command)

        self._run(cmd)
        return True

    def stop_agent(self, name: str) -> bool:
        """Stop an agent by killing its tmux session.

        Returns:
            True if stopped, False if wasn't running
        """
        session = self._session_name(name)

        if not self.is_session_running(session):
            return False

        self._run(["tmux", "kill-session", "-t", session], check=False)
        return True

    def restart_agent(self, name: str, command: str, working_dir: str | None = None) -> bool:
        """Restart an agent (stop then start)."""
        self.stop_agent(name)
        return self.start_agent(name, command, working_dir)

    def list_sessions(self) -> list[AgentStatus]:
        """List all NanoClaw agent sessions."""
        result = self._run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            check=False
        )

        if result.returncode != 0:
            return []

        statuses = []
        for line in result.stdout.strip().splitlines():
            if line.startswith(self.SESSION_PREFIX):
                agent_name = line[len(self.SESSION_PREFIX):]
                statuses.append(AgentStatus(
                    name=agent_name,
                    running=True,
                    session_name=line,
                ))

        return statuses

    def get_session_log(self, name: str, lines: int = 20) -> str | None:
        """Capture recent output from a tmux session.

        Returns last N lines of the session's visible pane, or None if session doesn't exist.
        """
        session = self._session_name(name)
        if not self.is_session_running(session):
            return None

        result = self._run(
            ["tmux", "capture-pane", "-t", session, "-p", "-S", f"-{lines}"],
            check=False
        )

        if result.returncode != 0:
            return None

        return result.stdout.rstrip()
