import sys

import structlog

from discord_ai.bot import create_bot
from discord_ai.claude.client import RealClaudeClient
from discord_ai.discord_client import RealDiscordClient
from discord_ai.handlers.messages import MessageHandler
from discord_ai.handlers.ready import on_ready as ready_handler
from discord_ai.logging_config import setup_logging
from discord_ai.settings import Settings

logger = structlog.get_logger()


def main():
    """Entry point for Discord AI bot"""

    try:
        settings = Settings()
    except Exception as e:
        print(f"Failed to load settings: {e}")
        print("Make sure DISCORD_BOT_TOKEN is set in .env")
        sys.exit(1)

    setup_logging(settings)
    logger.info("discord_ai.starting", version="0.1.0")

    bot = create_bot(settings)

    claude_client = RealClaudeClient(settings)
    discord_client = RealDiscordClient(bot)

    message_handler = MessageHandler(claude_client, discord_client, settings)  # noqa: F841

    @bot.event
    async def on_ready():
        await ready_handler(bot, settings)

    logger.info("discord_ai.bot.starting")
    try:
        bot.run(settings.discord_token)
    except Exception as e:
        logger.error("discord_ai.bot.error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
