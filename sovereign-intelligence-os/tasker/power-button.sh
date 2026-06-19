#!/data/data/com.termux/files/usr/bin/bash
# Called by Tasker → Termux:Tasker plugin when power button is double-pressed.
# Sends the current clipboard as the query.
set -euo pipefail

TOKEN="${SOVEREIGN_TRIGGER_TOKEN:-change-me-to-a-long-random-value}"
QUERY="$(termux-clipboard-get || echo '')"
if [ -z "$QUERY" ]; then
  termux-toast "Sovereign: clipboard empty"
  exit 0
fi
curl -sf -X POST http://127.0.0.1:8000/trigger           -H "x-sovereign-token: $TOKEN"           -H 'content-type: application/json'           -d "$(jq -n --arg q "$QUERY" '{query:$q,gesture:"power",context:"clipboard"}')"           | jq -r '.content' | termux-toast -g top
