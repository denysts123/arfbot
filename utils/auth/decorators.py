"""
Authentication decorators module.
Provides decorators for user validation before handler execution.
"""

from functools import wraps
from typing import Callable

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.logging import logger
from utils.user import get_user, is_banned, get_ban_date
from utils.i18n import tr, get_translation
from handlers.registration import RegistrationStates


def check_user(func: Callable) -> Callable:
    """
    Decorator to verify user exists and is not banned before executing handler.
    Starts registration flow if user not found.
    """

    @wraps(func)
    async def wrapper(update, state: FSMContext = None):
        user_id = update.from_user.id
        logger.debug(f"Checking user {user_id}")

        user_data = await get_user(user_id)
        if user_data is None:
            logger.info(f"User {user_id} not found, starting registration")
            await state.set_state(RegistrationStates.waiting_for_name)
            text = get_translation('en_US', 'messages.select_name')
            await update.answer(text)
            return None

        if await is_banned(user_id):
            logger.warning(f"User {user_id} is banned")
            ban_date = await get_ban_date(user_id)
            banned_msg = await tr(user_id, 'messages.banned')
            banned_msg = banned_msg.format(ban_date=ban_date)
            if isinstance(update, CallbackQuery):
                await update.answer(banned_msg, show_alert=True)
            else:
                await update.answer(banned_msg)
            return None

        return await func(update, state)

    return wrapper
