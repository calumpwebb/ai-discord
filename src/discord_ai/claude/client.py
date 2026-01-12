import asyncio
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
        cmd = [
            self.settings.claude_cli_path,
            "--print",
            "--output-format",
            "stream-json",
            "--verbose",
            "--session-id",
            session_id,
            message,
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            if process.stdout:
                async for line in process.stdout:
                    decoded = line.decode().strip()
                    if decoded:
                        yield decoded

            await asyncio.wait_for(process.wait(), timeout=self.settings.claude_timeout_seconds)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise
        finally:
            if process.stderr:
                await process.stderr.read()
