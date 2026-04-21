#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$HOME/.sovereign-os/pids"
LOG_DIR="$HOME/.sovereign-os/logs"
mkdir -p "$PID_DIR" "$LOG_DIR" "$HOME/sovereign-workspace"

start() {
  local name="$1"
  shift
  nohup "$@" > "$LOG_DIR/$name.log" 2>&1 &
  echo $! > "$PID_DIR/$name.pid"
  echo "[sovereign] started $name pid=$(cat "$PID_DIR/$name.pid")"
}

cd "$ROOT"
start orchestrator python -m orchestrator
start mcp-github npx -y @modelcontextprotocol/server-github
start mcp-gdrive npx -y @modelcontextprotocol/server-gdrive
start mcp-filesystem npx -y @modelcontextprotocol/server-filesystem "$HOME/sovereign-workspace"
echo "[sovereign] all services launched. Logs: $LOG_DIR"
