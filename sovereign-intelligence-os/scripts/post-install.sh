#!/usr/bin/env bash
# Post-install calibration: verify endpoints, seed memory, print status.
set -euo pipefail

HOST="${SOVEREIGN_HOST:-127.0.0.1}"
PORT="${SOVEREIGN_PORT:-8000}"
TOKEN="${SOVEREIGN_TRIGGER_TOKEN:-change-me-to-a-long-random-value}"

for _ in {1..15}; do
  if curl -sf "http://$HOST:$PORT/health" > /dev/null; then
    break
  fi
  sleep 1
done

curl -sf "http://$HOST:$PORT/health" | python -m json.tool
curl -sf -X POST "http://$HOST:$PORT/memory/add"           -H "x-sovereign-token: $TOKEN"           -H 'content-type: application/json'           -d '{"document": "Sovereign OS installed and calibrated", "metadata": {"source": "post-install"}}'           | python -m json.tool
