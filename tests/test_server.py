from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import autogen_api_agent.server as server_module
from autogen_api_agent.config import AppConfig, ProviderConfig


class _FakeFactory:
    def __init__(self, config: AppConfig):
        self.config = config

    def list_available(self) -> dict[str, str]:
        return {"openai": "gpt-4o", "google": "gemini-2.0-flash"}


class _FakeTeam:
    async def run(self, task: str):
        result = MagicMock()
        result.messages = [MagicMock(content="assistant response"), MagicMock(content="TERMINATE")]
        return result

    async def run_stream(self, task: str):
        yield SimpleNamespace(content="hello ")
        yield SimpleNamespace(content="world")
        yield SimpleNamespace(content="TERMINATE")


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    config = AppConfig(
        _env_file=None,
        providers=ProviderConfig(
            _env_file=None,
            OPENAI_API_KEY="sk-openai",
            GOOGLE_API_KEY="google-key",
        ),
    )
    monkeypatch.setattr(server_module, "get_config", lambda: config)
    monkeypatch.setattr(server_module, "ModelClientFactory", _FakeFactory)

    with TestClient(server_module.app) as test_client:
        yield test_client


def test_get_health_returns_status_providers_and_teams(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "providers": {"openai": "gpt-4o", "google": "gemini-2.0-flash"},
        "teams": ["productivity", "code_review", "research", "quick"],
    }


def test_get_models_returns_model_list(client: TestClient) -> None:
    response = client.get("/v1/models")

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert {item["id"] for item in data["data"]} == {
        "openai/gpt-4o",
        "google/gemini-2.0-flash",
    }


def test_get_providers_returns_provider_dict(client: TestClient) -> None:
    response = client.get("/v1/providers")

    assert response.status_code == 200
    assert response.json() == {"providers": {"openai": "gpt-4o", "google": "gemini-2.0-flash"}}


def test_get_teams_returns_team_list_with_four_entries(client: TestClient) -> None:
    response = client.get("/v1/teams")

    assert response.status_code == 200
    assert len(response.json()["teams"]) == 4


def test_post_chat_completions_returns_response(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(server_module, "create_team", lambda *args, **kwargs: _FakeTeam())

    response = client.post(
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Solve this"}]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["choices"][0]["message"] == {"role": "assistant", "content": "assistant response"}


def test_post_chat_completions_stream_returns_sse(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(server_module, "create_team", lambda *args, **kwargs: _FakeTeam())

    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "Stream this"}], "stream": True},
    ) as response:
        body = "".join(response.iter_text())

    assert response.status_code == 200
    assert "chat.completion.chunk" in body
    assert '"content": "hello"' in body
    assert "world" in body
    assert "[DONE]" in body


def test_get_session_returns_404_for_unknown_session(client: TestClient) -> None:
    response = client.get("/v1/sessions/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
