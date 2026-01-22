import asyncio
import sys
from os import getenv
from dotenv import load_dotenv

import aiogram.exceptions
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from utils import logger, bootstrap
from utils.decorators import check_user
from handlers.registration import RegistrationStates, process_name
from handlers.commands import send_welcome, send_full_info, send_change_lang, handle_lang_change

load_dotenv(dotenv_path=".env")
BOT_TOKEN = getenv("BOT_TOKEN")


dp = Dispatcher()

dp.message.register(process_name, RegistrationStates.waiting_for_name)


@dp.message(CommandStart())
@check_user
async def start_handler(message: Message):
    """Handle the /start command."""
    await send_welcome(message)


@dp.message(Command("full_info"))
@dp.callback_query(F.data == "full_info")
@check_user
async def full_info_handler(update: Message | CallbackQuery):
    """Handle the /full_info command or callback."""
    await send_full_info(update)


@dp.message(Command("changelang"))
@check_user
async def changelang_handler(message: Message):
    """Handle the /changelang command."""
    await send_change_lang(message)


@dp.callback_query(F.data.startswith("lang:"))
@check_user
async def lang_change_handler(callback: CallbackQuery):
    """Handle language change callback."""
    await handle_lang_change(callback)


async def start_bot() -> None:
    """Start the bot with connection test and polling."""
    logger.info("Starting bot...")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.get_me()  # Test bot connection
    except (aiogram.exceptions.TelegramConflictError, aiogram.exceptions.TelegramUnauthorizedError) as e:
        logger.critical(f"Can't start bot: {e}")
        if bot:
            await bot.session.close()
        sys.exit(1)
    else:
        logger.info("Bot successfully started.")
        logger.info("Bot information:")
        bot_info = await bot.get_me()
        logger.info(f"Username: @{bot_info.username}")
        logger.info(f"ID: {bot_info.id}")
        await dp.start_polling(bot)


async def main() -> None:
    """Main entry point: perform checks and start the bot."""
    bootstrap.bootstrap() # Perform initial setup with bootstrap.py
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        sys.exit(0)