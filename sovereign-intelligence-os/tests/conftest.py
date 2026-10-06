import importlib
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_home(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        monkeypatch.setenv("SOVEREIGN_MEMORY_PATH", str(Path(directory) / "memory"))
        monkeypatch.setenv("SOVEREIGN_IDENTITY_PATH", str(Path(directory) / "identity.md"))
        monkeypatch.setenv("SOVEREIGN_TRIGGER_TOKEN", "test-token")
        yield Path(directory)


@pytest.fixture
def load_module(tmp_home):
    def _load(name: str):
        importlib.invalidate_caches()
        for module_name in list(sys.modules):
            if module_name == "orchestrator" or module_name.startswith("orchestrator."):
                sys.modules.pop(module_name)
        return importlib.import_module(name)

    return _load
