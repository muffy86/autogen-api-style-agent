from orchestrator.identity import build_system_prompt, load_identity


def test_load_identity_missing_file_returns_empty(tmp_path):
    assert load_identity(tmp_path / "missing.md") == ""


def test_load_identity_present_file_returns_content(tmp_path):
    identity_path = tmp_path / "identity.md"
    identity_path.write_text("Operator: Jane", encoding="utf-8")

    assert load_identity(identity_path) == "Operator: Jane"


def test_build_system_prompt_concatenates_identity():
    prompt = build_system_prompt("Operator: Jane")

    assert "Sovereign Intelligence OS orchestrator" in prompt
    assert "Operator identity:" in prompt
    assert prompt.endswith("Operator: Jane")
