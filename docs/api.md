# HTTP API reference

Base URL examples below assume the server is running at `http://localhost:8000`.

## `GET /health`

Health check that reports server readiness, configured providers, and built-in teams.

### Response example

```json
{
  "status": "healthy",
  "providers": {
    "openai": "gpt-4.1-mini",
    "google": "gemini-2.5-flash"
  },
  "teams": [
    "productivity",
    "code_review",
    "research",
    "quick"
  ]
}
```

### curl

```bash
curl http://localhost:8000/health
```

## `GET /v1/models`

OpenAI-compatible model discovery endpoint. The response lists currently available provider/model pairs.

### Response example

```json
{
  "object": "list",
  "data": [
    {
      "id": "openai/gpt-4.1-mini",
      "object": "model",
      "created": 1712836800,
      "owned_by": "openai"
    },
    {
      "id": "google/gemini-2.5-flash",
      "object": "model",
      "created": 1712836800,
      "owned_by": "google"
    }
  ]
}
```

### curl

```bash
curl http://localhost:8000/v1/models
```

## `GET /v1/providers`

Lists configured providers and the default model name for each available provider.

### Response example

```json
{
  "providers": {
    "openai": "gpt-4.1-mini",
    "mistral": "mistral-small-latest"
  }
}
```

### curl

```bash
curl http://localhost:8000/v1/providers
```

## `GET /v1/teams`

Lists the built-in agent team presets exposed by `create_team()`.

### Response example

```json
{
  "teams": [
    {
      "name": "productivity",
      "agents": 8,
      "description": "Full 8-agent productivity team"
    },
    {
      "name": "code_review",
      "agents": 3,
      "description": "Focused code review (coder + reviewer + architect)"
    },
    {
      "name": "research",
      "agents": 3,
      "description": "Research and synthesis (researcher + writer + architect)"
    },
    {
      "name": "quick",
      "agents": 1,
      "description": "Single agent with all tools"
    }
  ]
}
```

### curl

```bash
curl http://localhost:8000/v1/teams
```

## `POST /v1/chat/completions`

Main OpenAI-style chat endpoint. The request body is defined by `ChatCompletionRequest`.

### Request schema

```json
{
  "messages": [
    {
      "role": "system | user | assistant",
      "content": "string"
    }
  ],
  "model": "auto",
  "team": "productivity",
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1024,
  "session_id": "optional-session-id"
}
```

### Non-streaming request example

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Write a FastAPI hello-world example."
    }
  ],
  "model": "auto",
  "team": "quick",
  "stream": false,
  "session_id": "demo-session-001"
}
```

### Non-streaming response example

The response body matches `ChatCompletionResponse`, with `choices[].message` matching `ChatMessage` and `usage` matching `Usage`.

```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1712836800,
  "model": "auto",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "from fastapi import FastAPI\\n\\napp = FastAPI()\\n\\n@app.get(\"/\")\\ndef hello():\\n    return {\"message\": \"hello\"}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### curl

```bash
curl -X POST http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"Write a FastAPI hello-world example."}],"team":"quick","model":"auto","stream":false,"session_id":"demo-session-001"}'
```

### Streaming request example

Set `"stream": true` to receive Server-Sent Events.

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Research AutoGen vs CrewAI."
    }
  ],
  "model": "auto",
  "team": "research",
  "stream": true,
  "session_id": "research-session-001"
}
```

### Streaming response example

Each SSE `data:` payload is a `ChatCompletionChunk`. The first chunk announces the assistant role, content chunks follow, then the final chunk includes `finish_reason: "stop"`, and the stream ends with `[DONE]`.

```text
data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1712836800,"model":"auto","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1712836800,"model":"auto","choices":[{"index":0,"delta":{"content":"AutoGen emphasizes ..."},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1712836800,"model":"auto","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### curl

```bash
curl -N -X POST http://localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"Research AutoGen vs CrewAI."}],"team":"research","model":"auto","stream":true,"session_id":"research-session-001"}'
```

## `GET /v1/sessions/{session_id}`

Returns the stored message history for an active, non-expired session.

### Response example

```json
{
  "session_id": "demo-session-001",
  "history": [
    {
      "role": "user",
      "content": "Write a FastAPI hello-world example."
    },
    {
      "role": "assistant",
      "content": "from fastapi import FastAPI\\n\\napp = FastAPI()\\n\\n@app.get(\"/\")\\ndef hello():\\n    return {\"message\": \"hello\"}"
    }
  ]
}
```

### Not found response

```json
{
  "detail": "Session not found"
}
```

### curl

```bash
curl http://localhost:8000/v1/sessions/demo-session-001
```

## `POST /github-webhook`

The current FastAPI router mounts the GitHub webhook handler at `POST /webhooks/github`. If you previously used `/github-webhook`, update clients to the mounted route.

This endpoint verifies `X-Hub-Signature-256` when `GITHUB_WEBHOOK_SECRET` is configured, accepts supported GitHub events, and returns immediately while agent execution continues in a background job.

### Required headers

- `X-GitHub-Event`
- `X-Hub-Signature-256` when webhook signature verification is enabled

### Pull request request example

```json
{
  "action": "opened",
  "pull_request": {
    "title": "Add session persistence",
    "body": "Implements Redis-backed session storage.",
    "diff_url": "https://github.com/example/repo/pull/123.diff"
  }
}
```

### Accepted response example

```json
{
  "status": "accepted",
  "job_id": "4f39d4ce4f414ee6a6f7f5f6df7c0a7f"
}
```

### Ignored response example

```json
{
  "status": "ignored",
  "event": "ping"
}
```

### curl

```bash
curl -X POST http://localhost:8000/webhooks/github -H 'Content-Type: application/json' -H 'X-GitHub-Event: pull_request' -d '{"action":"opened","pull_request":{"title":"Add session persistence","body":"Implements Redis-backed session storage.","diff_url":"https://github.com/example/repo/pull/123.diff"}}'
```

## `GET /webhooks/jobs/{job_id}`

Polls the status of a previously accepted webhook job.

### Response examples

```json
{
  "job_id": "4f39d4ce4f414ee6a6f7f5f6df7c0a7f",
  "status": "running"
}
```

```json
{
  "job_id": "4f39d4ce4f414ee6a6f7f5f6df7c0a7f",
  "status": "completed",
  "response": "The pull request introduces ..."
}
```

```json
{
  "job_id": "4f39d4ce4f414ee6a6f7f5f6df7c0a7f",
  "status": "failed",
  "error": "Agent execution failed"
}
```

### Not found response

```json
{
  "detail": "Job not found"
}
```

### curl

```bash
curl http://localhost:8000/webhooks/jobs/4f39d4ce4f414ee6a6f7f5f6df7c0a7f
```
