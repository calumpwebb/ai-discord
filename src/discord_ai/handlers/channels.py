from uuid import uuid4

import structlog

logger = structlog.get_logger()


async def initialize_channel(channel):
    """Initialize a channel with a session UUID"""

    if channel.topic and channel.topic.startswith("Session: "):
        logger.info("discord_ai.channel.existing", channel=channel.name, topic=channel.topic)
        return

    session_id = str(uuid4())
    new_topic = f"Session: {session_id}"

    try:
        await channel.edit(topic=new_topic)
        logger.info("discord_ai.channel.initialized", channel=channel.name, session_id=session_id)
    except Exception as e:
        logger.error("discord_ai.channel.init_failed", channel=channel.name, error=str(e))


async def on_channel_create(channel, settings):
    """Handle new channel creation"""

    if not channel.category:
        return

    if channel.category.name != settings.category_name:
        return

    logger.info("discord_ai.channel.created", channel=channel.name)
    await initialize_channel(channel)
