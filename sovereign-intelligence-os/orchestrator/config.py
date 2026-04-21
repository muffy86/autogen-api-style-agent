from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SOVEREIGN_", env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8000
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    memory_path: Path = Field(default=Path("~/.sovereign-os/memory"))
    identity_path: Path = Field(default=Path("~/.sovereign-os/identity.md"))

    default_model: str = "ollama/llama3.2"
    trigger_token: str = "change-me-to-a-long-random-value"
    mcp_servers_config: Path = Field(default=Path("./configs/mcp_servers.json"))

    @field_validator("memory_path", "identity_path", "mcp_servers_config", mode="after")
    @classmethod
    def _expand(cls, value: Path) -> Path:
        return value.expanduser()


settings = Settings()
settings.memory_path.mkdir(parents=True, exist_ok=True)
settings.identity_path.parent.mkdir(parents=True, exist_ok=True)
