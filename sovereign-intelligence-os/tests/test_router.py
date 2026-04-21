import pytest

from orchestrator.router import LLMRouter


@pytest.mark.asyncio
async def test_router_complete_success(monkeypatch):
    async def fake_acompletion(*, model, messages):
        assert model == "fake-model"
        assert messages[-1]["content"] == "hello"
        return {
            "model": "fake-model",
            "choices": [{"message": {"content": "world"}}],
        }

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)
    router = LLMRouter(default_model="fake-model")

    result = await router.complete(user_message="hello")

    assert result == {"ok": True, "model": "fake-model", "content": "world"}


@pytest.mark.asyncio
async def test_router_complete_exception(monkeypatch):
    async def fake_acompletion(*, model, messages):
        raise RuntimeError("boom")

    monkeypatch.setattr("orchestrator.router.litellm.acompletion", fake_acompletion)
    router = LLMRouter(default_model="fake-model")

    result = await router.complete(user_message="hello")

    assert result["ok"] is False
    assert result["content"] == ""
    assert "boom" in result["error"]
