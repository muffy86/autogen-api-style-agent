import os
from unittest.mock import patch

import pytest

from nanoclaw_bot.config import ConfigManager


class TestMaskValue:
    def test_mask_value_long_string(self):
        assert ConfigManager.mask_value("sk-abc123xyz") == "••••3xyz"

    def test_mask_value_short_string(self):
        assert ConfigManager.mask_value("abc") == "••••"

    def test_mask_value_exact_length(self):
        assert ConfigManager.mask_value("abcd") == "••••"

    def test_mask_value_custom_visible(self):
        assert ConfigManager.mask_value("sk-abc123xyz", visible=6) == "••••123xyz"


class TestGetBotToken:
    def test_get_bot_token_success(self, tmp_env):
        config = ConfigManager(env_path=tmp_env)
        assert config.get_bot_token() == "test-token-123"

    def test_get_bot_token_missing(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        config = ConfigManager(env_path=env_file)
        with pytest.raises(ValueError):
            config.get_bot_token()


class TestGetOwnerChatId:
    def test_get_owner_chat_id_success(self, tmp_env):
        config = ConfigManager(env_path=tmp_env)
        assert config.get_owner_chat_id() == 12345678

    def test_get_owner_chat_id_missing(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        config = ConfigManager(env_path=env_file)
        with pytest.raises(ValueError):
            config.get_owner_chat_id()


class TestSetAndGet:
    def test_set_and_get(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        config = ConfigManager(env_path=env_file)
        config.set("NEW_KEY", "new_value")
        assert config.get("NEW_KEY") == "new_value"

    def test_set_many(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        config = ConfigManager(env_path=env_file)
        config.set_many({"KEY_A": "val_a", "KEY_B": "val_b", "KEY_C": "val_c"})
        assert config.get("KEY_A") == "val_a"
        assert config.get("KEY_B") == "val_b"
        assert config.get("KEY_C") == "val_c"


class TestGetAllApiKeys:
    def test_get_all_api_keys(self, tmp_env):
        config = ConfigManager(env_path=tmp_env)
        keys = config.get_all_api_keys()
        assert "OPENAI_API_KEY" in keys
        assert "MISTRAL_API_KEY" in keys
        assert "TELEGRAM_BOT_TOKEN" not in keys
        assert "TELEGRAM_OWNER_CHAT_ID" not in keys


class TestEnsureEnvFile:
    def test_ensure_env_file_creates_with_permissions(self, tmp_path):
        env_file = tmp_path / "subdir" / ".env"
        config = ConfigManager(env_path=env_file)
        config.ensure_env_file()
        assert env_file.exists()
        mode = env_file.stat().st_mode & 0o777
        assert mode == 0o600


class TestGetFallback:
    def test_get_falls_back_to_env_var(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        config = ConfigManager(env_path=env_file)
        with patch.dict(os.environ, {"FALLBACK_TEST_KEY": "from_environ"}):
            assert config.get("FALLBACK_TEST_KEY") == "from_environ"
