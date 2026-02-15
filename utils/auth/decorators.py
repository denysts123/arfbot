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
    Extracts referral parameter from /start command if present.
    """

    @wraps(func)
    async def wrapper(update, state: FSMContext = None):
        user_id = update.from_user.id
        logger.debug(f"Checking user {user_id}")

        user_data = await get_user(user_id)
        if user_data is None:
            logger.info(f"User {user_id} not found, starting registration")
            
            referrer_id = None
            if hasattr(update, 'text') and update.text:
                args = update.text.split()[1] if len(update.text.split()) > 1 else None
                if args and args.isdigit():
                    potential_referrer = int(args)
                    if potential_referrer != user_id:
                        referrer_data = await get_user(potential_referrer)
                        if referrer_data and not await is_banned(potential_referrer):
                            referrer_id = potential_referrer
                            logger.info(f"User {user_id} has valid referrer {referrer_id}")
            
            await state.set_state(RegistrationStates.waiting_for_name)
            if referrer_id:
                await state.update_data(referrer_id=referrer_id)
            
            text = get_translation('en_US', 'messages.select_name')
            if isinstance(update, CallbackQuery):
                await update.answer()
                await update.message.answer(text)
            else:
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
