import asyncio
import sys
from os import getenv
from dotenv import load_dotenv
from functools import wraps

import aiogram.exceptions
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from utils import logger, bootstrap
from utils.user_utils import (
    get_user, is_banned as is_banned_func, get_ban_date, get_full_stats, create_user
)

load_dotenv(dotenv_path=".env")
BOT_TOKEN = getenv("BOT_TOKEN")


dp = Dispatcher()


def check_user(func):
    """Check if a user exists and is not banned. Working as decorator."""

    @wraps(func)
    async def wrapper(update):
        user_id = update.from_user.id
        logger.debug(f"Checking user {user_id} in decorator.")
        user_data = await get_user(user_id)
        if user_data is None:
            logger.info(f"User {user_id} not found, creating new user.")
            await create_user(user_id, update)
            return await func(update)
        if await is_banned_func(user_id):
            logger.warning(f"User {user_id} is banned, blocking access.")
            if isinstance(update, CallbackQuery):
                await update.answer("Вы забанены и не можете использовать этого бота.\n"
                                    f"Дата окончания бана: {await get_ban_date(user_id)}\n", show_alert=True)
            else:
                await update.answer("Вы забанены и не можете использовать этого бота.\n"
                                    f"Дата окончания бана: {await get_ban_date(user_id)}\n")
            return None
        logger.debug(f"User {user_id} passed checks, proceeding to handler.")
        return await func(update)

    return wrapper


@dp.message(CommandStart())
@check_user
async def send_welcome(message: Message):
    """Handle the /start command. Send a welcome message to the user."""
    user_id = message.from_user.id
    logger.debug(f"Handling /start command for user {user_id}.")
    user_data = await get_user(user_id)
    logger.debug(f"Sending welcome message to user {user_id}.")
    await message.answer(f"ID: {user_data[0]}\n"
                         f"Имя: {user_data[1]}\n"
                         f"Монеты: {user_data[8]}\n"
                         f"Билеты: {user_data[9]}\n"
                         f"Кубки: {user_data[10]}\n"
                         f"О игроке: \n{user_data[2]}")


@dp.message(Command("full_info"))
@dp.callback_query(F.data == "full_info")
@check_user
async def send_full_info(update: Message | CallbackQuery):
    """Handle the /full_info command or callback. Send full user information."""
    user_id = update.from_user.id
    logger.debug(f"Handling full_info for user {user_id}.")
    stats = await get_full_stats(user_id)
    if stats is None:
        text = "Пользователь не найден."
    else:
        user_data = stats["user_data"]
        logger.debug(f"Sending full info message to user {user_id}.")
        text = (f"Статистика игрока \"{user_data[1]}\"\n"
                f"Монеты: {user_data[8]}\n"
                f"Билеты: {user_data[9]}\n"
                f"Кубки: {user_data[10]}\n"
                f"\n"
                f"Всего получено монет: {user_data[17]}\n"
                f"Всего получено билетов: {user_data[18]}\n"
                f"Всего сыграно матчей: {user_data[13]}\n"
                f"Из них вы:\n"
                f"{user_data[11]} раз выиграли ({stats['win_rate']:.2f}%)\n"
                f"{user_data[12]} раз проиграли\n"
                f"{user_data[13] - (user_data[11] + user_data[12])} раз вышли в ничью\n"
                f"Открыто паков:\n"
                f"{user_data[22]} маленьких\n"
                f"{user_data[23]} средних\n"
                f"{user_data[24]} больших\n"
                f"Приглашено людей по реферальной ссылке: {user_data[16]}\n"
                f"Дата регистрации: {user_data[29]}\n"
                f"\nТакже учтите что некоторое количество этих ресурсов не будет учитыватся если они выданы вам от "
                f"администраторами (т.е. призрачные):\n"
                f"Призрачные маленькие паки: {user_data[19]}\n"
                f"Призрачные средние паки: {user_data[20]}\n"
                f"Призрачные большие паки: {user_data[21]}\n"
                f"Неучтенная успешность: {stats['ghost_success']}\n"
                f"\n\n"
                f"Ваша итоговая успешность: {stats['success']}\n"
                f"Вы находитесь на {stats['position']} месте в топе бота\n"
                f"Ваш ранг: {None}\n"  # TODO: Add value
                f"Уровень ФП: {None}Н/Д (скоро)"  # TODO: Add value
                )
    
    if isinstance(update, CallbackQuery):
        await update.answer()
        await update.message.answer(text)
    else:
        await update.answer(text)


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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
        sys.exit(0)