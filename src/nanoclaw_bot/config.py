import os
from pathlib import Path

from dotenv import dotenv_values, set_key


class ConfigManager:
    """Manages secure .env-based configuration."""

    def __init__(self, env_path: Path | None = None):
        if env_path:
            self.env_path = env_path
        else:
            project_env = Path.cwd() / ".env"
            home_env = Path.home() / ".nanoclaw" / ".env"
            self.env_path = project_env if project_env.exists() else home_env

    def ensure_env_file(self):
        """Create .env file with secure permissions if it doesn't exist."""
        self.env_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.env_path.exists():
            self.env_path.touch(mode=0o600)
        else:
            self.env_path.chmod(0o600)

    def get(self, key: str) -> str | None:
        """Get a config value."""
        values = dotenv_values(self.env_path)
        return values.get(key) or os.environ.get(key)

    def set(self, key: str, value: str):
        """Set a config value in .env file."""
        self.ensure_env_file()
        set_key(str(self.env_path), key, value)
        self.env_path.chmod(0o600)

    def set_many(self, keys: dict[str, str]):
        """Set multiple config values."""
        for k, v in keys.items():
            self.set(k, v)

    def get_all_api_keys(self) -> dict[str, str]:
        """Get all configured API keys (keys ending in _KEY or _TOKEN, excluding TELEGRAM_*)."""
        values = dotenv_values(self.env_path)
        return {
            k: v
            for k, v in values.items()
            if (k.endswith("_KEY") or k.endswith("_TOKEN")) and not k.startswith("TELEGRAM_") and v
        }

    @staticmethod
    def mask_value(value: str, visible: int = 4) -> str:
        """Mask a secret value, showing only last N chars."""
        if len(value) <= visible:
            return "••••"
        return "••••" + value[-visible:]

    def get_bot_token(self) -> str:
        token = self.get("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN not set. Add it to .env or set as environment variable."
            )
        return token

    def get_owner_chat_id(self) -> int:
        chat_id = self.get("TELEGRAM_OWNER_CHAT_ID")
        if not chat_id:
            raise ValueError(
                "TELEGRAM_OWNER_CHAT_ID not set. Add it to .env or set as environment variable."
            )
        return int(chat_id)
