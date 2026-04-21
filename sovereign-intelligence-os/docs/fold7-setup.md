# Galaxy Fold 7 setup checklist

1. Install Termux from F-Droid, not from the Play Store.
2. Launch Termux once, grant storage access, and update packages.
3. Copy this repository onto the device.
4. Run:

```bash
cd sovereign-intelligence-os
bash install-termux-phase1.sh
bash scripts/identity-init.sh
bash scripts/launch-os.sh
bash scripts/post-install.sh
```

5. Edit `~/.sovereign-os/identity.md` with your operator profile.
6. Import `tasker/sovereign-trigger.tsk.xml` into Tasker and update the shared secret.
7. Install Termux:Tasker if you want clipboard or gesture triggers.
8. Build or sideload the Kivy APK from `kivy-apk/`.
9. Verify `http://127.0.0.1:8000/health` responds locally.

Thermal guidance:
- Use `nice -n 10` or similar when launching proot-heavy workloads if the device heats aggressively.
- Avoid running Ollama models larger than 7B directly on-device.
- Use multi-window rather than DeX-like mirrored layouts when possible; it reduces background redraw pressure.
- Stop unused MCP servers to preserve memory and battery.
