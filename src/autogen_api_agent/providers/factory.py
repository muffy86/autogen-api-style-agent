from __future__ import annotations

from typing import Literal

from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..config import AppConfig

ProviderName = Literal["openai", "together", "openrouter", "google", "kimi", "mistral"]

PROVIDER_PRIORITY: list[ProviderName] = [
    "openai",
    "google",
    "mistral",
    "together",
    "openrouter",
    "kimi",
]


class ModelClientFactory:
    """Factory that creates model clients for any supported provider."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._clients: dict[str, object] = {}

    def create(self, provider: ProviderName | None = None, model: str | None = None):
        """Create a model client for the given provider. Falls back to default."""
        provider = provider or self.config.default_provider
        pc = self.config.providers

        if provider == "openai":
            return OpenAIChatCompletionClient(
                model=model or pc.openai_model,
                api_key=pc.openai_api_key,
            )
        elif provider == "together":
            return OpenAIChatCompletionClient(
                model=model or pc.together_model,
                api_key=pc.together_api_key,
                base_url=pc.together_base_url,
                model_info={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "unknown",
                    "structured_output": True,
                },
            )
        elif provider == "openrouter":
            return OpenAIChatCompletionClient(
                model=model or pc.openrouter_model,
                api_key=pc.openrouter_api_key,
                base_url=pc.openrouter_base_url,
                model_info={
                    "vision": True,
                    "function_calling": True,
                    "json_output": True,
                    "family": "unknown",
                    "structured_output": True,
                },
            )
        elif provider == "google":
            from autogen_ext.models.gemini import GeminiChatCompletionClient

            return GeminiChatCompletionClient(
                model=model or pc.google_model,
                api_key=pc.google_api_key,
            )
        elif provider == "kimi":
            return OpenAIChatCompletionClient(
                model=model or pc.kimi_model,
                api_key=pc.moonshot_api_key,
                base_url=pc.moonshot_base_url,
                model_info={
                    "vision": True,
                    "function_calling": True,
                    "json_output": True,
                    "family": "unknown",
                    "structured_output": True,
                },
            )
        elif provider == "mistral":
            return OpenAIChatCompletionClient(
                model=model or pc.mistral_model,
                api_key=pc.mistral_api_key,
                base_url=pc.mistral_base_url,
                model_info={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "unknown",
                    "structured_output": True,
                },
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def create_best_available(self):
        """Auto-detect the best available provider and create a client.

        Priority: openai > google > mistral > together > openrouter > kimi
        """
        available = self.config.providers.available_providers()
        for p in PROVIDER_PRIORITY:
            if p in available:
                return self.create(p)
        raise RuntimeError("No LLM provider API keys found. Set at least one in .env")

    def create_fallback_chain(self, providers: list[ProviderName] | None = None) -> list:
        """Create ordered list of clients for fallback."""
        providers = providers or self.config.providers.available_providers()
        return [self.create(p) for p in providers]

    def list_available(self) -> dict[str, str]:
        """Return dict of available provider -> default model."""
        pc = self.config.providers
        result: dict[str, str] = {}
        mapping: dict[str, str] = {
            "openai": pc.openai_model,
            "together": pc.together_model,
            "openrouter": pc.openrouter_model,
            "google": pc.google_model,
            "kimi": pc.kimi_model,
            "mistral": pc.mistral_model,
        }
        for p in pc.available_providers():
            result[p] = mapping[p]
        return result
