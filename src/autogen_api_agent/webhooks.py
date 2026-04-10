"""GitHub webhook handlers for automated agent responses."""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import uuid

import httpx
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from .config import get_config
from .providers import ModelClientFactory
from .teams import create_team
from .utils import extract_final_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_webhook_jobs: dict[str, dict] = {}

_MAX_DIFF_SIZE = 50_000


def _verify_signature(body: bytes, signature: str | None) -> None:
    """Verify GitHub webhook HMAC-SHA256 signature when a secret is configured."""
    secret = os.environ.get("GITHUB_WEBHOOK_SECRET")
    if not secret:
        return
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature header")
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")


async def _fetch_diff(url: str) -> str:
    """Fetch diff content from a GitHub diff URL."""
    if not url:
        return ""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, headers={"Accept": "application/vnd.github.v3.diff"})
            resp.raise_for_status()
            diff = resp.text
            if len(diff) > _MAX_DIFF_SIZE:
                return diff[:_MAX_DIFF_SIZE] + "\n\n... [diff truncated]"
            return diff
    except Exception:
        logger.warning("Failed to fetch diff from %s", url, exc_info=True)
        return "(diff could not be fetched)"


async def _run_webhook_agent(
    job_id: str,
    team_name: str,
    factory: ModelClientFactory,
    prompt: str,
    diff_url: str | None = None,
) -> None:
    """Background task for webhook agent execution."""
    try:
        if diff_url:
            diff_content = await _fetch_diff(diff_url)
            prompt = f"{prompt}\n\nDiff:\n```diff\n{diff_content}\n```"
        team_obj = create_team(team_name, factory)
        result = await team_obj.run(task=prompt)
        _webhook_jobs[job_id] = {
            "status": "completed",
            "response": extract_final_response(result),
        }
    except Exception:
        logger.exception("Webhook agent job %s failed", job_id)
        _webhook_jobs[job_id] = {"status": "failed", "error": "Agent execution failed"}


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(...),
    x_hub_signature_256: str | None = Header(None),
):
    """Handle GitHub webhook events — trigger agent teams asynchronously.

    Returns 202 Accepted immediately with a job ID. Agent execution runs
    in the background so GitHub's 10-second delivery timeout is never hit.

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

    team_name: str | None = None
    prompt: str | None = None
    diff_url: str | None = None

    if event == "pull_request" and payload.get("action") in (
        "opened",
        "synchronize",
    ):
        pr = payload["pull_request"]
        title = pr.get("title", "")
        body_text = pr.get("body", "") or ""
        diff_url = pr.get("diff_url", "")
        prompt = f"Review this pull request:\nTitle: {title}\nDescription: {body_text}"
        team_name = "code_review"

    elif event == "issues" and payload.get("action") == "opened":
        issue = payload["issue"]
        title = issue.get("title", "")
        body_text = issue.get("body", "") or ""
        prompt = (
            "Triage this GitHub issue and suggest labels, priority, and next steps:\n"
            f"Title: {title}\n"
            f"Body: {body_text}"
        )
        team_name = "research"

    elif event == "push":
        commits = payload.get("commits", [])
        commit_msgs = [c.get("message", "") for c in commits[:5]]
        prompt = "Analyze these commits for potential breaking changes or issues:\n" + "\n".join(
            f"- {m}" for m in commit_msgs
        )
        team_name = "quick"

    if team_name and prompt:
        job_id = uuid.uuid4().hex
        _webhook_jobs[job_id] = {"status": "running"}
        background_tasks.add_task(_run_webhook_agent, job_id, team_name, factory, prompt, diff_url)
        return {"status": "accepted", "job_id": job_id}

    return {"status": "ignored", "event": event}


@router.get("/jobs/{job_id}")
async def get_webhook_job(job_id: str):
    """Poll the result of a webhook-triggered agent job."""
    job = _webhook_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}
