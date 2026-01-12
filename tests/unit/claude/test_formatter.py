from uuid import UUID

from discord_ai.claude.formatter import EventFormatter
from discord_ai.models import (
    AssistantMessage,
    UserMessage,
)


def test_formats_text_content():
    event = AssistantMessage(
        type="assistant",
        message={"content": [{"type": "text", "text": "Hello world"}]},
        session_id=UUID("df83d374-79dd-4100-be18-fd7e4bccc33b"),
        uuid=UUID("408d2155-b3f8-4044-a00e-cedd765d3eaa"),
    )
    formatter = EventFormatter()

    messages = formatter.format_event(event)

    assert len(messages) == 1
    assert messages[0] == "Hello world"


def test_formats_tool_use():
    event = AssistantMessage(
        type="assistant",
        message={
            "content": [
                {
                    "type": "tool_use",
                    "id": "tool_123",
                    "name": "Read",
                    "input": {"file_path": "test.py"},
                }
            ]
        },
        session_id=UUID("df83d374-79dd-4100-be18-fd7e4bccc33b"),
        uuid=UUID("408d2155-b3f8-4044-a00e-cedd765d3eaa"),
    )
    formatter = EventFormatter()

    messages = formatter.format_event(event)

    assert len(messages) == 1
    assert "Read" in messages[0]
    assert "test.py" in messages[0]


def test_formats_tool_result_in_spoilers():
    event = UserMessage(
        type="user",
        message={"content": []},
        session_id=UUID("df83d374-79dd-4100-be18-fd7e4bccc33b"),
        uuid=UUID("408d2155-b3f8-4044-a00e-cedd765d3eaa"),
        tool_use_result={"stdout": "file contents here", "stderr": ""},
    )
    formatter = EventFormatter()

    messages = formatter.format_event(event)

    assert len(messages) == 1
    assert messages[0].startswith("||")
    assert messages[0].endswith("||")
    assert "file contents here" in messages[0]


def test_formats_error_in_spoilers():
    event = UserMessage(
        type="user",
        message={
            "content": [{"type": "tool_result", "is_error": True, "content": "File not found"}]
        },
        session_id=UUID("df83d374-79dd-4100-be18-fd7e4bccc33b"),
        uuid=UUID("408d2155-b3f8-4044-a00e-cedd765d3eaa"),
        tool_use_result="Error: File not found",
    )
    formatter = EventFormatter()

    messages = formatter.format_event(event)

    assert len(messages) == 1
    assert messages[0].startswith("||")
    assert "File not found" in messages[0]
