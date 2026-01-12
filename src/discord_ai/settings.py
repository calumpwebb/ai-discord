from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
    )

    discord_token: str = Field(default="", alias="DISCORD_BOT_TOKEN")
    category_name: str = "Claude Conversations"
    claude_cli_path: str = "claude"
    typing_interval_seconds: int = 5
    claude_timeout_seconds: int = 600
    log_level: str = "INFO"
