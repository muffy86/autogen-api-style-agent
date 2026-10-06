from fastapi.testclient import TestClient


def test_health_returns_200(load_module):
    main = load_module("orchestrator.main")

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["memory_entries"] == 0


def test_trigger_requires_token(load_module):
    main = load_module("orchestrator.main")

    with TestClient(main.app) as client:
        response = client.post("/trigger", json={"query": "hello"})

    assert response.status_code == 401


def test_memory_query_requires_token(load_module):
    main = load_module("orchestrator.main")

    with TestClient(main.app) as client:
        response = client.get("/memory/query", params={"q": "hello", "n": 5})

    assert response.status_code == 401


def test_trigger_and_memory_query_end_to_end(load_module, monkeypatch):
    main = load_module("orchestrator.main")

    async def fake_acompletion(*, model, messages, timeout):
        return {
            "model": model,
            "choices": [{"message": {"content": f"echo::{messages[-1]['content']}"}}],
        }

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)

    with TestClient(main.app) as client:
        trigger = client.post(
            "/trigger",
            json={"query": "store this", "gesture": "tap", "context": "test"},
            headers={"x-sovereign-token": "test-token"},
        )
        query = client.get(
            "/memory/query",
            params={"q": "store this", "n": 5},
            headers={"x-sovereign-token": "test-token"},
        )

    assert trigger.status_code == 200
    trigger_payload = trigger.json()
    assert trigger_payload["ok"] is True
    assert trigger_payload["memory_id"]
    assert "echo::store this" in trigger_payload["content"]

    assert query.status_code == 200
    results = query.json()["results"]
    assert results
    assert any("Q: store this" in item["document"] for item in results)
