"""Main module for the Telegram bot."""
import asyncio
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    """Main async function to initialize and start the bot."""
    try:
        logging.info("Bot starting...")

        # Initialize bot and dispatcher
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher()

        # Include handlers router in dispatcher
        dp.include_router(router)

        # Start polling
        await dp.start_polling(bot)

    except Exception as e:
        logging.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
