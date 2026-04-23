#!/usr/bin/env bash
# post-deploy-verify.sh — verify a deployed URL after a release.
# Usage:
#   DEPLOY_URL=https://example.vercel.app bash scripts/post-deploy-verify.sh
# Exit codes: 0 = verified, non-zero = failure.

set -euo pipefail

DEPLOY_URL="${DEPLOY_URL:-${VERCEL_URL:-}}"
TIMEOUT="${POST_DEPLOY_TIMEOUT:-30}"
RETRIES="${POST_DEPLOY_RETRIES:-5}"
RETRY_DELAY="${POST_DEPLOY_RETRY_DELAY:-6}"

if [ -z "$DEPLOY_URL" ]; then
  echo "[error] DEPLOY_URL (or VERCEL_URL) is not set." >&2
  exit 2
fi

# Normalize — strip trailing slash, ensure scheme.
DEPLOY_URL="${DEPLOY_URL%/}"
if [[ "$DEPLOY_URL" != http*://* ]]; then
  DEPLOY_URL="https://$DEPLOY_URL"
fi

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
NC=$'\033[0m'

failures=0

log_ok() { printf "${GREEN}[ok]${NC} %s\n" "$1"; }
log_fail() { printf "${RED}[fail]${NC} %s\n" "$1"; failures=$((failures + 1)); }

check_with_retry() {
  local label="$1"
  local url="$2"
  local expected_status="${3:-200}"
  local body_grep="${4:-}"

  local attempt=1
  while [ "$attempt" -le "$RETRIES" ]; do
    local status
    status=$(curl -sS --max-time "$TIMEOUT" -o /tmp/pdv_body -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    if [ "$status" = "$expected_status" ]; then
      if [ -n "$body_grep" ] && ! grep -q "$body_grep" /tmp/pdv_body; then
        log_fail "$label — $url [$status] body missing '$body_grep'"
        return
      fi
      log_ok "$label — $url [$status]"
      return
    fi
    if [ "$attempt" -lt "$RETRIES" ]; then
      printf "  retry %d/%d — %s returned %s, waiting %ss...\n" "$attempt" "$RETRIES" "$url" "$status" "$RETRY_DELAY"
      sleep "$RETRY_DELAY"
    fi
    attempt=$((attempt + 1))
  done
  log_fail "$label — $url never returned $expected_status after $RETRIES attempts"
}

printf "Post-deploy verification — %s\n\n" "$DEPLOY_URL"

# Frontend root must render.
check_with_retry "homepage" "$DEPLOY_URL/" 200 "<html"

# Login page must render (key route).
check_with_retry "login page" "$DEPLOY_URL/login" 200

rm -f /tmp/pdv_body

printf "\n"
if [ "$failures" -gt 0 ]; then
  printf "${RED}Post-deploy verification failed: %d check(s) failed.${NC}\n" "$failures"
  exit 1
fi
printf "${GREEN}Deployment verified.${NC}\n"
