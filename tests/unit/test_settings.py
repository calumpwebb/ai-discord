from discord_ai.settings import Settings


def test_loads_from_environment(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token_123")

    settings = Settings()

    assert settings.discord_token == "test_token_123"


def test_uses_default_values(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    # Set env vars to default values to override any .env file settings
    monkeypatch.setenv("CATEGORY_NAME", "Claude Conversations")
    monkeypatch.setenv("CLAUDE_CLI_PATH", "claude")
    monkeypatch.setenv("TYPING_INTERVAL_SECONDS", "5")
    monkeypatch.setenv("CLAUDE_TIMEOUT_SECONDS", "600")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    settings = Settings()

    assert settings.category_name == "Claude Conversations"
    assert settings.claude_cli_path == "claude"
    assert settings.typing_interval_seconds == 5
    assert settings.claude_timeout_seconds == 600
    assert settings.log_level == "INFO"


def test_overrides_defaults_from_env(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("CATEGORY_NAME", "Custom Category")
    monkeypatch.setenv("TYPING_INTERVAL_SECONDS", "3")

    settings = Settings()

    assert settings.category_name == "Custom Category"
    assert settings.typing_interval_seconds == 3
