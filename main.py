"""Minimal version of the Telegram bot for testing deployment."""
import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


async def cmd_start(message: Message, bot: Bot):
    """Handle /start command."""
    await message.answer(
        "🎬 Video Noise Reduction Bot\n\n"
        "Bot is running!\n\n"
        "Note: Video processing features are temporarily unavailable."
    )


async def cmd_help(message: Message, bot: Bot):
    """Handle /help command."""
    await message.answer(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


async def cmd_echo(message: Message, bot: Bot):
    """Echo message for testing."""
    await message.answer(f"You said: {message.text}")


async def main() -> None:
    """Main async function to initialize and start the bot."""
    # Check if BOT_TOKEN is set
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        logger.error("Please set BOT_TOKEN in your Render environment variables.")
        sys.exit(1)

    logger.info("Bot starting...")
    logger.info(f"Bot token is configured: {'*' * 20}{BOT_TOKEN[-10:]}")

    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(cmd_start, Command(commands=["start"]))
    dp.message.register(cmd_help, Command(commands=["help"]))
    dp.message.register(cmd_echo)

    # Start polling
    logger.info("Starting polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)
