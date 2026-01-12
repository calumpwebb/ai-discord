# tests/unit/test_models.py
from uuid import UUID

from discord_ai.models import (
    AssistantMessage,
    TextContent,
    ToolUseContent,
)


def test_text_content_validates():
    content = TextContent(type="text", text="Hello")

    assert content.type == "text"
    assert content.text == "Hello"


def test_tool_use_content_validates():
    content = ToolUseContent(
        type="tool_use", id="tool_123", name="Read", input={"file_path": "test.py"}
    )

    assert content.type == "tool_use"
    assert content.name == "Read"
    assert content.input["file_path"] == "test.py"


def test_assistant_message_parses_real_json():
    json_str = """
    {
        "type": "assistant",
        "message": {
            "content": [{"type": "text", "text": "Hello"}]
        },
        "session_id": "df83d374-79dd-4100-be18-fd7e4bccc33b",
        "uuid": "408d2155-b3f8-4044-a00e-cedd765d3eaa"
    }
    """

    event = AssistantMessage.model_validate_json(json_str)

    assert event.type == "assistant"
    assert event.session_id == UUID("df83d374-79dd-4100-be18-fd7e4bccc33b")


def test_assistant_message_extracts_content_blocks():
    json_str = """
    {
        "type": "assistant",
        "message": {
            "content": [
                {"type": "text", "text": "Let me read that"},
                {"type": "tool_use", "id": "tool_1", "name": "Read", "input": {}}
            ]
        },
        "session_id": "df83d374-79dd-4100-be18-fd7e4bccc33b",
        "uuid": "408d2155-b3f8-4044-a00e-cedd765d3eaa"
    }
    """

    event = AssistantMessage.model_validate_json(json_str)
    blocks = event.content_blocks

    assert len(blocks) == 2
    assert isinstance(blocks[0], TextContent)
    assert blocks[0].text == "Let me read that"
    assert isinstance(blocks[1], ToolUseContent)
    assert blocks[1].name == "Read"
