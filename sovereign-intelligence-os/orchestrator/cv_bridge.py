from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)


def capture_screen(output: Path | None = None) -> Path | None:
    """Capture a screenshot using termux-screencap. Returns path or None on failure."""
    if shutil.which("termux-screencap") is None:
        log.warning("termux-screencap not available; skipping capture")
        return None
    if output is None:
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        output = Path(path)
    try:
        subprocess.run(["termux-screencap", str(output)], check=True, timeout=10)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        log.warning("termux-screencap failed: %s", exc)
        return None
    return output


def describe_image(path: Path) -> dict:
    """Return basic image stats. Requires the 'cv' extra."""
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore  # noqa: F401
    except ImportError:
        return {"error": "opencv-python-headless not installed; install with [cv] extra"}
    img = cv2.imread(str(path))
    if img is None:
        return {"error": f"could not read image at {path}"}
    height, width, channels = img.shape
    mean = img.mean(axis=(0, 1)).tolist()
    return {
        "path": str(path),
        "width": int(width),
        "height": int(height),
        "channels": int(channels),
        "mean_bgr": [float(value) for value in mean],
    }
