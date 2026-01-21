import asyncio
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

import colorama

colorama.init(autoreset=True)

import database
db = database.Database()

BOT_TOKEN = getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print(colorama.Fore.RED + "Error: BOT_TOKEN environment variable is not set.")
    sys.exit(1)

dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: Message):
    """Handle the /start command.
    Send a welcome message to the user."""
    #database.get_user(message.from_user.id)
    await message.answer("ID: {UserId}\n"
                         "Имя: {Username}\n"
                         "Монеты: {Coins}\n"
                         "Билеты: {Tickets}\n"
                         "Кубки: {Cups}\n"
                         "О игроке: \n{UserInfo}")
    
