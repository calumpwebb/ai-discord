import asyncio

from discord_ai.claude.formatter import EventFormatter
from discord_ai.claude.parser import StreamParser
from discord_ai.utils.typing import typing_loop


class MessageHandler:
    """Handles incoming Discord messages"""

    def __init__(self, claude_client, discord_client, settings):
        self.claude_client = claude_client
        self.discord_client = discord_client
        self.settings = settings
        self.parser = StreamParser(claude_client)
        self.formatter = EventFormatter()

    async def handle_message(self, channel_id: str, session_id: str, content: str):
        channel = self.discord_client.get_channel(channel_id)

        await channel.trigger_typing()

        interval = getattr(self.settings, "typing_interval_seconds", 5) if self.settings else 5
        typing_task = asyncio.create_task(typing_loop(channel, interval=interval))

        try:
            async for event in self.parser.parse_stream(session_id, content):
                messages = self.formatter.format_event(event)
                for msg in messages:
                    await self.discord_client.send_message(channel_id, msg)
        finally:
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
