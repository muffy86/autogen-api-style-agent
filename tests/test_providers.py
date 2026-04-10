from __future__ import annotations

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from autogen_api_agent.config import AppConfig, ProviderConfig
from autogen_api_agent.providers.factory import ModelClientFactory


@pytest.fixture
def app_config() -> AppConfig:
    providers = ProviderConfig(
        _env_file=None,
        OPENAI_API_KEY="sk-openai",
        TOGETHER_API_KEY="together-key",
        OPENROUTER_API_KEY="openrouter-key",
        GOOGLE_API_KEY="google-key",
        MOONSHOT_API_KEY="moonshot-key",
        MISTRAL_API_KEY="mistral-key",
    )
    return AppConfig(_env_file=None, providers=providers)


def test_model_client_factory_create_openai_returns_openai_client(app_config: AppConfig) -> None:
    factory = ModelClientFactory(app_config)

    with patch("autogen_api_agent.providers.factory.OpenAIChatCompletionClient") as mock_client:
        result = factory.create("openai")

    assert result is mock_client.return_value
    mock_client.assert_called_once_with(
        model=app_config.providers.openai_model,
        api_key=app_config.providers.openai_api_key,
    )


def test_model_client_factory_create_google_returns_gemini_client(app_config: AppConfig) -> None:
    factory = ModelClientFactory(app_config)
    fake_module = ModuleType("autogen_ext.models.gemini")
    fake_constructor = MagicMock(name="GeminiChatCompletionClient", return_value=object())
    fake_module.GeminiChatCompletionClient = fake_constructor

    with patch.dict(sys.modules, {"autogen_ext.models.gemini": fake_module}):
        result = factory.create("google")

    assert result is fake_constructor.return_value
    fake_constructor.assert_called_once_with(
        model=app_config.providers.google_model,
        api_key=app_config.providers.google_api_key,
    )


def test_model_client_factory_create_together_passes_base_url_and_model_info(
    app_config: AppConfig,
) -> None:
    factory = ModelClientFactory(app_config)

    with patch("autogen_api_agent.providers.factory.OpenAIChatCompletionClient") as mock_client:
        result = factory.create("together")

    assert result is mock_client.return_value
    mock_client.assert_called_once()
    kwargs = mock_client.call_args.kwargs
    assert kwargs["model"] == app_config.providers.together_model
    assert kwargs["api_key"] == app_config.providers.together_api_key
    assert kwargs["base_url"] == app_config.providers.together_base_url
    assert kwargs["model_info"] == {
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
        "structured_output": True,
    }


def test_model_client_factory_create_openrouter_passes_correct_base_url(
    app_config: AppConfig,
) -> None:
    factory = ModelClientFactory(app_config)

    with patch("autogen_api_agent.providers.factory.OpenAIChatCompletionClient") as mock_client:
        result = factory.create("openrouter")

    assert result is mock_client.return_value
    assert mock_client.call_args.kwargs["base_url"] == app_config.providers.openrouter_base_url


def test_model_client_factory_create_kimi_passes_correct_base_url(app_config: AppConfig) -> None:
    factory = ModelClientFactory(app_config)

    with patch("autogen_api_agent.providers.factory.OpenAIChatCompletionClient") as mock_client:
        result = factory.create("kimi")

    assert result is mock_client.return_value
    assert mock_client.call_args.kwargs["base_url"] == app_config.providers.moonshot_base_url


def test_model_client_factory_create_mistral_passes_correct_base_url(app_config: AppConfig) -> None:
    factory = ModelClientFactory(app_config)

    with patch("autogen_api_agent.providers.factory.OpenAIChatCompletionClient") as mock_client:
        result = factory.create("mistral")

    assert result is mock_client.return_value
    assert mock_client.call_args.kwargs["base_url"] == app_config.providers.mistral_base_url


def test_model_client_factory_create_invalid_provider_raises_value_error(
    app_config: AppConfig,
) -> None:
    factory = ModelClientFactory(app_config)

    with pytest.raises(ValueError, match="Unknown provider"):
        factory.create("invalid")  # type: ignore[arg-type]


def test_model_client_factory_create_best_available_picks_highest_priority() -> None:
    config = MagicMock()
    config.default_provider = "openai"
    config.providers.available_providers.return_value = ["kimi", "google", "together"]
    factory = ModelClientFactory(config)

    with patch.object(factory, "create", return_value="google-client") as mock_create:
        result = factory.create_best_available()

    assert result == "google-client"
    mock_create.assert_called_once_with("google")


def test_model_client_factory_create_best_available_raises_with_no_providers() -> None:
    config = MagicMock()
    config.default_provider = "openai"
    config.providers.available_providers.return_value = []
    factory = ModelClientFactory(config)

    with pytest.raises(RuntimeError, match="No LLM provider API keys found"):
        factory.create_best_available()


def test_model_client_factory_list_available_returns_expected_mapping(
    app_config: AppConfig,
) -> None:
    app_config.providers = ProviderConfig(
        _env_file=None,
        OPENAI_API_KEY="sk-openai",
        GOOGLE_API_KEY="google-key",
    )
    factory = ModelClientFactory(app_config)

    assert factory.list_available() == {
        "openai": "gpt-4o",
        "google": "gemini-2.0-flash",
    }


@pytest.mark.parametrize(
    ("module_name", "default_model", "has_base_url"),
    [
        ("openai_provider", "gpt-4o", False),
        ("google_provider", "gemini-2.0-flash", False),
        ("together_provider", "meta-llama/Llama-3.3-70B-Instruct-Turbo", True),
        ("openrouter_provider", "openai/gpt-4o", True),
        ("kimi_provider", "kimi-k2.5", True),
        ("mistral_provider", "mistral-large-latest", True),
    ],
)
def test_provider_modules_expose_expected_constants(
    module_name: str,
    default_model: str,
    has_base_url: bool,
) -> None:
    module = importlib.import_module(f"autogen_api_agent.providers.{module_name}")

    assert default_model == module.DEFAULT_MODEL
    assert default_model in module.RECOMMENDED_MODELS
    assert module.MODEL_INFO["function_calling"] is True
    assert module.MODEL_INFO["json_output"] is True
    assert module.MODEL_INFO["structured_output"] is True
    assert "vision" in module.MODEL_INFO
    assert "family" in module.MODEL_INFO
    if has_base_url:
        assert module.BASE_URL.startswith("https://")
    else:
        assert not hasattr(module, "BASE_URL")
