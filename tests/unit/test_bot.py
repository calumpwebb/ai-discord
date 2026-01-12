from discord_ai.bot import create_bot
from discord_ai.settings import Settings


def test_create_bot_returns_discord_bot(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    bot = create_bot(settings)

    assert bot is not None
    assert hasattr(bot, "run")


def test_create_bot_configures_intents(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    bot = create_bot(settings)

    assert bot.intents.message_content is True
    assert bot.intents.guilds is True
