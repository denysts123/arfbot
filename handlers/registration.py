from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from utils.formatters import format_welcome_message
from utils.i18n import get_translation
from utils.logging import logger
from utils.user import create_user, get_user


class RegistrationStates(StatesGroup):
    """States for user registration process."""
    waiting_for_name = State()


def get_lang_from_code(lang_code: str) -> str:
    """Determine language code from Telegram language code, defaulting to en_US."""
    if lang_code == 'en':
        return 'en_US'
    elif lang_code == 'uk':
        return 'uk_UA'
    elif lang_code == 'ru':
        return 'ru_RU'
    elif lang_code == 'cs':
        return 'cs_CZ'
    else:
        return 'en_US'


async def process_name(message: Message, state: FSMContext):
    """Handle username input during registration, validate it, create the user, and send welcome message."""
    user_id = message.from_user.id
    name = message.text.strip()
    if not name:
        lang_code = message.from_user.language_code
        lang = get_lang_from_code(lang_code)
        text = get_translation(lang, 'messages.name_empty')
        await message.answer(text)
        return
    logger.debug(f"Received name '{name}' for user {user_id}.")
    
    lang_code = message.from_user.language_code
    lang = get_lang_from_code(lang_code)
    
    await create_user(user_id, name, lang)
    await state.clear()
    
    user_data = await get_user(user_id)
    text = await format_welcome_message(user_id, user_data)
    await message.answer(text)
