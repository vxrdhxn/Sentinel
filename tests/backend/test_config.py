from backend.app.config import Settings


def test_settings_load_from_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.environment == "testing"
    assert settings.log_level == "DEBUG"
