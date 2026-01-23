import asyncio
import sys
from os import getenv
from dotenv import load_dotenv
from pathlib import Path

import aiogram.exceptions
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.commands import setup_handlers
from utils.bootstrap_dir import bootstrap
from utils.logging import logger

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

dp = Dispatcher()
setup_handlers(dp)


async def start_bot() -> None:
    """Starts the bot by establishing a connection, verifying bot credentials, logging essential information, and initiating the polling loop for handling updates."""
    logger.info("Starting bot...")
    bot = Bot(token=getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        bot_info = await bot.get_me()
    except (aiogram.exceptions.TelegramConflictError, aiogram.exceptions.TelegramUnauthorizedError) as e:
        logger.critical(f"Can't start bot: {e}")
        await bot.session.close()
        sys.exit(1)
    else:
        logger.info("Bot successfully started.")
        logger.info("Bot information:")
        logger.info(f"Username: @{bot_info.username}")
        logger.info(f"ID: {bot_info.id}")
        await dp.start_polling(bot)


async def main() -> None:
    """Serves as the main entry point of the application, executing bootstrap procedures for initial setup and subsequently starting the bot."""
    await bootstrap()
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        sys.exit(0)