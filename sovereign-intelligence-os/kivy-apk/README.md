# Kivy APK client

Thin Android UI for Sovereign Intelligence OS.

Build:

```bash
pip install buildozer cython
buildozer android debug
adb install -r bin/*.apk
```

Notes:
- Heavy Python dependencies such as `chromadb`, `litellm`, and OpenCV are not packaged in the APK.
- The APK is only an HTTP client for the orchestrator running in Termux.
- Set `SOVEREIGN_API` and `SOVEREIGN_TRIGGER_TOKEN` at runtime if you do not use defaults.
