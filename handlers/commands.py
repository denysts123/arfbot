from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils import logger
from utils.user_utils import get_user, get_full_stats, change_user_lang
from utils.localization import tr, locales
from utils.text_formatters import format_welcome_message, format_full_info_message


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
    """Handle language change callback."""
    user_id = callback.from_user.id
    lang = callback.data.split(":")[1]
    logger.debug(f"Handling language change for user {user_id} to {lang}.")
    await change_user_lang(user_id, lang)
    # Get confirmation message in new language
    confirm_text = await tr(user_id, 'messages.lang_changed')
    await callback.answer(confirm_text, show_alert=True)
    # Optionally, edit the message or send a new one
    await callback.message.edit_text(confirm_text)
