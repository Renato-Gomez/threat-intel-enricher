import pytest
from src.config import Settings, load_config


def test_settings_initialization_empty():
    """Test that Settings can be initialized with an empty dictionary by default."""
    settings = Settings()
    assert settings.api_keys == {}


def test_settings_get_api_key_success():
    """Test getting an existing API key from the Settings object."""
    settings = Settings(api_keys={"ABUSEIPDB_API_KEY": "test_key_123"})

    # Should resolve "abuseipdb" to "ABUSEIPDB_API_KEY"
    key = settings.get_api_key("abuseipdb")
    assert key == "test_key_123"


def test_settings_get_api_key_missing():
    """Test that getting a missing API key raises a ValueError (fail-fast)."""
    settings = Settings(api_keys={})

    with pytest.raises(
        ValueError, match="Required configuration missing in .env: VIRUSTOTAL_API_KEY"
    ):
        settings.get_api_key("virustotal")


def test_load_config_success(monkeypatch):
    """
    Test that load_config correctly picks up _API_KEY env vars.
    We use monkeypatch to avoid side effects on the real environment.
    """
    monkeypatch.setenv("DUMMY_API_KEY", "dummy_value")
    monkeypatch.setenv("OTHER_VAR", "ignored_value")

    settings = load_config()

    # It should pick up DUMMY_API_KEY but not OTHER_VAR
    assert "DUMMY_API_KEY" in settings.api_keys
    assert settings.api_keys["DUMMY_API_KEY"] == "dummy_value"
    assert "OTHER_VAR" not in settings.api_keys


def test_load_config_empty_values_ignored(monkeypatch):
    """Test that empty string API keys are ignored during load."""
    monkeypatch.setenv("EMPTY_API_KEY", "   ")

    settings = load_config()
    assert "EMPTY_API_KEY" not in settings.api_keys
