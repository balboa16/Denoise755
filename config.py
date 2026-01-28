"""Configuration module for loading environment variables."""
from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration class for the Telegram bot."""

    bot_token: str

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config: Config instance with loaded values.

        Raises:
            ValueError: If BOT_TOKEN is not set in environment variables.
        """
        load_dotenv()

        bot_token = getenv("BOT_TOKEN")

        if not bot_token:
            raise ValueError("BOT_TOKEN environment variable is not set")

        return cls(bot_token=bot_token)
