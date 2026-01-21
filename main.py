import asyncio
import sys
from os import getenv

import aiogram.exceptions
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import colorama

from utils import logger
from models import User

colorama.init(autoreset=True)


load_dotenv(dotenv_path=".env")
BOT_TOKEN = getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print(colorama.Fore.RED + "Error: BOT_TOKEN environment variable is not set.")
    sys.exit(1)

dp = Dispatcher()

@dp.message(CommandStart())
async def send_welcome(message: Message):
    """Handle the /start command.
    Send a welcome message to the user."""
    user_data = await User(user_id=message.from_user.id).get_user()
    await message.answer(f"ID: {user_data[0]}\n"
                         f"Имя: {user_data[1]}\n"
                         f"Монеты: {user_data[8]}\n"
                         f"Билеты: {user_data[9]}\n"
                         f"Кубки: {user_data[10]}\n"
                         f"О игроке: \n{user_data[2]}")



async def start_bot() -> None:
    logger.info("Starting bot...")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.get_me() # Test bot connection
    except (aiogram.exceptions.TelegramConflictError, aiogram.exceptions.TelegramUnauthorizedError) as e: # Catch connection errors
        logger.critical(f"Can't start bot: {e}")
        if bot:
            await bot.session.close()
        input("\033[96mPress enter to exit...\033[0m")
        exit(1)
    else:
        logger.info("Bot successfully started.")
        logger.info("Bot information:")
        bot_info = await bot.get_me()
        logger.info(f"Username: @{bot_info.username}")
        logger.info(f"ID: {bot_info.id}")
        await dp.start_polling(bot)

async def main() -> None:
    


if __name__ == "__main__":
    asyncio.run(main())