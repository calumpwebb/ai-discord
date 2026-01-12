import pytest

from discord_ai.claude.client import FakeClaudeClient
from discord_ai.discord_client import FakeDiscordClient
from discord_ai.handlers.messages import MessageHandler
from tests.helpers.data.claude_responses import SIMPLE_TEXT


@pytest.mark.asyncio
async def test_handles_message_and_sends_response():
    claude = FakeClaudeClient(SIMPLE_TEXT)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings=None)

    await handler.handle_message(
        channel_id="channel_123", session_id="session-id-123", content="hello"
    )

    messages = discord.get_messages("channel_123")
    assert len(messages) == 1
    assert "Hello" in messages[0].content


@pytest.mark.asyncio
async def test_sends_typing_indicator_while_processing():
    claude = FakeClaudeClient(SIMPLE_TEXT)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings=None)

    await handler.handle_message(
        channel_id="channel_123", session_id="session-id-123", content="hello"
    )

    channel = discord.get_channel("channel_123")
    assert channel.typing_count >= 1
