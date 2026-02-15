"""
Main entry point for the Telegram bot application.
Initializes the bot, sets up handlers, and starts polling.
"""
import asyncio
import sys
from os import getenv
from pathlib import Path

import aiogram.exceptions
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers.commands import setup_handlers
from core.bootstrap import bootstrap
from core.logger import logger

load_dotenv(dotenv_path=Path(__file__).parent / '.env')

dp = Dispatcher()


async def start_bot() -> None:
    """
    Start the bot by establishing connection, setting commands, and starting polling.
    Logs essential bot information on successful startup.
    """
    logger.info("Starting bot...")
    bot = Bot(token=getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    commands = [
        BotCommand(command="start", description="Start the bot and show main menu"),
        BotCommand(command="full_info", description="View detailed statistics"),
        BotCommand(command="changelang", description="Change language"),
        BotCommand(command="games", description="Access games section"),
        BotCommand(command="stats", description="View statistics"),
        BotCommand(command="referral", description="Referral system"),
    ]
    await bot.set_my_commands(commands)
    
    try:
        bot_info = await bot.get_me()
        logger.info("Bot successfully started")
        logger.info(f"Username: @{bot_info.username}")
        logger.info(f"ID: {bot_info.id}")
    except (aiogram.exceptions.TelegramConflictError, aiogram.exceptions.TelegramUnauthorizedError) as e:
        logger.critical(f"Can't start bot: {e}")
        await bot.session.close()
        sys.exit(1)
    
    setup_handlers(dp)
    await dp.start_polling(bot)



async def main() -> None:
    """
    Main entry point of the application.
    Runs bootstrap checks and starts the bot.
    """
    await bootstrap()
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)