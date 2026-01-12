import sys

import structlog

from discord_ai.handlers.channels import initialize_channel

logger = structlog.get_logger()


async def on_ready(bot, settings):
    """Handle bot ready event"""

    logger.info("discord_ai.bot.ready", user=str(bot.user))

    if not bot.guilds:
        logger.error("discord_ai.bot.no_guilds")
        await bot.close()
        sys.exit(1)

    guild = bot.guilds[0]
    category = None

    for cat in guild.categories:
        if cat.name == settings.category_name:
            category = cat
            break

    if not category:
        available = [cat.name for cat in guild.categories]
        error_msg = f"""
Category '{settings.category_name}' not found in server.

To fix this, either:
1. Create a category named '{settings.category_name}' in your Discord server
2. Update CATEGORY_NAME in your .env file to match an existing category

Available categories in server:
{chr(10).join(f"  - {name}" for name in available)}
"""
        logger.error(
            "discord_ai.category.not_found", category=settings.category_name, available=available
        )
        print(error_msg)
        await bot.close()
        sys.exit(1)

    logger.info(
        "discord_ai.category.found", category=category.name, channels=len(category.channels)
    )

    for channel in category.channels:
        await initialize_channel(channel)

    logger.info("discord_ai.bot.ready_complete")
