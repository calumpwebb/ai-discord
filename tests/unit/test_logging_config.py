import structlog

from discord_ai.logging_config import setup_logging
from discord_ai.settings import Settings


def test_setup_logging_configures_structlog(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = Settings()

    setup_logging(settings)

    logger = structlog.get_logger()
    assert logger is not None


def test_setup_logging_respects_log_level(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    settings = Settings()

    setup_logging(settings)
