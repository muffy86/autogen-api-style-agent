#!/usr/bin/env bash
# Smoke-test a deployed SvelteKit URL.
# Usage: scripts/smoke-test.sh <base-url>
set -euo pipefail

if [ "$#" -ne 1 ] || [ -z "${1:-}" ]; then
  echo "Usage: $0 <base-url>" >&2
  exit 2
fi

BASE="${1%/}"
FAILED=0

check() {
  local path="$1"
  local expect="$2"
  local url="${BASE}${path}"
  local code
  code=$(curl -sS -o /dev/null -L --max-time 30 -w '%{http_code}' "$url" || echo '000')
  if [ "$code" = "$expect" ]; then
    echo "OK   $url -> $code"
  else
    echo "FAIL $url -> $code (expected $expect)" >&2
    FAILED=1
  fi
}

echo "Smoke-testing $BASE"
check "/"       "200"
check "/login"  "200"

if [ "$FAILED" -ne 0 ]; then
  echo "Smoke test FAILED" >&2
  exit 1
fi
echo "Smoke test PASSED"
