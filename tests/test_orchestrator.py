from clawbot.orchestrator import OpenClawAdapter


def test_missing_command_is_reported(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    result = OpenClawAdapter("missing-openclaw").run("hello")
    assert not result.ok
    assert "not found" in result.output.lower()
