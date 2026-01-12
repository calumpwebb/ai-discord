# Discord AI Bot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.
>
> **Execution:** Follow the **Waves** structure below. Execute waves in parallel using subagents. Perform **code review after each wave** before proceeding.

**Goal:** Build a Discord bot that bridges Discord channels to Claude CLI sessions, enabling conversational AI interactions.

**Architecture:** Each channel in "Claude Conversations" category maps to a persistent Claude CLI session via UUID stored in channel topic. Bot spawns Claude CLI subprocess for each message, parses stream-json output, and sends formatted responses to Discord in real-time.

**Tech Stack:** Python 3.12+, discord.py, pydantic-settings, structlog, pytest, uv

---

## 🌊 Execution Waves

This plan is organized into **5 waves** with **5 code reviews** for parallelization + quality.

### Wave Dependency Graph

```
🌊 Wave 0 (Sequential - Foundation)
├── Task 1: Project Setup & Tooling
└── ⚠️  Must complete before any other wave

🌊 Wave 1 (Parallel - 4 subagents possible)
├── Task 2: Settings Module
├── Task 3: Stream Event Models
├── Task 8: Typing Indicator
└── Task 11: Logging Setup

🌊 Wave 2 (Parallel - 2 subagents possible)
├── Task 4: Claude Client Protocol
└── Task 9: Discord Client Protocol

🌊 Wave 3 (Parallel - 2 subagents possible)
├── Task 5: RealClaudeClient (depends on 4)
└── Task 7: Event Formatter (depends on 3)

🌊 Wave 4 (Parallel - 4 subagents possible)
├── Task 6: Stream Parser (depends on 3, 4)
├── Task 10: Message Handler (depends on 6, 7, 8, 9)
├── Task 12: Bot Initialization
└── Task 13: Main Entry Point (depends on 11, 12)

🌊 Wave 5 (Sequential - Integration)
├── Task 14: Ready Handler (depends on 13)
├── Task 15: Channel Detection (depends on 14)
├── Task 16: Message Handler Integration (depends on 10, 13)
├── Task 17: README
└── Task 18: Integration Tests
```

### Code Review Schedule

After completing each wave, perform a code review:

| Phase | Focus |
|-------|-------|
| 🔍 Review Wave 0 | Settings, Models, Typing, Logging |
| 🔍 Review Wave 1 | Claude Client, Discord Client Protocols |
| 🔍 Review Wave 2 | RealClaudeClient, EventFormatter |
| 🔍 Review Wave 3 | StreamParser, MessageHandler, Bot, Main |
| 🔍 Review Wave 4 | Ready, Channels, MessageHandler Integration, README, Tests |

### Parallelization Summary

| Wave | Parallel Tasks | Estimated Speedup |
|------|----------------|-------------------|
| 0 | 1 | baseline |
| 1 | 4 | **4x** |
| 2 | 2 | **2x** |
| 3 | 2 | **2x** |
| 4 | 4 | **4x** |
| 5 | 5 | **5x** |

---

## Task 1: Project Setup, Tooling, and Linting

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `.pre-commit-config.yaml`

**Step 1: Create pyproject.toml**

```bash
cat > pyproject.toml << 'EOF'
[project]
name = "discord-ai"
version = "0.1.0"
description = "Discord bot powered by Claude CLI"
requires-python = ">=3.12"
dependencies = [
    "discord.py>=2.3.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",
    "pre-commit>=3.5.0",
]

[project.scripts]
discord-ai-bot = "discord_ai.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["discord_ai"]
EOF
```

**Step 2: Create .gitignore**

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
EOF
```

**Step 3: Create .env.example**

```bash
cat > .env.example << 'EOF'
DISCORD_BOT_TOKEN=your_token_here
CATEGORY_NAME=Claude Conversations
CLAUDE_CLI_PATH=claude
TYPING_INTERVAL_SECONDS=5
CLAUDE_TIMEOUT_SECONDS=600
LOG_LEVEL=INFO
EOF
```

**Step 4: Create .pre-commit-config.yaml**

```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      # Run the linter
      - id: ruff
        args: [--fix]
      # Run the formatter
      - id: ruff-format
EOF
```

**Step 5: Install dependencies and setup pre-commit**

Run: 
```bash
uv sync
uv run pre-commit install
```
Expected: Dependencies installed and pre-commit hooks set up

**Step 6: Commit**

```bash
git add pyproject.toml .gitignore .env.example .pre-commit-config.yaml
git commit -m "chore: initialize project with dependencies and tooling"
```

---

## Task 2: Settings Module

**Files:**
- Create: `src/discord_ai/settings.py`
- Create: `tests/unit/test_settings.py`

**Step 1: Write failing test**

```python
# tests/unit/test_settings.py
import os
import pytest
from discord_ai.settings import Settings


def test_loads_from_environment(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token_123")

    settings = Settings()

    assert settings.discord_token == "test_token_123"


def test_uses_default_values(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")

    settings = Settings()

    assert settings.category_name == "Claude Conversations"
    assert settings.claude_cli_path == "claude"
    assert settings.typing_interval_seconds == 5
    assert settings.claude_timeout_seconds == 600
    assert settings.log_level == "INFO"


def test_overrides_defaults_from_env(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("CATEGORY_NAME", "Custom Category")
    monkeypatch.setenv("TYPING_INTERVAL_SECONDS", "3")

    settings = Settings()

    assert settings.category_name == "Custom Category"
    assert settings.typing_interval_seconds == 3
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_settings.py -v`
Expected: FAIL with "No module named 'discord_ai.settings'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    discord_token: str = Field(alias="DISCORD_BOT_TOKEN")
    category_name: str = "Claude Conversations"
    claude_cli_path: str = "claude"
    typing_interval_seconds: int = 5
    claude_timeout_seconds: int = 600
    log_level: str = "INFO"
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_settings.py -v`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/settings.py tests/unit/test_settings.py
git commit -m "feat: add settings module with pydantic-settings"
```

---

## Task 3: Stream Event Models

**Files:**
- Create: `src/discord_ai/models.py`
- Create: `tests/unit/test_models.py`
- Create: `tests/helpers/data/claude_responses.py`

**Step 1: Write failing test**

```python
# tests/unit/test_models.py
import pytest
from discord_ai.models import (
    TextContent,
    ToolUseContent,
    SystemEvent,
    AssistantMessage,
    UserMessage,
    ResultEvent,
)
from uuid import UUID


def test_text_content_validates():
    content = TextContent(type="text", text="Hello")

    assert content.type == "text"
    assert content.text == "Hello"


def test_tool_use_content_validates():
    content = ToolUseContent(
        type="tool_use",
        id="tool_123",
        name="Read",
        input={"file_path": "test.py"}
    )

    assert content.type == "tool_use"
    assert content.name == "Read"
    assert content.input["file_path"] == "test.py"


def test_assistant_message_parses_real_json():
    json_str = '''
    {
        "type": "assistant",
        "message": {
            "content": [{"type": "text", "text": "Hello"}]
        },
        "session_id": "df83d374-79dd-4100-be18-fd7e4bccc33b",
        "uuid": "408d2155-b3f8-4044-a00e-cedd765d3eaa"
    }
    '''

    event = AssistantMessage.model_validate_json(json_str)

    assert event.type == "assistant"
    assert event.session_id == UUID("df83d374-79dd-4100-be18-fd7e4bccc33b")


def test_assistant_message_extracts_content_blocks():
    json_str = '''
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
    '''

    event = AssistantMessage.model_validate_json(json_str)
    blocks = event.content_blocks

    assert len(blocks) == 2
    assert isinstance(blocks[0], TextContent)
    assert blocks[0].text == "Let me read that"
    assert isinstance(blocks[1], ToolUseContent)
    assert blocks[1].name == "Read"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_models.py -v`
Expected: FAIL with "No module named 'discord_ai.models'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/models.py
from pydantic import BaseModel
from typing import Literal, Any
from uuid import UUID


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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_models.py -v`
Expected: PASS (all 4 tests)

**Step 5: Create canned test data**

```python
# tests/helpers/data/claude_responses.py
"""Real Claude CLI JSON responses for testing"""

SIMPLE_TEXT = [
    '{"type":"assistant","message":{"content":[{"type":"text","text":"Hello"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
]

TOOL_USE_SEQUENCE = [
    '{"type":"assistant","message":{"content":[{"type":"text","text":"Let me check that file"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
    '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"toolu_123","name":"Read","input":{"file_path":"test.py"}}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"78f33550-6bd1-4fa4-98a3-94257f97bf7d"}',
    '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"file contents here","is_error":false,"tool_use_id":"toolu_123"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"1b9893ae-1fbd-4b73-88b2-0e7a4b5d215c","tool_use_result":{"stdout":"file contents here","stderr":"","interrupted":false}}',
    '{"type":"assistant","message":{"content":[{"type":"text","text":"I see the file contains..."}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"408d2155-b3f8-4044-a00e-cedd765d3eaa"}',
]

ERROR_RESPONSE = [
    '{"type":"user","message":{"role":"user","content":[{"type":"tool_result","content":"<tool_use_error>File does not exist.</tool_use_error>","is_error":true,"tool_use_id":"toolu_123"}]},"session_id":"df83d374-79dd-4100-be18-fd7e4bccc33b","uuid":"1b9893ae-1fbd-4b73-88b2-0e7a4b5d215c","tool_use_result":"Error: File does not exist."}',
]
```

**Step 6: Commit**

```bash
git add src/discord_ai/models.py tests/unit/test_models.py tests/helpers/data/claude_responses.py
git commit -m "feat: add stream event models with pydantic"
```

---

## Task 4: Claude Client Protocol and Implementations

**Files:**
- Create: `src/discord_ai/claude/client.py`
- Create: `tests/unit/claude/test_client.py`

**Step 1: Write failing test for FakeClaudeClient**

```python
# tests/unit/claude/test_client.py
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
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/claude/test_client.py -v`
Expected: FAIL with "No module named 'discord_ai.claude.client'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/claude/client.py
from typing import Protocol, AsyncIterator


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
        # Will implement in next task
        raise NotImplementedError("RealClaudeClient not yet implemented")
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/claude/test_client.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/claude/client.py tests/unit/claude/test_client.py
git commit -m "feat: add ClaudeClient protocol with Fake implementation"
```

---

## Task 5: RealClaudeClient Implementation

**Files:**
- Modify: `src/discord_ai/claude/client.py`
- Create: `tests/integration/test_claude_client.py`

**Step 1: Write integration test**

```python
# tests/integration/test_claude_client.py
import pytest
from discord_ai.claude.client import RealClaudeClient
from discord_ai.settings import Settings
import json


@pytest.mark.asyncio
async def test_real_client_spawns_subprocess(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()
    client = RealClaudeClient(settings)

    # Simple command that should work
    lines = []
    async for line in client.run_session("test-session-id", "echo hello"):
        lines.append(line)
        # Just collect a few lines, don't need full response
        if len(lines) >= 3:
            break

    # Verify we got JSON
    assert len(lines) > 0
    first_event = json.loads(lines[0])
    assert "type" in first_event
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/integration/test_claude_client.py -v`
Expected: FAIL with "NotImplementedError: RealClaudeClient not yet implemented"

**Step 3: Implement RealClaudeClient**

```python
# src/discord_ai/claude/client.py (modify RealClaudeClient class)
import asyncio
from typing import AsyncIterator


class RealClaudeClient:
    """Real implementation spawning Claude CLI subprocess"""

    def __init__(self, settings):
        self.settings = settings

    async def run_session(self, session_id: str, message: str) -> AsyncIterator[str]:
        cmd = [
            self.settings.claude_cli_path,
            "--print",
            "--output-format", "stream-json",
            "--verbose",
            "--session-id", session_id,
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
                    yield line.decode().strip()

            # Wait for process with timeout
            await asyncio.wait_for(
                process.wait(), 
                timeout=self.settings.claude_timeout_seconds
            )
        except asyncio.TimeoutError:
            # Kill process if it times out
            process.kill()
            await process.wait()
            raise
        finally:
            # Consume stderr to prevent deadlock
            if process.stderr:
                await process.stderr.read()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/integration/test_claude_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/discord_ai/claude/client.py tests/integration/test_claude_client.py
git commit -m "feat: implement RealClaudeClient with subprocess"
```

---

## Task 6: Stream Parser

**Files:**
- Create: `src/discord_ai/claude/parser.py`
- Create: `tests/unit/claude/test_parser.py`

**Step 1: Write failing test**

```python
# tests/unit/claude/test_parser.py
import pytest
from discord_ai.claude.parser import StreamParser
from discord_ai.claude.client import FakeClaudeClient
from discord_ai.models import AssistantMessage, TextContent
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

    # Should only get assistant message, system event filtered
    assert len(events) == 1
    assert isinstance(events[0], AssistantMessage)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/claude/test_parser.py -v`
Expected: FAIL with "No module named 'discord_ai.claude.parser'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/claude/parser.py
from typing import AsyncIterator
import json
from discord_ai.models import StreamEvent, SystemEvent, ResultEvent


class StreamParser:
    """Parses Claude stream-json output into typed events"""

    def __init__(self, client):
        self.client = client

    async def parse_stream(self, session_id: str, message: str) -> AsyncIterator[StreamEvent]:
        async for line in self.client.run_session(session_id, message):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                event_type = data.get("type")

                # Skip system and result events
                if event_type in ("system", "result"):
                    continue

                # Parse to appropriate model
                if event_type == "assistant":
                    from discord_ai.models import AssistantMessage
                    yield AssistantMessage(**data)
                elif event_type == "user":
                    from discord_ai.models import UserMessage
                    yield UserMessage(**data)

            except (json.JSONDecodeError, Exception):
                # Skip malformed lines
                continue
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/claude/test_parser.py -v`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/claude/parser.py tests/unit/claude/test_parser.py
git commit -m "feat: add stream parser for Claude JSON events"
```

---

## Task 7: Event Formatter for Discord

**Files:**
- Create: `src/discord_ai/claude/formatter.py`
- Create: `tests/unit/claude/test_formatter.py`

**Step 1: Write failing test**

```python
# tests/unit/claude/test_formatter.py
import pytest
from discord_ai.claude.formatter import EventFormatter
from discord_ai.models import (
    AssistantMessage,
    UserMessage,
    TextContent,
    ToolUseContent,
)
from uuid import UUID


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
            "content": [{
                "type": "tool_use",
                "id": "tool_123",
                "name": "Read",
                "input": {"file_path": "test.py"}
            }]
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
        message={"content": [{"type": "tool_result", "is_error": True, "content": "File not found"}]},
        session_id=UUID("df83d374-79dd-4100-be18-fd7e4bccc33b"),
        uuid=UUID("408d2155-b3f8-4044-a00e-cedd765d3eaa"),
        tool_use_result="Error: File not found",
    )
    formatter = EventFormatter()

    messages = formatter.format_event(event)

    assert len(messages) == 1
    assert messages[0].startswith("||")
    assert "File not found" in messages[0]
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/claude/test_formatter.py -v`
Expected: FAIL with "No module named 'discord_ai.claude.formatter'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/claude/formatter.py
from discord_ai.models import AssistantMessage, UserMessage, TextContent, ToolUseContent


class EventFormatter:
    """Formats Claude events for Discord messages"""

    def format_event(self, event) -> list[str]:
        """Returns list of Discord message strings for this event"""

        if isinstance(event, AssistantMessage):
            return self._format_assistant_message(event)
        elif isinstance(event, UserMessage):
            return self._format_user_message(event)
        else:
            return []

    def _format_assistant_message(self, event: AssistantMessage) -> list[str]:
        messages = []

        for block in event.content_blocks:
            if isinstance(block, TextContent):
                messages.append(block.text)
            elif isinstance(block, ToolUseContent):
                tool_msg = f"Tool: {block.name}"
                if block.input:
                    # Format input nicely
                    args = ", ".join(f"{k}={v}" for k, v in block.input.items())
                    tool_msg += f" ({args})"
                messages.append(tool_msg)

        return messages

    def _format_user_message(self, event: UserMessage) -> list[str]:
        if not event.tool_use_result:
            return []

        # Format result in spoilers
        result = event.tool_use_result
        if isinstance(result, dict):
            content = result.get("stdout", "") or str(result)
        else:
            content = str(result)

        return [f"||{content}||"]
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/claude/test_formatter.py -v`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/claude/formatter.py tests/unit/claude/test_formatter.py
git commit -m "feat: add event formatter for Discord messages"
```

---

## Task 8: Typing Indicator Loop

**Files:**
- Create: `src/discord_ai/utils/typing.py`
- Create: `tests/unit/utils/test_typing.py`

**Step 1: Write failing test**

```python
# tests/unit/utils/test_typing.py
import pytest
import asyncio
from discord_ai.utils.typing import typing_loop


class FakeChannel:
    def __init__(self):
        self.typing_count = 0

    async def trigger_typing(self):
        self.typing_count += 1


@pytest.mark.asyncio
async def test_typing_loop_sends_typing_indicator():
    channel = FakeChannel()

    task = asyncio.create_task(typing_loop(channel, interval=0.1))
    await asyncio.sleep(0.25)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    # Should have sent typing at least twice (0.1s intervals)
    assert channel.typing_count >= 2


@pytest.mark.asyncio
async def test_typing_loop_stops_on_cancel():
    channel = FakeChannel()

    task = asyncio.create_task(typing_loop(channel, interval=0.1))
    await asyncio.sleep(0.05)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    initial_count = channel.typing_count
    await asyncio.sleep(0.2)

    # Should not increase after cancel
    assert channel.typing_count == initial_count
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/utils/test_typing.py -v`
Expected: FAIL with "No module named 'discord_ai.utils.typing'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/utils/typing.py
import asyncio


async def typing_loop(channel, interval: int = 5):
    """Continuously sends typing indicator until cancelled"""
    try:
        while True:
            await channel.trigger_typing()
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        # Clean cancellation
        raise
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/utils/test_typing.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/utils/typing.py tests/unit/utils/test_typing.py
git commit -m "feat: add typing indicator loop utility"
```

---

## Task 9: Discord Client Protocol

**Files:**
- Create: `src/discord_ai/discord_client.py`
- Create: `tests/unit/test_discord_client.py`

**Step 1: Write failing test**

```python
# tests/unit/test_discord_client.py
import pytest
from discord_ai.discord_client import FakeDiscordClient


@pytest.mark.asyncio
async def test_fake_discord_sends_message():
    client = FakeDiscordClient()

    await client.send_message("channel_123", "Hello world")

    messages = client.get_messages("channel_123")
    assert len(messages) == 1
    assert messages[0].content == "Hello world"


@pytest.mark.asyncio
async def test_fake_discord_multiple_messages():
    client = FakeDiscordClient()

    await client.send_message("channel_123", "Message 1")
    await client.send_message("channel_123", "Message 2")

    messages = client.get_messages("channel_123")
    assert len(messages) == 2
    assert messages[0].content == "Message 1"
    assert messages[1].content == "Message 2"


@pytest.mark.asyncio
async def test_fake_discord_trigger_typing():
    client = FakeDiscordClient()
    channel = client.get_channel("channel_123")

    await channel.trigger_typing()

    assert channel.typing_count == 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_discord_client.py -v`
Expected: FAIL with "No module named 'discord_ai.discord_client'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/discord_client.py
from typing import Protocol
from dataclasses import dataclass, field


@dataclass
class FakeMessage:
    content: str
    channel_id: str


@dataclass
class FakeChannel:
    channel_id: str
    typing_count: int = 0

    async def trigger_typing(self):
        self.typing_count += 1


class DiscordClient(Protocol):
    """Protocol for Discord API interaction"""

    async def send_message(self, channel_id: str, content: str):
        ...

    def get_channel(self, channel_id: str):
        ...


class FakeDiscordClient:
    """Test implementation storing messages in memory"""

    def __init__(self):
        self._messages: dict[str, list[FakeMessage]] = {}
        self._channels: dict[str, FakeChannel] = {}

    async def send_message(self, channel_id: str, content: str):
        if channel_id not in self._messages:
            self._messages[channel_id] = []

        msg = FakeMessage(content=content, channel_id=channel_id)
        self._messages[channel_id].append(msg)

    def get_messages(self, channel_id: str) -> list[FakeMessage]:
        return self._messages.get(channel_id, [])

    def get_channel(self, channel_id: str) -> FakeChannel:
        if channel_id not in self._channels:
            self._channels[channel_id] = FakeChannel(channel_id=channel_id)
        return self._channels[channel_id]


class RealDiscordClient:
    """Real implementation using discord.py"""

    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, channel_id: str, content: str):
        channel = self.bot.get_channel(int(channel_id))
        if channel:
            await channel.send(content)

    def get_channel(self, channel_id: str):
        return self.bot.get_channel(int(channel_id))
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_discord_client.py -v`
Expected: PASS (all 3 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/discord_client.py tests/unit/test_discord_client.py
git commit -m "feat: add DiscordClient protocol with Fake implementation"
```

---

## Task 10: Message Handler

**Files:**
- Create: `src/discord_ai/handlers/messages.py`
- Create: `tests/unit/handlers/test_messages.py`

**Step 1: Write failing test**

```python
# tests/unit/handlers/test_messages.py
import pytest
from discord_ai.handlers.messages import MessageHandler
from discord_ai.claude.client import FakeClaudeClient
from discord_ai.discord_client import FakeDiscordClient
from tests.helpers.data.claude_responses import SIMPLE_TEXT


@pytest.mark.asyncio
async def test_handles_message_and_sends_response():
    claude = FakeClaudeClient(SIMPLE_TEXT)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings=None)

    await handler.handle_message(
        channel_id="channel_123",
        session_id="session-id-123",
        content="hello"
    )

    messages = discord.get_messages("channel_123")
    assert len(messages) == 1
    assert "Hello" in messages[0].content


@pytest.mark.asyncio
async def test_sends_typing_indicator_while_processing():
    claude = FakeClaudeClient(SIMPLE_TEXT)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings=None)

    await handler.handle_message(
        channel_id="channel_123",
        session_id="session-id-123",
        content="hello"
    )

    channel = discord.get_channel("channel_123")
    # Should have triggered typing at least once
    assert channel.typing_count >= 1
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/handlers/test_messages.py -v`
Expected: FAIL with "No module named 'discord_ai.handlers.messages'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/handlers/messages.py
import asyncio
from discord_ai.claude.parser import StreamParser
from discord_ai.claude.formatter import EventFormatter
from discord_ai.utils.typing import typing_loop


class MessageHandler:
    """Handles incoming Discord messages"""

    def __init__(self, claude_client, discord_client, settings):
        self.claude_client = claude_client
        self.discord_client = discord_client
        self.settings = settings
        self.parser = StreamParser(claude_client)
        self.formatter = EventFormatter()

    async def handle_message(self, channel_id: str, session_id: str, content: str):
        channel = self.discord_client.get_channel(channel_id)

        # Start typing indicator
        typing_task = asyncio.create_task(typing_loop(channel, interval=5))

        try:
            # Parse stream and send messages
            async for event in self.parser.parse_stream(session_id, content):
                messages = self.formatter.format_event(event)
                for msg in messages:
                    await self.discord_client.send_message(channel_id, msg)
        finally:
            # Always stop typing
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/handlers/test_messages.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/handlers/messages.py tests/unit/handlers/test_messages.py
git commit -m "feat: add message handler with typing indicator"
```

---

## Task 11: Logging Setup

**Files:**
- Create: `src/discord_ai/logging_config.py`
- Create: `tests/unit/test_logging_config.py`

**Step 1: Write failing test**

```python
# tests/unit/test_logging_config.py
import pytest
from discord_ai.logging_config import setup_logging
from discord_ai.settings import Settings
import structlog


def test_setup_logging_configures_structlog(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = Settings()

    setup_logging(settings)

    logger = structlog.get_logger()
    assert logger is not None


def test_setup_logging_respects_log_level(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    settings = Settings()

    # Should not raise
    setup_logging(settings)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_logging_config.py -v`
Expected: FAIL with "No module named 'discord_ai.logging_config'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/logging_config.py
import structlog
import logging


def setup_logging(settings):
    """Configure structlog for the application"""

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_logging_config.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/logging_config.py tests/unit/test_logging_config.py
git commit -m "feat: add structured logging configuration"
```

---

## Task 12: Bot Initialization

**Files:**
- Create: `src/discord_ai/bot.py`
- Create: `tests/unit/test_bot.py`

**Step 1: Write failing test**

```python
# tests/unit/test_bot.py
import pytest
from discord_ai.bot import create_bot
from discord_ai.settings import Settings


def test_create_bot_returns_discord_bot(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    bot = create_bot(settings)

    assert bot is not None
    assert hasattr(bot, "run")


def test_create_bot_configures_intents(monkeypatch):
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    bot = create_bot(settings)

    # Verify intents are set
    assert bot.intents.message_content is True
    assert bot.intents.guilds is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_bot.py -v`
Expected: FAIL with "No module named 'discord_ai.bot'"

**Step 3: Write minimal implementation**

```python
# src/discord_ai/bot.py
import discord
from discord.ext import commands


def create_bot(settings):
    """Create and configure Discord bot"""

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    return bot
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_bot.py -v`
Expected: PASS (all 2 tests)

**Step 5: Commit**

```bash
git add src/discord_ai/bot.py tests/unit/test_bot.py
git commit -m "feat: add bot creation with intents"
```

---

## Task 13: Main Entry Point

**Files:**
- Create: `src/discord_ai/main.py`

**Step 1: Write main.py**

```python
# src/discord_ai/main.py
import sys
import structlog
from discord_ai.settings import Settings
from discord_ai.logging_config import setup_logging
from discord_ai.bot import create_bot
from discord_ai.claude.client import RealClaudeClient
from discord_ai.discord_client import RealDiscordClient
from discord_ai.handlers.messages import MessageHandler


logger = structlog.get_logger()


def main():
    """Entry point for Discord AI bot"""

    # Load settings
    try:
        settings = Settings()
    except Exception as e:
        print(f"Failed to load settings: {e}")
        print("Make sure DISCORD_BOT_TOKEN is set in .env")
        sys.exit(1)

    # Setup logging
    setup_logging(settings)
    logger.info("discord_ai.starting", version="0.1.0")

    # Create bot
    bot = create_bot(settings)

    # Create clients
    claude_client = RealClaudeClient(settings)
    discord_client = RealDiscordClient(bot)

    # Create handler
    message_handler = MessageHandler(claude_client, discord_client, settings)

    # Setup event handlers (will implement in next tasks)
    # @bot.event
    # async def on_ready():
    #     ...

    # @bot.event
    # async def on_message(message):
    #     ...

    # Run bot
    logger.info("discord_ai.bot.starting")
    try:
        bot.run(settings.discord_token)
    except Exception as e:
        logger.error("discord_ai.bot.error", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 2: Test manually**

Run: `uv run python -m discord_ai.main`
Expected: Should fail with "DISCORD_BOT_TOKEN not set" (expected, we haven't configured it)

**Step 3: Commit**

```bash
git add src/discord_ai/main.py
git commit -m "feat: add main entry point"
```

---

## Task 14: Ready Handler with Category Validation

**Files:**
- Create: `src/discord_ai/handlers/ready.py`
- Modify: `src/discord_ai/main.py`

**Step 1: Write ready handler**

```python
# src/discord_ai/handlers/ready.py
import sys
import structlog


logger = structlog.get_logger()


async def on_ready(bot, settings):
    """Handle bot ready event"""

    logger.info("discord_ai.bot.ready", user=str(bot.user))

    # Validate category exists
    if not bot.guilds:
        logger.error("discord_ai.bot.no_guilds")
        await bot.close()
        sys.exit(1)

    guild = bot.guilds[0]
    category = None

    for cat in guild.categories:
        if cat.name == settings.category_name:
            category = cat
            break

    if not category:
        available = [cat.name for cat in guild.categories]
        error_msg = f"""
Category '{settings.category_name}' not found in server.

To fix this, either:
1. Create a category named '{settings.category_name}' in your Discord server
2. Update CATEGORY_NAME in your .env file to match an existing category

Available categories in server:
{chr(10).join(f'  - {name}' for name in available)}
"""
        logger.error("discord_ai.category.not_found",
                    category=settings.category_name,
                    available=available)
        print(error_msg)
        await bot.close()
        sys.exit(1)

    logger.info("discord_ai.category.found",
               category=category.name,
               channels=len(category.channels))
```

**Step 2: Integrate with main.py**

```python
# src/discord_ai/main.py (add to main function after creating bot)
from discord_ai.handlers.ready import on_ready as ready_handler

# ... existing code ...

# Setup event handlers
@bot.event
async def on_ready():
    await ready_handler(bot, settings)

# ... rest of code ...
```

**Step 3: Commit**

```bash
git add src/discord_ai/handlers/ready.py src/discord_ai/main.py
git commit -m "feat: add ready handler with category validation"
```

---

## Task 15: Channel Detection and Initialization

**Files:**
- Create: `src/discord_ai/handlers/channels.py`
- Modify: `src/discord_ai/main.py`

**Step 1: Write channel handler**

```python
# src/discord_ai/handlers/channels.py
import structlog
from uuid import uuid4


logger = structlog.get_logger()


async def initialize_channel(channel):
    """Initialize a channel with a session UUID"""

    # Check if topic already has UUID format
    if channel.topic and channel.topic.startswith("Session: "):
        # Already initialized
        logger.info("discord_ai.channel.existing",
                   channel=channel.name,
                   topic=channel.topic)
        return

    # Generate new UUID and set topic
    session_id = str(uuid4())
    new_topic = f"Session: {session_id}"

    try:
        await channel.edit(topic=new_topic)
        logger.info("discord_ai.channel.initialized",
                   channel=channel.name,
                   session_id=session_id)
    except Exception as e:
        logger.error("discord_ai.channel.init_failed",
                    channel=channel.name,
                    error=str(e))


async def on_channel_create(channel, settings):
    """Handle new channel creation"""

    # Check if channel is in our category
    if not channel.category:
        return

    if channel.category.name != settings.category_name:
        return

    logger.info("discord_ai.channel.created", channel=channel.name)
    await initialize_channel(channel)
```

**Step 2: Integrate with main.py and ready handler**

```python
# src/discord_ai/handlers/ready.py (add to end of on_ready function)
from discord_ai.handlers.channels import initialize_channel

# ... existing code in on_ready ...

# Initialize existing channels
for channel in category.channels:
    await initialize_channel(channel)

logger.info("discord_ai.bot.ready_complete")
```

```python
# src/discord_ai/main.py (add event handler)
from discord_ai.handlers.channels import on_channel_create as channel_create_handler

# ... existing code ...

@bot.event
async def on_guild_channel_create(channel):
    await channel_create_handler(channel, settings)

# ... rest of code ...
```

**Step 3: Commit**

```bash
git add src/discord_ai/handlers/channels.py src/discord_ai/handlers/ready.py src/discord_ai/main.py
git commit -m "feat: add channel detection and initialization"
```

---

## Task 16: Message Event Handler

**Files:**
- Modify: `src/discord_ai/main.py`

**Step 1: Add message event handler**

```python
# src/discord_ai/main.py (add after other event handlers)
import re

# ... existing code ...

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only handle messages in monitored category
    if not message.channel.category:
        return

    if message.channel.category.name != settings.category_name:
        return

    # Extract session ID from channel topic
    topic = message.channel.topic or ""
    
    if not topic.startswith("Session: "):
        logger.warning("discord_ai.message.no_session_id",
                      channel=message.channel.name)
        await message.channel.send("||Error: No session ID found in channel topic||")
        return

    session_id = topic.replace("Session: ", "").strip()

    logger.info("discord_ai.message.received",
               channel=message.channel.name,
               session_id=session_id,
               user=str(message.author))

    try:
        await message_handler.handle_message(
            channel_id=str(message.channel.id),
            session_id=session_id,
            content=message.content
        )
    except Exception as e:
        logger.error("discord_ai.message.error",
                    error=str(e),
                    channel=message.channel.name)
        await message.channel.send(f"||Error: {str(e)}||")

# ... rest of code ...
```

**Step 2: Commit**

```bash
git add src/discord_ai/main.py
git commit -m "feat: add message event handler"
```

---

## Task 17: Create README

**Files:**
- Create: `README.md`

**Step 1: Write README**

```markdown
# Discord AI Bot

A Discord bot that bridges Discord channels to Claude CLI sessions, enabling conversational AI interactions directly in Discord.

## Features

- Each channel in "Claude Conversations" category gets its own persistent Claude session
- Real-time streaming responses
- Tool execution visibility (with spoiler tags for details)
- Typing indicators while processing
- Structured logging with structlog

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Claude CLI installed and configured
- Discord bot token

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd discord-ai
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Configure your `.env`:
```env
DISCORD_BOT_TOKEN=your_bot_token_here
CATEGORY_NAME=Claude Conversations
```

### Discord Setup

1. Create bot at https://discord.com/developers/applications
2. Enable intents in Bot settings:
   - Message Content Intent
   - Server Members Intent
3. Generate and copy bot token
4. Invite bot to your server with permissions:
   - Send Messages
   - Manage Channels
   - Read Messages/View Channels
5. Create a category named "Claude Conversations" in your Discord server
6. Create channels within this category for conversations

## Running

```bash
uv run discord-ai-bot
```

Or:
```bash
uv run python -m discord_ai.main
```

## Usage

1. Create a new text channel under the "Claude Conversations" category
2. Bot will automatically initialize it with a session UUID
3. Send messages in the channel to interact with Claude
4. Claude's responses, tool calls, and results will appear as messages

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit -v

# Integration tests
uv run pytest tests/integration -v

# With coverage
uv run pytest --cov=discord_ai
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Lint and auto-fix
uv run ruff check --fix .

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

### Project Structure

```
discord-ai/
├── src/discord_ai/       # Main application code
│   ├── claude/           # Claude CLI integration
│   ├── handlers/         # Discord event handlers
│   └── utils/            # Utilities
└── tests/                # Tests
    ├── unit/             # Fast unit tests with fakes
    └── integration/      # Integration tests
```

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

## Task 18: Final Integration Test

**Files:**
- Create: `tests/integration/test_end_to_end.py`

**Step 1: Write end-to-end test**

```python
# tests/integration/test_end_to_end.py
"""
End-to-end test with fake Discord but real Claude.
This verifies the full flow works together.
"""
import pytest
from discord_ai.settings import Settings
from discord_ai.claude.client import RealClaudeClient
from discord_ai.discord_client import FakeDiscordClient
from discord_ai.handlers.messages import MessageHandler


@pytest.mark.asyncio
async def test_full_message_flow_with_real_claude(monkeypatch):
    """
    Integration test: Real Claude CLI, Fake Discord
    Verifies messages flow through the system correctly
    """
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "test_token")
    settings = Settings()

    claude = RealClaudeClient(settings)
    discord = FakeDiscordClient()
    handler = MessageHandler(claude, discord, settings)

    # Send simple message
    await handler.handle_message(
        channel_id="test_channel",
        session_id="integration-test-session",
        content="Say hello in one word"
    )

    # Verify we got responses
    messages = discord.get_messages("test_channel")
    assert len(messages) > 0

    # Verify typing was triggered
    channel = discord.get_channel("test_channel")
    assert channel.typing_count > 0
```

**Step 2: Run test**

Run: `uv run pytest tests/integration/test_end_to_end.py -v -s`
Expected: PASS (may take a few seconds for real Claude)

**Step 3: Commit**

```bash
git add tests/integration/test_end_to_end.py
git commit -m "test: add end-to-end integration test"
```

---

## Completion Checklist

Before marking complete:

### Code Reviews
- [ ] 🔍 Review Wave 0: Settings, Models, Typing, Logging
- [ ] 🔍 Review Wave 1: Claude Client, Discord Client Protocols
- [ ] 🔍 Review Wave 2: RealClaudeClient, EventFormatter
- [ ] 🔍 Review Wave 3: StreamParser, MessageHandler, Bot, Main
- [ ] 🔍 Review Wave 4: Ready, Channels, MessageHandler Integration, README, Tests

### Testing
- [ ] All unit tests pass: `uv run pytest tests/unit -v`
- [ ] All integration tests pass: `uv run pytest tests/integration -v`

### Code Quality
- [ ] All ruff checks pass: `uv run ruff check .`
- [ ] Code formatted: `uv run ruff format .`

### Documentation & Setup
- [ ] README exists and is accurate
- [ ] `.env.example` exists
- [ ] Bot can start (even if it fails on missing token, that's expected)
- [ ] All files committed to git
- [ ] Design doc exists in `docs/plans/`
- [ ] Implementation plan exists in `docs/plans/`

## Next Steps After Implementation

1. Test with real Discord server
2. Add slash commands (/new, /fork)
3. Add message queuing
4. Improve error handling
5. Add metrics/monitoring
6. Deploy to production

---

## Notes

- **Waves**: Execute in parallel where possible. Review after each wave.
- **TDD Required**: Every task follows RED-GREEN-REFACTOR
- **Dependency Injection**: Use Protocol interfaces for testability
- **Logging**: Use structlog for all logging
- **Error Handling**: Errors sent to Discord in spoilers
- **Commit Often**: Commit after each task completion
- **Code Quality**: Run ruff check and format before committing
