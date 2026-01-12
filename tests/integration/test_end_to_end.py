"""
End-to-end test with fake Discord but real Claude.
This verifies the full flow works together.
"""

from uuid import uuid4

import pytest

from discord_ai.claude.client import RealClaudeClient
from discord_ai.discord_client import FakeDiscordClient
from discord_ai.handlers.messages import MessageHandler
from discord_ai.settings import Settings


@pytest.mark.asyncio
async def test_full_message_flow_with_real_claude(monkeypatch):
    """
    Integration test: Real Claude CLI, Fake Discord
    Verifies messages flow through the system correctly
    """
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    claude = RealClaudeClient(settings)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings)

    session_id = str(uuid4())

    await handler.handle_message(
        channel_id="test_channel",
        session_id=session_id,
        content="Say hello in one word",
    )

    messages = discord.get_messages("test_channel")
    assert len(messages) > 0

    channel = discord.get_channel("test_channel")
    assert channel.typing_count > 0
