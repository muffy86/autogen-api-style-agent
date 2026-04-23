#!/usr/bin/env bash
# Rollback to a previous Vercel production deployment.
#
# Usage: scripts/rollback.sh <previous-deployment-url-or-id>
#
# Requires: VERCEL_TOKEN (env), vercel CLI on PATH.
# Optional:  GH_TOKEN/GITHUB_TOKEN + GITHUB_REPOSITORY + COMMIT_SHA for posting
#            a rollback notice as a commit comment.
#
# Exits non-zero on any failure.
set -euo pipefail

if [ "$#" -ne 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: $0 <previous-deployment-url-or-id>" >&2
  exit 2
fi

PREV="$1"

if [ -z "${VERCEL_TOKEN:-}" ]; then
  echo "ERROR: VERCEL_TOKEN is not set" >&2
  exit 1
fi

if ! command -v vercel >/dev/null 2>&1; then
  echo "ERROR: vercel CLI not found on PATH" >&2
  exit 1
fi

echo "Rolling back production to: $PREV"

# `vercel promote` re-promotes an existing deployment to production without
# rebuilding. This is the canonical rollback path.
if ! vercel promote "$PREV" --token="$VERCEL_TOKEN" --yes; then
  echo "ERROR: vercel promote failed" >&2
  exit 1
fi

echo "Rollback succeeded: $PREV is now production."

# Best-effort commit comment. Never fails the rollback itself.
if command -v gh >/dev/null 2>&1 \
   && [ -n "${GITHUB_REPOSITORY:-}" ] \
   && [ -n "${COMMIT_SHA:-}" ] \
   && { [ -n "${GH_TOKEN:-}" ] || [ -n "${GITHUB_TOKEN:-}" ]; }; then
  body="Automated rollback: production promoted back to \`$PREV\` after post-deploy verification failed on this commit."
  if gh api \
      --method POST \
      "repos/$GITHUB_REPOSITORY/commits/$COMMIT_SHA/comments" \
      -f body="$body" >/dev/null 2>&1; then
    echo "Posted rollback notice to commit $COMMIT_SHA."
  else
    echo "WARN: failed to post commit comment (continuing)."
  fi
else
  echo "Skipping commit comment (missing gh CLI, GITHUB_REPOSITORY, COMMIT_SHA, or token)."
fi
