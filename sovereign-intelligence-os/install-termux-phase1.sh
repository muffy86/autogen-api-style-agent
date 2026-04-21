#!/data/data/com.termux/files/usr/bin/bash
# Sovereign Intelligence OS — Termux bootstrap, Phase 1 (2026.5)
# Idempotent; safe to re-run.
set -euo pipefail

log() { printf '\033[1;36m[sovereign]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[sovereign]\033[0m %s\n' "$*" >&2; }

if [ -z "${PREFIX:-}" ] || [[ "$PREFIX" != */com.termux/* ]]; then
  warn "This script is designed for Termux. Continuing anyway."
fi

log "Updating Termux packages"
pkg update -y
pkg upgrade -y

log "Installing base tooling"
pkg install -y git python nodejs-lts proot-distro build-essential \
  libffi openssl wget curl jq termux-api termux-tasker x11-repo
pkg install -y chromium || warn "chromium install skipped — run 'pkg install chromium' manually if needed"

log "Installing proot Ubuntu 24.04"
proot-distro install ubuntu || log "ubuntu distro already installed"

log "Preparing Termux storage access"
termux-setup-storage || warn "storage permission not granted; re-run after granting"

# OpenClaw — pin to a post-incident version to avoid compromised releases
log "Installing OpenClaw (pinned >=2026.3.22)"
npm install -g 'openclaw@>=2026.3.22'

log "Installing browser and MCP tooling"
npm install -g playwright-core
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-gdrive
npm install -g @modelcontextprotocol/server-filesystem

log "Bootstrapping Python env"
python -m pip install --upgrade pip
python -m pip install --user -r "$(dirname "$0")/requirements.txt"

# Playwright: use system chromium, skip browser downloads
export PLAYWRIGHT_BROWSERS_PATH=0
CHROME_EXECUTABLE_PATH="$(command -v chromium || true)"
export CHROME_EXECUTABLE_PATH

mkdir -p "$HOME/.sovereign-os/memory"
mkdir -p "$HOME/sovereign-workspace"
if [ ! -f "$HOME/.sovereign-os/identity.md" ]; then
  cp "$(dirname "$0")/configs/identity.example.md" "$HOME/.sovereign-os/identity.md"
  log "Created $HOME/.sovereign-os/identity.md — edit to personalize"
fi

log "Phase 1 complete. Next: bash scripts/launch-os.sh"
