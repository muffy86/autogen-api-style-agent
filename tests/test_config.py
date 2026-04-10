from __future__ import annotations

import pytest

from autogen_api_agent.config import AppConfig, ProviderConfig, get_config

_PROVIDER_ENV_VARS = [
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "TOGETHER_API_KEY",
    "TOGETHER_MODEL",
    "OPENROUTER_API_KEY",
    "OPENROUTER_MODEL",
    "GOOGLE_API_KEY",
    "GOOGLE_MODEL",
    "MOONSHOT_API_KEY",
    "KIMI_MODEL",
    "MISTRAL_API_KEY",
    "MISTRAL_MODEL",
]


@pytest.fixture
def clear_provider_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _PROVIDER_ENV_VARS:
        monkeypatch.delenv(key, raising=False)


def test_provider_config_loads_defaults_with_no_env_vars_set(
    clear_provider_env: None,
) -> None:
    config = ProviderConfig(_env_file=None)

    assert config.openai_api_key is None
    assert config.openai_model == "gpt-4o"
    assert config.together_api_key is None
    assert config.together_model == "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    assert config.openrouter_api_key is None
    assert config.openrouter_model == "openai/gpt-4o"
    assert config.google_api_key is None
    assert config.google_model == "gemini-2.0-flash"
    assert config.moonshot_api_key is None
    assert config.kimi_model == "kimi-k2.5"
    assert config.mistral_api_key is None
    assert config.mistral_model == "mistral-large-latest"


def test_provider_config_available_providers_returns_empty_list_with_no_keys(
    clear_provider_env: None,
) -> None:
    config = ProviderConfig(_env_file=None)

    assert config.available_providers() == []


def test_provider_config_available_providers_detects_keys(
    clear_provider_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-key")
    monkeypatch.setenv("MISTRAL_API_KEY", "mistral-key")

    config = ProviderConfig(_env_file=None)

    assert config.available_providers() == ["openai", "google", "mistral"]


def test_app_config_has_expected_defaults(clear_provider_env: None) -> None:
    config = AppConfig(_env_file=None)

    assert config.host == "0.0.0.0"
    assert config.port == 8000
    assert config.debug is False
    assert config.default_provider == "openai"
    assert config.default_team == "productivity"
    assert config.max_turns == 30
    assert config.timeout_seconds == 300
    assert config.session_ttl_minutes == 60
    assert isinstance(config.providers, ProviderConfig)


def test_get_config_returns_app_config_instance(
    clear_provider_env: None,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.chdir(tmp_path)

    config = get_config()

    assert isinstance(config, AppConfig)
