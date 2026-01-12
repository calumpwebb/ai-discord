# Discord AI Bot - Agent Guidelines

This document provides comprehensive guidelines for AI agents working on the Discord AI bot codebase. It covers build commands, testing procedures, code style conventions, and development workflows.

## Table of Contents

1. [Build and Development Commands](#build-and-development-commands)
2. [Testing Guidelines](#testing-guidelines)
3. [Code Style and Conventions](#code-style-and-conventions)
4. [Project Structure](#project-structure)
5. [Development Workflow](#development-workflow)
6. [Error Handling and Logging](#error-handling-and-logging)
7. [Type Safety](#type-safety)
8. [Dependencies and Imports](#dependencies-and-imports)

## Build and Development Commands

### Package Management
```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --dev

# Update dependencies
uv lock --upgrade
```

### Running the Application
```bash
# Run the bot
uv run discord-ai-bot

# Run via module
uv run python -m discord_ai.main

# Run with debug logging
LOG_LEVEL=DEBUG uv run discord-ai-bot
```

### Code Quality Tools
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Lint and auto-fix
uv run ruff check --fix .

# Run all pre-commit hooks
uv run pre-commit run --all-files

# Run pre-commit on staged files
uv run pre-commit run
```

## Testing Guidelines

### Test Commands
```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest tests/unit -v

# Run integration tests only
uv run pytest tests/integration -v

# Run tests with coverage
uv run pytest --cov=discord_ai

# Run a specific test file
uv run pytest tests/unit/test_settings.py

# Run a specific test function
uv run pytest tests/unit/test_settings.py::test_loads_from_environment -v

# Run tests in parallel
uv run pytest -n auto
```

### Test Structure
- **Unit tests** (`tests/unit/`): Fast, isolated tests with mocks/fakes
- **Integration tests** (`tests/integration/`): End-to-end tests with real dependencies
- Use `pytest-asyncio` for async test functions
- Use `pytest-mock` for mocking dependencies
- Follow naming convention: `test_<functionality>.py`

### Test Coverage
- Aim for high unit test coverage
- Integration tests should cover critical user journeys
- Use coverage reports to identify gaps: `uv run pytest --cov=discord_ai --cov-report=html`

## Code Style and Conventions

### Python Version and Standards
- **Python version**: 3.12+ (configured in `pyproject.toml`)
- **Line length**: 100 characters (configured in `ruff`)
- **Target version**: py312 (for Ruff and type checking)

### Ruff Configuration
```toml
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
```

### Naming Conventions
- **Variables/Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Modules**: `snake_case`
- **Packages**: `snake_case`

### Code Formatting
- Use Ruff formatter for consistent formatting
- Let the formatter handle line breaks and spacing
- Focus on logical structure over manual formatting

## Project Structure

```
discord-ai/
├── src/discord_ai/              # Main application code
│   ├── __init__.py             # Package initialization
│   ├── main.py                 # Application entry point
│   ├── bot.py                  # Discord bot setup
│   ├── discord_client.py       # Discord API client wrapper
│   ├── settings.py             # Configuration management
│   ├── logging_config.py       # Logging setup
│   ├── models.py               # Pydantic data models
│   ├── claude/                 # Claude CLI integration
│   │   ├── __init__.py
│   │   ├── client.py           # Claude CLI client
│   │   ├── parser.py           # Stream parsing
│   │   └── formatter.py        # Response formatting
│   ├── handlers/               # Discord event handlers
│   │   ├── __init__.py
│   │   ├── ready.py            # Bot ready handler
│   │   ├── channels.py         # Channel management
│   │   └── messages.py         # Message handling
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── typing.py           # Typing utilities
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── helpers/                # Test helpers
│       └── data/               # Test data
├── docs/                       # Documentation
│   └── plans/                  # Implementation plans
├── .env.example                # Environment variables template
├── pyproject.toml              # Project configuration
├── uv.lock                     # Dependency lock file
├── .pre-commit-config.yaml     # Pre-commit hooks
└── README.md                   # Project documentation
```

## Development Workflow

### Feature Development
1. Create a feature branch from `main`
2. Implement changes with tests
3. Run full test suite: `uv run pytest`
4. Run linting: `uv run ruff check --fix && uv run ruff format`
5. Run pre-commit hooks: `uv run pre-commit run --all-files`
6. Test integration manually if needed
7. Create pull request with description

### Commit Guidelines
- Use descriptive commit messages
- Follow conventional commit format when possible
- Keep commits focused and atomic
- Run pre-commit hooks before committing

### Pull Request Process
- Ensure CI passes (tests, linting, formatting)
- Include tests for new functionality
- Update documentation if needed
- Get code review from maintainers

## Error Handling and Logging

### Logging
- Use `structlog` for structured logging
- Import logger: `logger = structlog.get_logger()`
- Use consistent log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- Include relevant context in log messages

```python
import structlog

logger = structlog.get_logger()

# Good logging examples
logger.info("discord_ai.message.received", channel=channel_name, session_id=session_id)
logger.error("discord_ai.message.error", error=str(e), channel=channel_name)
```

### Error Handling Patterns
- Use try/except blocks for expected errors
- Log exceptions with context
- Don't expose internal errors to users directly
- Use Discord spoiler tags (`|| ||`) for error messages in channels

```python
try:
    # risky operation
    await some_async_operation()
except Exception as e:
    logger.error("operation.failed", error=str(e), context=relevant_data)
    await channel.send(f"||Error: {str(e)}||")
```

## Type Safety

### Type Hints
- Use comprehensive type hints throughout the codebase
- Leverage Python 3.12 features (union syntax `X | Y`)
- Use `typing` module for complex types
- Define custom types when helpful

### Pydantic Models
- Use Pydantic `BaseModel` for data structures
- Define literal types for discriminated unions
- Use `Field` for validation and defaults
- Keep models simple and focused

```python
from typing import Any, Literal
from pydantic import BaseModel, Field

class MessageEvent(BaseModel):
    type: Literal["message"]
    content: str
    channel_id: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

## Dependencies and Imports

### Import Organization
- Use absolute imports within the package
- Follow Ruff's isort configuration
- Group imports: standard library, third-party, local
- Use `from __future__ import annotations` for forward references

```python
# Good import organization
import asyncio
from typing import Any, Literal

import discord
import structlog
from pydantic import BaseModel

from discord_ai.models import MessageEvent
from discord_ai.settings import Settings
```

### Dependency Management
- Use `uv` for dependency management
- Keep dependencies minimal and up-to-date
- Separate runtime and development dependencies
- Use exact versions in `uv.lock` for reproducibility

### Environment Variables
- Use Pydantic Settings for configuration
- Load from `.env` files
- Provide sensible defaults
- Document required environment variables

```python
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    discord_token: str = Field(default="", alias="DISCORD_BOT_TOKEN")
    category_name: str = "Claude Conversations"
    log_level: str = "INFO"
```

## Discord Bot Specific Guidelines

### Event Handling
- Use descriptive event handler functions
- Separate business logic from event handling
- Handle bot's own messages appropriately
- Validate channel context before processing

### Async Patterns
- Use `asyncio` for concurrent operations
- Handle cancellation properly in async contexts
- Use `asyncio.create_task()` for background operations
- Manage typing indicators and timeouts

### Claude Integration
- Maintain session isolation per Discord channel
- Handle streaming responses appropriately
- Format tool calls and results for Discord
- Respect rate limits and timeouts

## Performance Considerations

### Async Best Practices
- Avoid blocking operations in async functions
- Use appropriate timeouts for external calls
- Cancel background tasks properly
- Monitor for race conditions

### Memory Management
- Clean up resources in exception handlers
- Avoid accumulating state unnecessarily
- Use appropriate data structures for the use case

### Testing Performance
- Keep unit tests fast (< 100ms each)
- Mock external dependencies in unit tests
- Use fixtures for expensive setup
- Run integration tests separately from unit tests

## Security Guidelines

### API Keys and Secrets
- Never commit secrets to version control
- Use environment variables for sensitive data
- Validate and sanitize user input
- Log errors without exposing sensitive information

### Discord Permissions
- Request minimal required permissions
- Validate bot permissions before operations
- Handle permission errors gracefully
- Document required permissions in setup

---

This document should be updated as the codebase evolves. When making changes that affect these guidelines, update this document accordingly.