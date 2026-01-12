from dataclasses import dataclass
from typing import Protocol


@dataclass
class FakeMessage:
    content: str
    channel_id: str


@dataclass
class FakeChannel:
    channel_id: str
    typing_count: int = 0

    async def trigger_typing(self):
        self.typing_count += 1


class DiscordClient(Protocol):
    """Protocol for Discord API interaction"""

    async def send_message(self, channel_id: str, content: str):
        ...

    def get_channel(self, channel_id: str):
        ...


class FakeDiscordClient:
    """Test implementation storing messages in memory"""

    def __init__(self):
        self._messages: dict[str, list[FakeMessage]] = {}
        self._channels: dict[str, FakeChannel] = {}

    async def send_message(self, channel_id: str, content: str):
        if channel_id not in self._messages:
            self._messages[channel_id] = []

        msg = FakeMessage(content=content, channel_id=channel_id)
        self._messages[channel_id].append(msg)

    def get_messages(self, channel_id: str) -> list[FakeMessage]:
        return self._messages.get(channel_id, [])

    def get_channel(self, channel_id: str) -> FakeChannel:
        if channel_id not in self._channels:
            self._channels[channel_id] = FakeChannel(channel_id=channel_id)
        return self._channels[channel_id]


class RealDiscordClient:
    """Real implementation using discord.py"""

    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, channel_id: str, content: str):
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            await channel.send(content)

    def get_channel(self, channel_id: str):
        return self.bot.get_channel(int(channel_id))
