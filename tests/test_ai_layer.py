from repair_loop.ai import is_enabled


def test_ai_layer_disabled_without_key(monkeypatch):
    monkeypatch.delenv("REPAIRLOOP_API_KEY", raising=False)
    assert is_enabled() is False


def test_ai_layer_enabled_with_key(monkeypatch):
    monkeypatch.setenv("REPAIRLOOP_API_KEY", "test")
    assert is_enabled() is True
