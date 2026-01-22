import asyncio
import sys
from os import getenv
from dotenv import load_dotenv
from functools import wraps

import aiogram.exceptions
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from utils import logger, bootstrap
from models import User

load_dotenv(dotenv_path=".env")
BOT_TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


def is_banned(func):
    """Check if a user is banned. Working as decorator."""

    @wraps(func)
    async def wrapper(message: Message):
        user = User(user_id=message.from_user.id)
        if await user.is_banned():
            await message.answer("Вы забанены и не можете использовать этого бота.\n"
                                 f"Дата окончания бана: {await user.get_ban_date()}\n")
            return None
        return await func(message)


@dp.message(CommandStart())
@is_banned
async def send_welcome(message: Message):
    """Handle the /start command. Send a welcome message to the user."""
    user_data = await User(user_id=message.from_user.id).get_user()
    await message.answer(f"ID: {user_data[0]}\n"
                         f"Имя: {user_data[1]}\n"
                         f"Монеты: {user_data[8]}\n"
                         f"Билеты: {user_data[9]}\n"
                         f"Кубки: {user_data[10]}\n"
                         f"О игроке: \n{user_data[2]}")


@dp.message(Command("full_info"))
@is_banned
async def send_full_info(message: Message):
    """Handle the /full_info command. Send full user information."""
    user = User(user_id=message.from_user.id)
    user_data = await user.get_user()
    await message.answer(f"Статистика игрока \"{user_data[1]}\"\n"
                         f"Монеты: {user_data[8]}\n"
                         f"Билеты: {user_data[9]}\n"
                         f"Кубки: {user_data[10]}\n"
                         f"\n"
                         f"Всего получено монет: {user_data[17]}\n"
                         f"Всего получено билетов: {user_data[18]}\n"
                         f"Всего сыграно матчей: {user_data[13]}\n"
                         f"Из них вы:\n"
                         f"{user_data[11]} раз выиграли ({await user.get_win_rate_percent():.2f}%)\n"
                         f"{user_data[12]} раз проиграли\n"
                         f"{user_data[13] - (user_data[11] + user_data[12])} раз вышли в ничью\n"
                         f"Открыто паков:\n"
                         f"{user_data[22]} маленьких\n"
                         f"{user_data[23]} средних\n"
                         f"{user_data[24]} больших\n"
                         f"Приглашено людей по реферальной ссылке: {user_data[16]}\n"
                         f"Дата регистрации: {user_data[29]}\n"
                         f"\nТакже учтите что некоторое количество этих ресурсов не будет учитыватся если они выданы вам от "
                         f"администраторов (т.е. призрачные):\n"
                         f"Призрачные маленькие паки: {user_data[19]}\n"
                         f"Призрачные средние паки: {user_data[20]}\n"
                         f"Призрачные большие паки: {user_data[21]}\n"
                         f"Неучтенная успешность: {await user.calculate_ghost_success()}\n"
                         f"\n\n"
                         f"Ваша итоговая успешность: {await user.calculate_success()}\n"
                         f"Вы находитесь на {await user.get_user_position()} месте в топе бота\n"
                         f"Ваш ранг: {None}\n"  # TODO: Add value
                         f"Уровень ФП: {None}Н/Д (скоро)"  # TODO: Add value
                         )


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
    bootstrap.bootstrap()
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
