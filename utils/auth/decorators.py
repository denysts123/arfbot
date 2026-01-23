from functools import wraps
from typing import Callable

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from utils.logging import logger
from utils.user import get_user, is_banned as is_banned_func, get_ban_date
from utils.i18n import tr, get_translation
from handlers.registration import RegistrationStates, get_lang_from_code


def check_user(func: Callable) -> Callable:
    """Decorator to check if a user exists and is not banned before executing the handler."""

    @wraps(func)
    async def wrapper(update, state: FSMContext = None):
        user_id = update.from_user.id
        logger.debug(f"Checking user {user_id} in decorator.")
        user_data = await get_user(user_id)
        if user_data is None:
            logger.info(f"User {user_id} not found, starting registration.")
            await state.set_state(RegistrationStates.waiting_for_name)
            lang_code = update.from_user.language_code
            lang = get_lang_from_code(lang_code)
            text = get_translation(lang, 'messages.select_name')
            await update.answer(text)
            return None
        if await is_banned_func(user_id):
            logger.warning(f"User {user_id} is banned, blocking access.")
            ban_date = await get_ban_date(user_id)
            banned_msg = await tr(user_id, 'messages.banned')
            banned_msg = banned_msg.format(ban_date=ban_date)
            if isinstance(update, CallbackQuery):
                await update.answer(banned_msg, show_alert=True)
            else:
                await update.answer(banned_msg)
            return None
        logger.debug(f"User {user_id} passed checks, proceeding to handler.")
        return await func(update, state)

    return wrapper
