import asyncio

import pytest

from orchestrator.router import LLMRouter


@pytest.mark.asyncio
async def test_router_complete_success(monkeypatch):
    async def fake_acompletion(*, model, messages, timeout):
        assert model == "fake-model"
        assert messages[-1]["content"] == "hello"
        assert timeout == 12.5
        return {
            "model": "fake-model",
            "choices": [{"message": {"content": "world"}}],
        }

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)
    router = LLMRouter(default_model="fake-model", timeout=12.5)

    result = await router.complete(user_message="hello")

    assert result == {"ok": True, "model": "fake-model", "content": "world"}


@pytest.mark.asyncio
async def test_router_complete_exception(monkeypatch):
    async def fake_acompletion(*, model, messages, timeout):
        raise RuntimeError("boom")

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)
    router = LLMRouter(default_model="fake-model")

    result = await router.complete(user_message="hello")

    assert result["ok"] is False
    assert result["content"] == ""
    assert "boom" in result["error"]


@pytest.mark.asyncio
async def test_router_complete_timeout(monkeypatch):
    async def fake_acompletion(*, model, messages, timeout):
        raise asyncio.TimeoutError("timed out")

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)
    router = LLMRouter(default_model="fake-model", timeout=3.0)

    result = await router.complete(user_message="hello")

    assert result["ok"] is False
    assert result["content"] == ""
    assert "timed out" in result["error"]
