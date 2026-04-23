#!/usr/bin/env bash
# smoke-test.sh — hit local backend + frontend health endpoints.
# Usage:
#   bash scripts/smoke-test.sh
# Env:
#   SMOKE_BACKEND_URL  (default: http://localhost:8000)
#   SMOKE_FRONTEND_URL (default: http://localhost:5173)
#   SMOKE_TIMEOUT      (default: 10) — per-request timeout in seconds
# Exit codes: 0 = all checks passed, non-zero = at least one failed.

set -euo pipefail

BACKEND_URL="${SMOKE_BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${SMOKE_FRONTEND_URL:-http://localhost:5173}"
TIMEOUT="${SMOKE_TIMEOUT:-10}"

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
NC=$'\033[0m'

failures=0

log_ok() { printf "${GREEN}[ok]${NC} %s\n" "$1"; }
log_fail() { printf "${RED}[fail]${NC} %s\n" "$1"; failures=$((failures + 1)); }
log_skip() { printf "${YELLOW}[skip]${NC} %s\n" "$1"; }

check_http() {
  local label="$1"
  local url="$2"
  local expected_status="${3:-200}"
  local body_grep="${4:-}"

  local status body
  if ! body=$(curl -sS --max-time "$TIMEOUT" -o /tmp/smoke_body -w "%{http_code}" "$url" 2>/dev/null); then
    log_fail "$label — request failed for $url"
    return
  fi
  status="$body"
  if [ "$status" != "$expected_status" ]; then
    log_fail "$label — $url returned $status (expected $expected_status)"
    return
  fi
  if [ -n "$body_grep" ]; then
    if ! grep -q "$body_grep" /tmp/smoke_body; then
      log_fail "$label — $url body missing expected content '$body_grep'"
      return
    fi
  fi
  log_ok "$label — $url [$status]"
}

printf "Smoke test — backend=%s frontend=%s timeout=%ss\n\n" "$BACKEND_URL" "$FRONTEND_URL" "$TIMEOUT"

# ─── Backend (Python FastAPI) ──────────────────────────────────────────────
if curl -sS --max-time 2 -o /dev/null -w "%{http_code}" "$BACKEND_URL" >/dev/null 2>&1; then
  check_http "backend /health"    "$BACKEND_URL/health"    200 '"status"'
  check_http "backend /v1/models" "$BACKEND_URL/v1/models" 200 '"object"'
else
  log_skip "backend not reachable at $BACKEND_URL — skipping backend checks"
fi

# ─── Frontend (SvelteKit) ──────────────────────────────────────────────────
if curl -sS --max-time 2 -o /dev/null -w "%{http_code}" "$FRONTEND_URL" >/dev/null 2>&1; then
  check_http "frontend /"       "$FRONTEND_URL/"       200
  check_http "frontend /login"  "$FRONTEND_URL/login"  200
else
  log_skip "frontend not reachable at $FRONTEND_URL — skipping frontend checks"
fi

rm -f /tmp/smoke_body

printf "\n"
if [ "$failures" -gt 0 ]; then
  printf "${RED}Smoke test failed: %d check(s) failed.${NC}\n" "$failures"
  exit 1
fi
printf "${GREEN}All smoke checks passed.${NC}\n"
