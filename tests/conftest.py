import pytest
from pathlib import Path


@pytest.fixture
def tmp_env(tmp_path):
    """Create a temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TELEGRAM_BOT_TOKEN=test-token-123\n"
        "TELEGRAM_OWNER_CHAT_ID=12345678\n"
        "OPENAI_API_KEY=sk-test-key-abcdefgh\n"
        "MISTRAL_API_KEY=xm-test-key-12345678\n"
    )
    env_file.chmod(0o600)
    return env_file
