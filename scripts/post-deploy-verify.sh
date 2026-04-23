#!/usr/bin/env bash
# Post-deploy verification for a promoted Vercel production URL.
# Usage: scripts/post-deploy-verify.sh <base-url>
#
# Checks three key flows against the deployed SvelteKit surface:
#   1. GET /                -> 2xx/3xx (homepage renders)
#   2. GET /login           -> 2xx/3xx (auth entry renders)
#   3. GET /api/suggestions -> 2xx/3xx/401/403 (API route reachable; auth-gated OK)
#
# Exits non-zero if any gate fails.
set -euo pipefail

if [ "$#" -ne 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: $0 <base-url>" >&2
  exit 2
fi

BASE="${1%/}"
FAILED=0

gate_range() {
  # Generic gate: accept any code in [200, max).
  local name="$1"
  local path="$2"
  local max="$3"
  local url="${BASE}${path}"
  local code
  code=$(curl -sS -o /dev/null -L --max-time 30 -w '%{http_code}' "$url" || echo '000')
  if [ "$code" -ge 200 ] && [ "$code" -lt "$max" ]; then
    echo "PASS $name  $url -> $code"
  else
    echo "FAIL $name  $url -> $code" >&2
    FAILED=1
  fi
}

gate_api() {
  # API reachability: accept 2xx/3xx (success/redirect) and 401/403 (auth-gated but booted).
  # Reject 404 (route missing), 405 (method wrong), 5xx (function crash), and network errors.
  local name="$1"
  local path="$2"
  local url="${BASE}${path}"
  local code
  code=$(curl -sS -o /dev/null -L --max-time 30 -w '%{http_code}' "$url" || echo '000')
  case "$code" in
    2[0-9][0-9]|3[0-9][0-9]|401|403)
      echo "PASS $name  $url -> $code"
      ;;
    *)
      echo "FAIL $name  $url -> $code (not in allow-list: 2xx/3xx/401/403)" >&2
      FAILED=1
      ;;
  esac
}

echo "Post-deploy verification against $BASE"
gate_range "home"      "/"                 "400"
gate_range "login"     "/login"            "400"
gate_api   "api-reach" "/api/suggestions"

if [ "$FAILED" -ne 0 ]; then
  echo "Post-deploy verification FAILED" >&2
  exit 1
fi
echo "Post-deploy verification PASSED"
