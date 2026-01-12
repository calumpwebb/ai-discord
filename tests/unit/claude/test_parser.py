import pytest

from discord_ai.claude.client import FakeClaudeClient
from discord_ai.claude.parser import StreamParser
from discord_ai.models import AssistantMessage
from tests.helpers.data.claude_responses import SIMPLE_TEXT, TOOL_USE_SEQUENCE


@pytest.mark.asyncio
async def test_parser_yields_parsed_events():
    client = FakeClaudeClient(SIMPLE_TEXT)
    parser = StreamParser(client)

    events = [e async for e in parser.parse_stream("session-123", "hello")]

    assert len(events) == 1
    assert isinstance(events[0], AssistantMessage)
    assert events[0].type == "assistant"


@pytest.mark.asyncio
async def test_parser_handles_multiple_events():
    client = FakeClaudeClient(TOOL_USE_SEQUENCE)
    parser = StreamParser(client)

    events = [e async for e in parser.parse_stream("session-123", "read file")]

    assert len(events) == 4
    assert all(hasattr(e, "type") for e in events)


@pytest.mark.asyncio
async def test_parser_skips_system_events():
    system_event = '{"type":"system","subtype":"init","session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"bc660af3-0540-4e00-b3e0-dcdb493c72dd"}'
    text_event = '{"type":"assistant","message":{"content":[{"type":"text","text":"Hello"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}'

    client = FakeClaudeClient([system_event, text_event])
    parser = StreamParser(client)

    events = [e async for e in parser.parse_stream("session-123", "hello")]

    assert len(events) == 1
    assert isinstance(events[0], AssistantMessage)
