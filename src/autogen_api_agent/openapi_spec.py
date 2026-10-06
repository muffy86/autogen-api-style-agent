"""OpenAPI 3.0 Specification for Autogen API Style Agent."""

_spec = {
    "openapi": "3.0.3",
    "info": {
        "title": "Autogen API Style Agent",
        "description": "Multi-agent AI system: A2A + MCP + Zero Trust + Local Web",
        "version": "0.2.0",
    },
    "servers": [{"url": "http://localhost:8000"}],
    "paths": {
        "/health": {"get": {"tags": ["System"], "responses": {"200": {"description": "OK"}}}},
        "/v1/chat/completions": {
            "post": {"tags": ["OpenAI"], "responses": {"200": {"description": "OK"}}}
        },
        "/v1/agent/chat": {
            "post": {"tags": ["Multi-Agent"], "responses": {"200": {"description": "OK"}}}
        },
        "/v1/providers": {
            "get": {"tags": ["Providers"], "responses": {"200": {"description": "OK"}}}
        },
        "/v1/teams": {"get": {"tags": ["Teams"], "responses": {"200": {"description": "OK"}}}},
        "/mcp/tools": {"get": {"tags": ["MCP"], "responses": {"200": {"description": "OK"}}}},
        "/a2a": {"post": {"tags": ["A2A"], "responses": {"200": {"description": "OK"}}}},
        "/gateway/health": {
            "get": {"tags": ["Gateway"], "responses": {"200": {"description": "OK"}}}
        },
        "/security/approvals": {
            "get": {"tags": ["Security"], "responses": {"200": {"description": "OK"}}}
        },
        "/swiss/providers": {
            "get": {"tags": ["Swiss AI"], "responses": {"200": {"description": "OK"}}}
        },
        "/composable/tools": {
            "get": {"tags": ["Composable"], "responses": {"200": {"description": "OK"}}}
        },
        "/extensions": {
            "get": {"tags": ["Extensions"], "responses": {"200": {"description": "OK"}}}
        },
        "/local/node": {
            "get": {"tags": ["Local Web"], "responses": {"200": {"description": "OK"}}}
        },
    },
    "tags": [
        {"name": "System", "description": "System health"},
        {"name": "OpenAI", "description": "OpenAI-compatible"},
        {"name": "Multi-Agent", "description": "Agent teams"},
        {"name": "Providers", "description": "LLM providers"},
        {"name": "Teams", "description": "Agent teams"},
        {"name": "MCP", "description": "Model Context Protocol"},
        {"name": "A2A", "description": "Agent-to-Agent"},
        {"name": "Gateway", "description": "MCP Gateway"},
        {"name": "Security", "description": "Zero Trust"},
        {"name": "Swiss AI", "description": "Swiss AI Ecosystem"},
        {"name": "Composable", "description": "Composable Tools"},
        {"name": "Extensions", "description": "UI Extensions"},
        {"name": "Local Web", "description": "P2P Network"},
    ],
}

OPENAPI_SPEC = _spec


def get_spec():
    return OPENAPI_SPEC
