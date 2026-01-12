import asyncio
from uuid import UUID

from discord_ai.claude.client import RealClaudeClient
from discord_ai.settings import Settings


async def main():
    settings = Settings()
    client = RealClaudeClient(settings)

    session_id = str(UUID("b2c3d4e5-f6a7-8901-bcde-f23456789012"))

    print(f"Starting session: {session_id}")
    lines = []
    async for line in client.run_session(session_id, "Hello, say hi"):
        print(f"Got line: {line[:100]}...")
        lines.append(line)
        if len(lines) >= 5:
            break

    print(f"Total lines: {len(lines)}")
    if lines:
        print(f"First line: {lines[0][:200]}")


if __name__ == "__main__":
    asyncio.run(main())
