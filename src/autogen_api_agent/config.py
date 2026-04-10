from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseSettings):
    """Individual provider settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="", extra="ignore"
    )

    # OpenAI
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o", alias="OPENAI_MODEL")

    # Together.ai
    together_api_key: str | None = Field(None, alias="TOGETHER_API_KEY")
    together_model: str = Field("meta-llama/Llama-3.3-70B-Instruct-Turbo", alias="TOGETHER_MODEL")
    together_base_url: str = "https://api.together.xyz/v1"

    # OpenRouter
    openrouter_api_key: str | None = Field(None, alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field("openai/gpt-4o", alias="OPENROUTER_MODEL")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Google Gemini
    google_api_key: str | None = Field(None, alias="GOOGLE_API_KEY")
    google_model: str = Field("gemini-2.0-flash", alias="GOOGLE_MODEL")

    # Kimi K2.5 (Moonshot)
    moonshot_api_key: str | None = Field(None, alias="MOONSHOT_API_KEY")
    kimi_model: str = Field("kimi-k2.5", alias="KIMI_MODEL")
    moonshot_base_url: str = "https://api.moonshot.cn/v1"

    # Mistral
    mistral_api_key: str | None = Field(None, alias="MISTRAL_API_KEY")
    mistral_model: str = Field("mistral-large-latest", alias="MISTRAL_MODEL")
    mistral_base_url: str = "https://api.mistral.ai/v1"

    def available_providers(self) -> list[str]:
        """Return list of providers with valid API keys."""
        providers = []
        if self.openai_api_key:
            providers.append("openai")
        if self.together_api_key:
            providers.append("together")
        if self.openrouter_api_key:
            providers.append("openrouter")
        if self.google_api_key:
            providers.append("google")
        if self.moonshot_api_key:
            providers.append("kimi")
        if self.mistral_api_key:
            providers.append("mistral")
        return providers


class AppConfig(BaseSettings):
    """Main application config."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Agent defaults
    default_provider: str = "openai"
    default_team: str = "productivity"
    max_turns: int = 30
    timeout_seconds: int = 300

    # Session
    session_ttl_minutes: int = 60

    # Provider config (nested)
    providers: ProviderConfig = Field(default_factory=ProviderConfig)


def get_config() -> AppConfig:
    """Load config from environment."""
    return AppConfig()
