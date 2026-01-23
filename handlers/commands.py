from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from utils.logging import logger
from utils.user import get_user, get_full_stats, change_user_lang
from utils.i18n import tr, locales
from utils.formatters import format_welcome_message, format_full_info_message
from utils.auth import check_user
from handlers.registration import RegistrationStates, process_name


async def send_welcome(message: Message):
    """Handle the /start command. Send a welcome message to the user."""
    user_id = message.from_user.id
    logger.debug(f"Handling /start command for user {user_id}.")
    user_data = await get_user(user_id)
    logger.debug(f"Sending welcome message to user {user_id}.")
    text = await format_welcome_message(user_id, user_data)
    await message.answer(text)


async def send_full_info(update: Message | CallbackQuery):
    """Handle the /full_info command or callback. Send full user information."""
    user_id = update.from_user.id
    logger.debug(f"Handling full_info for user {user_id}.")
    stats = await get_full_stats(user_id)
    if stats is None:
        text = await tr(user_id, 'messages.user_not_found')
    else:
        logger.debug(f"Sending full info message to user {user_id}.")
        text = await format_full_info_message(user_id, stats)
    
    if isinstance(update, CallbackQuery):
        await update.answer()
        await update.message.answer(text)
    else:
        await update.answer(text)


async def send_change_lang(message: Message):
    """Handle the /changelang command. Show language selection menu."""
    user_id = message.from_user.id
    logger.debug(f"Handling /changelang command for user {user_id}.")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{locales[lang]['config']['loc_flag']} {locales[lang]['config']['loc_name']}", callback_data=f"lang:{lang}")]
        for lang in locales
    ])
    text = await tr(user_id, 'messages.select_lang')
    await message.answer(text, reply_markup=keyboard)


async def handle_lang_change(callback: CallbackQuery):
    """Handles the callback query for language selection, updates the user's language in the database and cache, and confirms the change to the user."""
    user_id = callback.from_user.id
    lang = callback.data.split(":")[1]
    logger.debug(f"Handling language change for user {user_id} to {lang}.")
    await change_user_lang(user_id, lang)
    confirm_text = await tr(user_id, 'messages.lang_changed')
    await callback.answer(confirm_text, show_alert=True)
    await callback.message.edit_text(confirm_text)


def setup_handlers(dp: Dispatcher):
    """Registers all handlers with the dispatcher."""
    dp.message.register(process_name, RegistrationStates.waiting_for_name)

    @dp.message(CommandStart())
    @check_user
    async def start_handler(message: Message, state: FSMContext = None):
        """Handles the /start command by sending a welcome message to the user."""
        await send_welcome(message)

    @dp.message(Command("full_info"))
    @dp.callback_query(F.data == "full_info")
    @check_user
    async def full_info_handler(update: Message | CallbackQuery, state: FSMContext = None):
        """Handles the /full_info command or full_info callback query by sending detailed user information."""
        await send_full_info(update)

    @dp.message(Command("changelang"))
    @check_user
    async def changelang_handler(message: Message, state: FSMContext = None):
        """Handles the /changelang command by initiating the language change process."""
        await send_change_lang(message)

    @dp.callback_query(F.data.startswith("lang:"))
    @check_user
    async def lang_change_handler(callback: CallbackQuery, state: FSMContext = None):
        """Handles callback queries for language selection, updating the user's language preference."""
        await handle_lang_change(callback)
