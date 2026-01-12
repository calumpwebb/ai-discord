from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel


class TextContent(BaseModel):
    type: Literal["text"]
    text: str


class ToolUseContent(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: dict[str, Any]


class SystemEvent(BaseModel):
    type: Literal["system"]
    subtype: str
    session_id: UUID
    uuid: UUID


class AssistantMessage(BaseModel):
    type: Literal["assistant"]
    message: dict[str, Any]
    session_id: UUID
    uuid: UUID

    @property
    def content_blocks(self) -> list[TextContent | ToolUseContent]:
        blocks = []
        for item in self.message.get("content", []):
            if item["type"] == "text":
                blocks.append(TextContent(**item))
            elif item["type"] == "tool_use":
                blocks.append(ToolUseContent(**item))
        return blocks


class UserMessage(BaseModel):
    type: Literal["user"]
    message: dict[str, Any]
    session_id: UUID
    uuid: UUID
    tool_use_result: dict[str, Any] | None = None


class ResultEvent(BaseModel):
    type: Literal["result"]
    subtype: str
    is_error: bool
    result: str
    session_id: UUID
    uuid: UUID


StreamEvent = SystemEvent | AssistantMessage | UserMessage | ResultEvent
