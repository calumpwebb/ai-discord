from collections.abc import AsyncIterator
from typing import Protocol


class ClaudeClient(Protocol):
    """Protocol for Claude CLI interaction"""

    async def run_session(self, session_id: str, message: str) -> AsyncIterator[str]:
        """Yields JSON lines from Claude CLI"""
        ...


class FakeClaudeClient:
    """Test implementation returning canned responses"""

    def __init__(self, responses: list[str]):
        self.responses = responses

    async def run_session(self, session_id: str, message: str) -> AsyncIterator[str]:
        for line in self.responses:
            yield line


class RealClaudeClient:
    """Real implementation spawning Claude CLI subprocess"""

    def __init__(self, settings):
        self.settings = settings

    async def run_session(self, session_id: str, message: str) -> AsyncIterator[str]:
        raise NotImplementedError("RealClaudeClient not yet implemented")
