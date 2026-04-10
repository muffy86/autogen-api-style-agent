"""FastAPI HTTP server — OpenAI-compatible chat completions with SSE streaming."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .config import get_config
from .models import (
    ChatChoice,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    StreamChoice,
    StreamDelta,
)
from .providers import ModelClientFactory
from .session import SessionManager
from .teams import create_team
from .utils import extract_final_response, extract_message_text, format_task
from .webhooks import router as webhook_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup, cleanup on shutdown."""
    config = get_config()
    app.state.config = config
    app.state.factory = ModelClientFactory(config)
    app.state.sessions = SessionManager(ttl_minutes=config.session_ttl_minutes)

    async def _cleanup_loop() -> None:
        while True:
            await asyncio.sleep(300)
            count = await app.state.sessions.cleanup_expired()
            if count:
                logger.info("Cleaned up %d expired sessions", count)

    cleanup_task = asyncio.create_task(_cleanup_loop())
    yield
    cleanup_task.cancel()
    with suppress(asyncio.CancelledError):
        await cleanup_task
    await app.state.sessions.cleanup_all()


app = FastAPI(
    title="AutoGen API Style Agent",
    description="Multi-agent productivity system with OpenAI-compatible API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)


# ---------------------------------------------------------------------------
# Health / discovery endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
async def health():
    """Health check with provider status."""
    factory: ModelClientFactory = app.state.factory
    return {
        "status": "healthy",
        "providers": factory.list_available(),
        "teams": ["productivity", "code_review", "research", "quick"],
    }


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)."""
    factory: ModelClientFactory = app.state.factory
    available = factory.list_available()
    models = []
    for provider, model in available.items():
        models.append(
            {
                "id": f"{provider}/{model}",
                "object": "model",
                "created": int(time.time()),
                "owned_by": provider,
            }
        )
    return {"object": "list", "data": models}


# ---------------------------------------------------------------------------
# Chat completions (OpenAI-compatible)
# ---------------------------------------------------------------------------


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """Main chat endpoint — OpenAI-compatible."""
    factory: ModelClientFactory = app.state.factory
    sessions: SessionManager = app.state.sessions

    session = await sessions.get_or_create(request.session_id)

    task = format_task(request.messages)
    user_msg = request.messages[-1].content if request.messages else ""
    session.add_message("user", user_msg)

    try:
        provider = None
        model = None
        if request.model and request.model != "auto" and "/" in request.model:
            provider, model = request.model.split("/", 1)
        team_obj = create_team(
            team_name=request.team,
            factory=factory,
            provider=provider,
            model=model,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Team creation failed: {exc}") from exc

    if request.stream:
        return EventSourceResponse(
            _stream_response(team_obj, task, request.model, session),
            media_type="text/event-stream",
        )

    try:
        result = await team_obj.run(task=task)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    assistant_content = extract_final_response(result)
    session.add_message("assistant", assistant_content)

    return ChatCompletionResponse(
        model=request.model,
        choices=[ChatChoice(message=ChatMessage(role="assistant", content=assistant_content))],
    )


async def _stream_response(team, task: str, model: str, session) -> AsyncGenerator[str, None]:
    """Stream team execution as SSE chunks."""
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())
    full_content = ""
    try:
        yield json.dumps(
            ChatCompletionChunk(
                id=chunk_id,
                created=created,
                model=model,
                choices=[StreamChoice(delta=StreamDelta(role="assistant"))],
            ).model_dump()
        )

        async for message in team.run_stream(task=task):
            text = extract_message_text(message)
            if text:
                full_content += text
                yield json.dumps(
                    ChatCompletionChunk(
                        id=chunk_id,
                        created=created,
                        model=model,
                        choices=[StreamChoice(delta=StreamDelta(content=text))],
                    ).model_dump()
                )

        yield json.dumps(
            ChatCompletionChunk(
                id=chunk_id,
                created=created,
                model=model,
                choices=[StreamChoice(delta=StreamDelta(), finish_reason="stop")],
            ).model_dump()
        )
        yield "[DONE]"
    finally:
        if full_content:
            session.add_message("assistant", full_content)


# ---------------------------------------------------------------------------
# Provider / team / session management
# ---------------------------------------------------------------------------


@app.get("/v1/providers")
async def list_providers():
    """List configured providers and their status."""
    factory: ModelClientFactory = app.state.factory
    return {"providers": factory.list_available()}


@app.get("/v1/teams")
async def list_teams():
    """List available agent teams."""
    return {
        "teams": [
            {
                "name": "productivity",
                "agents": 8,
                "description": "Full 8-agent productivity team",
            },
            {
                "name": "code_review",
                "agents": 3,
                "description": "Focused code review (coder + reviewer + architect)",
            },
            {
                "name": "research",
                "agents": 3,
                "description": "Research and synthesis (researcher + writer + architect)",
            },
            {
                "name": "quick",
                "agents": 1,
                "description": "Single agent with all tools",
            },
        ]
    }


@app.get("/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session history."""
    sessions: SessionManager = app.state.sessions
    session = await sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.session_id, "history": session.history}


def create_app() -> FastAPI:
    """Factory function for the FastAPI app."""
    return app
