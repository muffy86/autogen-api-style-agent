# Security considerations

- OpenClaw had supply-chain incidents in Feb and Mar 2026. The Termux bootstrap pins `openclaw@>=2026.3.22` to avoid compromised builds and should only be updated after manual review.
- ClawJacked-style localhost WebSocket abuse is a real concern for mobile agents. The orchestrator binds to `127.0.0.1` by default, not `0.0.0.0`.
- All mutating endpoints require the shared-secret `x-sovereign-token` header. Rotate it immediately after initial setup.
- The operator identity file contains personal information. Store it at `~/.sovereign-os/identity.md`; do not commit it to git.
- Termux permissions should be granted intentionally. `SYSTEM_ALERT_WINDOW` supports overlay-style cockpit UX, while `MEDIA_PROJECTION` is the Android permission family typically required for screen capture workflows paired with `termux-screencap` or related automation.
- Prefer Ollama or other local models over cloud providers whenever the workload is sensitive, sovereign, or uncensored.
- Keep Google Drive MCP credentials scoped narrowly and avoid sharing a drive account used for unrelated personal data.
- The browser bridge requires `playwright-core` plus a system Chromium binary; avoid browsing untrusted pages with elevated filesystem MCP access in the same session.
