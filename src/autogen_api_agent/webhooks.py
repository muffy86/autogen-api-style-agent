"""GitHub webhook handlers for automated agent responses."""
from __future__ import annotations

import hashlib
import hmac
import logging
import os

from fastapi import APIRouter, Header, HTTPException, Request

from .config import get_config
from .providers import ModelClientFactory
from .teams import create_team
from .utils import extract_final_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _verify_signature(body: bytes, signature: str | None) -> None:
    """Verify GitHub webhook HMAC-SHA256 signature when a secret is configured."""
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature header")
    expected = "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str | None = Header(None),
):
    """Handle GitHub webhook events — trigger agent teams automatically.

    Supported events:
    - ``pull_request`` (opened / synchronize): auto-review with code_review team
    - ``issues`` (opened): auto-triage with research team
    - ``push``: analyse recent commits with quick agent
    """
    body = await request.body()
    _verify_signature(body, x_hub_signature_256)

    payload = await request.json()
    event = x_github_event

    config = get_config()
    factory = ModelClientFactory(config)

    try:
        if event == "pull_request" and payload.get("action") in (
            "opened",
            "synchronize",
        ):
            pr = payload["pull_request"]
            title = pr.get("title", "")
            body_text = pr.get("body", "") or ""
            diff_url = pr.get("diff_url", "")
            prompt = (
                f"Review this pull request:\n"
                f"Title: {title}\n"
                f"Description: {body_text}\n"
                f"Diff URL: {diff_url}"
            )
            team_obj = create_team("code_review", factory)
            result = await team_obj.run(task=prompt)
            return {"status": "reviewed", "response": extract_final_response(result)}

        if event == "issues" and payload.get("action") == "opened":
            issue = payload["issue"]
            title = issue.get("title", "")
            body_text = issue.get("body", "") or ""
            prompt = (
                "Triage this GitHub issue and suggest labels, priority, and next steps:\n"
                f"Title: {title}\n"
                f"Body: {body_text}"
            )
            team_obj = create_team("research", factory)
            result = await team_obj.run(task=prompt)
            return {"status": "triaged", "response": extract_final_response(result)}

        if event == "push":
            commits = payload.get("commits", [])
            commit_msgs = [c.get("message", "") for c in commits[:5]]
            prompt = (
                "Analyze these commits for potential breaking changes or issues:\n"
                + "\n".join(f"- {m}" for m in commit_msgs)
            )
            team_obj = create_team("quick", factory)
            result = await team_obj.run(task=prompt)
            return {"status": "analyzed", "response": extract_final_response(result)}

    except Exception:
        logger.exception("Webhook handler error for event=%s", event)
        raise HTTPException(status_code=500, detail="Agent execution failed") from None

    return {"status": "ignored", "event": event}
