import pytest

from discord_ai.claude.client import FakeClaudeClient


@pytest.mark.asyncio
async def test_fake_client_yields_canned_responses():
    responses = ["line1", "line2", "line3"]
    client = FakeClaudeClient(responses)

    lines = [line async for line in client.run_session("session-123", "hello")]

    assert lines == ["line1", "line2", "line3"]


@pytest.mark.asyncio
async def test_fake_client_can_be_reused():
    responses = ["response"]
    client = FakeClaudeClient(responses)

    first_run = [line async for line in client.run_session("session-1", "msg1")]
    second_run = [line async for line in client.run_session("session-2", "msg2")]

    assert first_run == ["response"]
    assert second_run == ["response"]
