from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from .config import settings
from .identity import build_system_prompt, load_identity
from .mcp_bridge import MCPServer, load_mcp_config
from .memory import ForeverMemory
from .router import LLMRouter

log = logging.getLogger("sovereign")
logging.basicConfig(level=settings.log_level)


class TriggerPayload(BaseModel):
    query: str = Field(..., min_length=1, max_length=10_000)
    gesture: str | None = None
    context: str | None = None
    model: str | None = None


class TriggerResponse(BaseModel):
    ok: bool
    model: str | None = None
    content: str = ""
    memory_id: str | None = None
    error: str | None = None


state: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    state["memory"] = ForeverMemory(settings.memory_path)
    state["identity"] = load_identity(settings.identity_path)
    state["router"] = LLMRouter(default_model=settings.default_model)
    state["mcp_servers"] = load_mcp_config(settings.mcp_servers_config)
    log.info(
        "Sovereign OS ready: memory_entries=%s identity_loaded=%s mcp_servers=%s",
        state["memory"].count(),
        bool(state["identity"]),
        [server.name for server in state["mcp_servers"]],
    )
    yield
    state.clear()


app = FastAPI(title="Sovereign Intelligence OS", version="2026.5.0", lifespan=lifespan)


def _verify_token(x_sovereign_token: Annotated[str | None, Header()] = None) -> None:
    if x_sovereign_token != settings.trigger_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="bad token",
        )


@app.get("/health")
async def health() -> dict[str, Any]:
    memory: ForeverMemory = state["memory"]
    return {
        "ok": True,
        "version": "2026.5.0",
        "memory_entries": memory.count(),
        "identity_loaded": bool(state["identity"]),
    }


@app.get("/mcp/status")
async def mcp_status() -> dict[str, Any]:
    servers: list[MCPServer] = state["mcp_servers"]
    return {"servers": [server.name for server in servers], "count": len(servers)}


@app.post("/trigger", response_model=TriggerResponse, dependencies=[Depends(_verify_token)])
async def trigger(payload: TriggerPayload) -> TriggerResponse:
    memory: ForeverMemory = state["memory"]
    router: LLMRouter = state["router"]
    identity: str = state["identity"]

    system = build_system_prompt(identity)
    recall = memory.query(payload.query, n_results=3)
    recall_text = "\n".join(f"- {item['document']}" for item in recall)
    user_msg = (
        payload.query if not recall_text else f"{payload.query}\n\nRelevant memory:\n{recall_text}"
    )

    result = await router.complete(
        user_message=user_msg,
        system_prompt=system,
        model=payload.model,
    )

    memory_id = None
    if result.get("ok"):
        memory_id = memory.add(
            document=f"Q: {payload.query}\nA: {result['content']}",
            metadata={
                "gesture": payload.gesture or "",
                "context": payload.context or "",
            },
        )

    return TriggerResponse(
        ok=bool(result.get("ok")),
        model=result.get("model"),
        content=result.get("content", ""),
        memory_id=memory_id,
        error=result.get("error"),
    )


@app.post("/memory/add", dependencies=[Depends(_verify_token)])
async def memory_add(doc: dict[str, Any]) -> dict[str, Any]:
    memory: ForeverMemory = state["memory"]
    text = str(doc.get("document", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="document required")
    memory_id = memory.add(text, metadata=doc.get("metadata") or {})
    return {"ok": True, "id": memory_id}


@app.get("/memory/query")
async def memory_query(q: str, n: int = 5) -> dict[str, Any]:
    memory: ForeverMemory = state["memory"]
    return {"results": memory.query(q, n_results=n)}
