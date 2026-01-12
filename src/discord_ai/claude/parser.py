import json
from collections.abc import AsyncIterator

from discord_ai.claude.client import ClaudeClient
from discord_ai.models import AssistantMessage, StreamEvent, UserMessage


class StreamParser:
    def __init__(self, client: ClaudeClient):
        self.client = client

    async def parse_stream(self, session_id: str, message: str) -> AsyncIterator[StreamEvent]:
        async for line in self.client.run_session(session_id, message):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                event_type = data.get("type")

                if event_type in ("system", "result"):
                    continue

                if event_type == "assistant":
                    yield AssistantMessage(**data)
                elif event_type == "user":
                    yield UserMessage(**data)

            except (json.JSONDecodeError, TypeError, KeyError):
                continue
