#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="$HOME/.sovereign-os/pids"
LOG_DIR="$HOME/.sovereign-os/logs"
export SOVEREIGN_WORKSPACE_DIR="${SOVEREIGN_WORKSPACE_DIR:-$HOME/sovereign-workspace}"
mkdir -p "$PID_DIR" "$LOG_DIR" "$SOVEREIGN_WORKSPACE_DIR"

cmd="${1:-start}"

stop_one() {
  local name="$1"
  local pidfile="$PID_DIR/$name.pid"
  if [ -f "$pidfile" ]; then
    local pid
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      echo "[sovereign] stopped $name (pid=$pid)"
    fi
    rm -f "$pidfile"
  fi
}

start_one() {
  local name="$1"
  shift
  stop_one "$name"
  nohup "$@" > "$LOG_DIR/$name.log" 2>&1 &
  echo $! > "$PID_DIR/$name.pid"
  echo "[sovereign] started $name pid=$(cat "$PID_DIR/$name.pid")"
}

status_one() {
  local name="$1"
  local pidfile="$PID_DIR/$name.pid"
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "[sovereign] $name running pid=$(cat "$pidfile")"
  else
    echo "[sovereign] $name stopped"
  fi
}

services=(orchestrator mcp-github mcp-gdrive mcp-filesystem)

case "$cmd" in
  start)
    cd "$ROOT"
    start_one orchestrator python -m orchestrator
    start_one mcp-github npx -y @modelcontextprotocol/server-github
    start_one mcp-gdrive npx -y @modelcontextprotocol/server-gdrive
    start_one mcp-filesystem npx -y @modelcontextprotocol/server-filesystem "$SOVEREIGN_WORKSPACE_DIR"
    echo "[sovereign] all services launched. Logs: $LOG_DIR"
    ;;
  stop)
    for s in "${services[@]}"; do
      stop_one "$s"
    done
    ;;
  status)
    for s in "${services[@]}"; do
      status_one "$s"
    done
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  *)
    echo "usage: $0 {start|stop|status|restart}" >&2
    exit 2
    ;;
esac
