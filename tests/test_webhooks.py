from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import autogen_api_agent.webhooks as webhooks_module
from autogen_api_agent.config import AppConfig


class _FakeFactory:
    def __init__(self, config: AppConfig):
        self.config = config


@pytest.fixture(autouse=True)
def clear_webhook_jobs() -> None:
    webhooks_module._webhook_jobs.clear()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    app = FastAPI()
    app.include_router(webhooks_module.router)
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)
    monkeypatch.setattr(webhooks_module, "get_config", lambda: AppConfig(_env_file=None))
    monkeypatch.setattr(webhooks_module, "ModelClientFactory", _FakeFactory)
    monkeypatch.setattr(webhooks_module, "_run_webhook_agent", lambda *args, **kwargs: None)

    with TestClient(app) as test_client:
        yield test_client


def test_verify_signature_passes_with_no_secret_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_WEBHOOK_SECRET", raising=False)

    webhooks_module._verify_signature(b"{}", None)


def test_verify_signature_raises_401_with_invalid_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "top-secret")

    with pytest.raises(HTTPException) as exc_info:
        webhooks_module._verify_signature(b"payload", "sha256=bad")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid signature"


def test_post_github_webhook_pull_request_event_returns_accepted_job(
    client: TestClient,
) -> None:
    response = client.post(
        "/webhooks/github",
        headers={"X-GitHub-Event": "pull_request"},
        json={
            "action": "opened",
            "pull_request": {"title": "PR", "body": "desc", "diff_url": "https://example.com/diff"},
        },
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["job_id"]


def test_post_github_webhook_issues_event_returns_accepted_job(client: TestClient) -> None:
    response = client.post(
        "/webhooks/github",
        headers={"X-GitHub-Event": "issues"},
        json={"action": "opened", "issue": {"title": "Bug", "body": "details"}},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_post_github_webhook_push_event_returns_accepted_job(client: TestClient) -> None:
    response = client.post(
        "/webhooks/github",
        headers={"X-GitHub-Event": "push"},
        json={"commits": [{"message": "feat: add thing"}]},
    )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"


def test_post_github_webhook_unknown_event_returns_ignored(client: TestClient) -> None:
    response = client.post(
        "/webhooks/github",
        headers={"X-GitHub-Event": "deployment"},
        json={"action": "created"},
    )

    assert response.status_code == 202
    assert response.json() == {"status": "ignored", "event": "deployment"}


def test_get_webhook_job_returns_404_for_unknown_job(client: TestClient) -> None:
    response = client.get("/webhooks/jobs/missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"
