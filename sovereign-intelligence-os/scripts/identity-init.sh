#!/usr/bin/env bash
set -euo pipefail

TARGET="$HOME/.sovereign-os/identity.md"
mkdir -p "$(dirname "$TARGET")"
if [ -f "$TARGET" ]; then
  echo "[sovereign] identity already exists at $TARGET"
  exit 0
fi
cp "$(dirname "$0")/../configs/identity.example.md" "$TARGET"
echo "[sovereign] wrote $TARGET — edit to personalize"
