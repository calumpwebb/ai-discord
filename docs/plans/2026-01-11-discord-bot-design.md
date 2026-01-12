# Discord AI Bot Design

## Overview

A Discord bot that bridges Discord channels to Claude CLI sessions. Each channel in the "Claude Conversations" category maps to a persistent Claude CLI session, enabling conversational AI interactions directly in Discord.

## Architecture

### Channel-to-Session Mapping

- Bot monitors all channels in the "Claude Conversations" Discord category
- Each channel's topic stores its unique session UUID
- On channel creation, bot generates UUID and updates channel topic
- Session UUIDs persist in channel topics (source of truth)
- Bot rebuilds in-memory mapping on startup by scanning category

### Message Flow

1. User sends message in monitored channel
2. Bot extracts session UUID from channel topic
3. Bot starts Discord typing indicator (refreshed every 5 seconds)
4. Bot spawns `claude --print --output-format stream-json --verbose --session-id <uuid> --resume <uuid> "<message>"`
5. Bot parses streaming JSON events from stdout
6. Bot sends Discord messages in real-time as events arrive:
   - Text content → regular message
   - Tool calls → formatted message with tool name and args
   - Tool results → message in spoiler tags `||result||`
7. When subprocess completes, typing indicator stops
8. Errors handled gracefully, sent to channel in spoiler tags

### Technology Stack

- **Language**: Python 3.12+
- **Package Manager**: uv
- **Discord Library**: discord.py
- **Settings**: pydantic-settings
- **Logging**: structlog
- **Testing**: pytest, pytest-asyncio, pytest-mock

### Dependency Injection

Use Protocol interfaces for testability:

**ClaudeClient Protocol**:
- `RealClaudeClient` - spawns actual subprocess
- `FakeClaudeClient` - returns canned JSON lines for testing

**DiscordClient Protocol**:
- `RealDiscordClient` - wraps discord.py API
- `FakeDiscordClient` - stores messages in memory for testing

## Project Structure

```
discord-ai/
├── .env
├── .gitignore
├── pyproject.toml
├── README.md
├── docs/
│   └── plans/
│       └── 2026-01-11-discord-bot-design.md
├── src/
│   └── discord_ai/
│       ├── main.py              # Entry point
│       ├── bot.py               # Bot initialization
│       ├── settings.py          # Pydantic settings
│       ├── models.py            # Pydantic models for events
│       ├── handlers/
│       │   ├── ready.py         # on_ready, startup
│       │   ├── channels.py      # Channel creation/detection
│       │   └── messages.py      # Message handling
│       ├── commands/            # Future: bot commands
│       │   └── conversation.py
│       ├── claude/
│       │   ├── client.py        # Claude CLI subprocess
│       │   ├── parser.py        # Stream JSON parsing
│       │   └── formatter.py     # Format events for Discord
│       └── utils/
│           └── typing.py        # Typing indicator loop
└── tests/
    ├── conftest.py              # pytest fixtures
    ├── helpers/
    │   ├── builders.py          # Fluent builders for test data
    │   ├── fixtures.py          # Reusable test objects
    │   ├── assertions.py        # Custom assertions
    │   ├── validators.py        # Validate test data matches real
    │   └── data/
    │       ├── claude_responses.py   # Canned Claude JSON
    │       └── discord_objects.py    # Sample Discord data
    ├── unit/                    # Fast tests with Fakes
    │   ├── test_settings.py
    │   ├── test_models.py
    │   ├── handlers/
    │   │   ├── test_ready.py
    │   │   ├── test_channels.py
    │   │   └── test_messages.py
    │   ├── claude/
    │   │   ├── test_client.py
    │   │   ├── test_parser.py
    │   │   └── test_formatter.py
    │   └── utils/
    │       └── test_typing.py
    └── integration/             # Selective tests with Real
        ├── test_claude_client.py
        └── test_discord_client.py
```

## Data Models

### Settings (pydantic-settings)

```python
class Settings(BaseSettings):
    discord_token: str
    category_name: str = "Claude Conversations"
    claude_cli_path: str = "claude"
    typing_interval_seconds: int = 5
    claude_timeout_seconds: int = 600
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
```

### Stream Events (pydantic)

Based on real Claude CLI output:

**Event Types**:
- `SystemEvent` - Internal Claude events (ignore for Discord)
- `AssistantMessage` - Claude's responses and tool calls
- `UserMessage` - Tool results
- `ResultEvent` - Session end marker (ignore for Discord)

**Content Types**:
- `TextContent` - Claude's text response
- `ToolUseContent` - Tool call with name and args
- `ToolResultContent` - Tool execution result

**Discord Mapping**:
- AssistantMessage(TextContent) → Send as message
- AssistantMessage(ToolUseContent) → Send formatted: "Tool: name"
- UserMessage(tool_result) → Send in spoilers: "||result||"
- Errors → Send in spoilers: "||Error: message||"

## Error Handling

### Claude CLI Failures

- Subprocess timeout (600s default)
- Non-zero exit code
- JSON parsing errors
- All errors logged with structlog
- User sees error in spoiler tags
- Typing indicator always stops (try/finally)

### Discord API Failures

- Channel not found
- Category not found
- Permission errors
- All logged, bot continues running
- Graceful degradation where possible

### Startup Validation

On bot startup:
1. Validate Discord token
2. Find category by name
3. If category not found:
   - Log error with available categories
   - Exit cleanly with exit code 1

## Testing Strategy

### Test-Driven Development

**Strict RED-GREEN-REFACTOR cycle**:
- Write failing test
- Watch it fail (verify correct failure)
- Write minimal code to pass
- Watch it pass
- Refactor if needed

**No exceptions**: Every function has a test written first.

### Test Helpers

**Builders** - Fluent API for test data:
```python
ClaudeResponseBuilder()
    .with_text("hello")
    .with_tool_call("Read", "file.py")
    .with_tool_result("contents")
    .build()
```

**Fixtures** - Reusable test objects via pytest fixtures

**Validators** - Ensure canned data matches real pydantic models

**Custom Assertions** - Clear, readable test assertions

### Test Data Validation

- Canned responses validated against pydantic models on test startup
- Integration tests compare real output to expected schema
- Capture script for updating test data when Claude changes

## Logging

Using structlog for structured logging:

**Log Events**:
- Bot startup/shutdown
- Channel detection/initialization
- Message received (channel_id, user_id, session_id)
- Claude CLI spawn (command, session_id)
- Stream events received (type, uuid)
- Tool calls and results
- Discord API calls (send_message, update_topic)
- Errors (with context)

**Log Levels**:
- DEBUG: Stream events, tool calls
- INFO: Messages, sessions, channel events
- WARNING: Retryable errors
- ERROR: Failures requiring attention

## Future Enhancements

Not in initial implementation:

1. **Startup Message** - Bot posts greeting in channels
2. **Command Channel** - Dedicated channel for bot commands
3. **Commands** - /new, /fork, /archive
4. **Message Queuing** - Queue messages while processing
5. **Channel Locking** - Prevent messages during processing
6. **Advanced Formatting** - Code blocks, syntax highlighting
7. **Session Management** - Timeout inactive sessions
8. **Multi-server Support** - Support multiple Discord servers

## Implementation Order

Following TDD, build in this order:

1. **Settings** - Simple, no dependencies
2. **Models** - Parse real Claude JSON
3. **ClaudeClient** - Subprocess management
4. **Parser** - Parse stream events
5. **Formatter** - Format for Discord
6. **Typing Loop** - Background task
7. **Message Handler** - Orchestrate flow
8. **Channel Handler** - Detect and initialize
9. **Ready Handler** - Startup validation
10. **Bot** - Wire everything together
11. **Main** - Entry point

Each module: write test, watch fail, write code, watch pass.

## Running the Bot

Install dependencies:
```bash
uv sync
```

Configure:
```bash
cp .env.example .env
# Edit .env with your DISCORD_BOT_TOKEN
```

Run:
```bash
uv run python -m discord_ai.main
```

Or with script entry point:
```bash
uv run discord-ai-bot
```

## Discord Setup

1. Create bot at https://discord.com/developers/applications
2. Enable intents: Message Content, Guilds
3. Generate bot token
4. Invite bot to server with permissions: Send Messages, Manage Channels, Read Messages
5. Create category "Claude Conversations"
6. Create channels within category
