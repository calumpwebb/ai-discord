import sys

import structlog

from discord_ai.bot import create_bot
from discord_ai.claude.client import RealClaudeClient
from discord_ai.discord_client import RealDiscordClient
from discord_ai.handlers.channels import on_channel_create as channel_create_handler
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

    @bot.event
    async def on_guild_channel_create(channel):
        await channel_create_handler(channel, settings)

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if not message.channel.category:
            return

        if message.channel.category.name != settings.category_name:
            return

        topic = message.channel.topic or ""

        if not topic.startswith("Session: "):
            logger.warning("discord_ai.message.no_session_id", channel=message.channel.name)
            await message.channel.send("||Error: No session ID found in channel topic||")
            return

        session_id = topic.replace("Session: ", "").strip()

        logger.info(
            "discord_ai.message.received",
            channel=message.channel.name,
            session_id=session_id,
            user=str(message.author),
        )

        try:
            await message_handler.handle_message(
                channel_id=str(message.channel.id),
                session_id=session_id,
                content=message.content,
            )
        except Exception as e:
            logger.error("discord_ai.message.error", error=str(e), channel=message.channel.name)
            await message.channel.send(f"||Error: {str(e)}||")

    logger.info("discord_ai.bot.starting")
    try:
        bot.run(settings.discord_token)
    except Exception as e:
        logger.error("discord_ai.bot.error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
