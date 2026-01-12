import pytest

from discord_ai.discord_client import FakeDiscordClient


@pytest.mark.asyncio
async def test_fake_discord_sends_message():
    client = FakeDiscordClient()

    await client.send_message("channel_123", "Hello world")

    messages = client.get_messages("channel_123")
    assert len(messages) == 1
    assert messages[0].content == "Hello world"


@pytest.mark.asyncio
async def test_fake_discord_multiple_messages():
    client = FakeDiscordClient()

    await client.send_message("channel_123", "Message 1")
    await client.send_message("channel_123", "Message 2")

    messages = client.get_messages("channel_123")
    assert len(messages) == 2
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"


@pytest.mark.asyncio
async def test_fake_discord_trigger_typing():
    client = FakeDiscordClient()
    channel = client.get_channel("channel_123")

    await channel.trigger_typing()

    assert channel.typing_count == 1
