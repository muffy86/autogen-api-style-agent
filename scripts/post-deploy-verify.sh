#!/usr/bin/env bash
# Post-deploy verification for a promoted Vercel production URL.
# Usage: scripts/post-deploy-verify.sh <base-url>
#
# Checks three key flows against the deployed SvelteKit surface:
#   1. GET /       -> 200 (homepage renders)
#   2. GET /login  -> 200 (auth entry renders)
#   3. GET /api/suggestions -> 2xx/3xx (API route reachable)
#
# Exits non-zero if any gate fails.
set -euo pipefail

if [ "$#" -ne 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: $0 <base-url>" >&2
  exit 2
fi

BASE="${1%/}"
FAILED=0

gate() {
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

echo "Post-deploy verification against $BASE"
gate "home"         "/"                 "400"
gate "login"        "/login"            "400"
gate "api-reach"    "/api/suggestions"  "500"

if [ "$FAILED" -ne 0 ]; then
  echo "Post-deploy verification FAILED" >&2
  exit 1
fi
echo "Post-deploy verification PASSED"
