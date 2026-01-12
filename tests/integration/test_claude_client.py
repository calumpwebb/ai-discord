import json
from uuid import uuid4

import pytest

from discord_ai.claude.client import RealClaudeClient
from discord_ai.settings import Settings


@pytest.mark.asyncio
async def test_real_client_spawns_subprocess(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()
    client = RealClaudeClient(settings)

    session_id = str(uuid4())
    lines = []
    async for line in client.run_session(session_id, "hello"):
        lines.append(line)
        if len(lines) >= 3:
            break

    assert len(lines) > 0
    first_event = json.loads(lines[0])
    assert "type" in first_event
