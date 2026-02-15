"""
Registration handlers module.
Provides FSM states and handlers for user registration flow.
"""
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from utils.formatters import format_welcome_message
from utils.i18n import get_translation
from utils.logging import logger
from utils.user import create_user, get_user
from utils.keyboards import create_main_menu_markup


class RegistrationStates(StatesGroup):
    """States for user registration process."""
    waiting_for_name = State()


def get_lang_from_code(lang_code: str) -> str:
    """
    Determine language code from Telegram language code.
    Defaults to en_US for unsupported languages.
    """
    lang_map = {'en': 'en_US', 'uk': 'uk_UA', 'ru': 'ru_RU', 'cs': 'cs_CZ'}
    return lang_map.get(lang_code, 'en_US')


async def process_name(message: Message, state: FSMContext):
    """
    Handle username input during registration.
    Validates name, creates user, and sends welcome message.
    """
    user_id = message.from_user.id
    name = message.text.strip()
    
    if not name:
        text = get_translation('en_US', 'messages.name_empty')
        await message.answer(text)
        return
    
    logger.info(f"User {user_id} registering with name '{name}'")
    
    lang = get_lang_from_code(message.from_user.language_code)
    await create_user(user_id, name, lang)
    await state.clear()
    
    user_data = await get_user(user_id)
    text = await format_welcome_message(user_id, user_data)
    markup = await create_main_menu_markup(user_id)
    await message.answer(text, reply_markup=markup)
