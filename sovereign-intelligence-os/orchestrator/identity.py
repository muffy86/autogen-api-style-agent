from __future__ import annotations

from pathlib import Path


def load_identity(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def build_system_prompt(identity: str) -> str:
    base = (
        "You are the Sovereign Intelligence OS orchestrator. You run locally on the "
        "operator's device. Be terse, technical, and autonomous."
    )
    if not identity:
        return base
    return f"{base}\n\n---\nOperator identity:\n{identity}"
