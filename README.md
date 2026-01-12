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
