"""
Keyboard utilities module.
Provides functions for creating inline keyboards.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.i18n import tr, locales


async def create_games_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for games selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await tr(user_id, 'messages.penalty'), callback_data='penalty')],
        [InlineKeyboardButton(text=await tr(user_id, 'messages.matches'), callback_data='matches')]
    ])


async def create_play_button_markup(user_id: int, callback_data: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with a play button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await tr(user_id, 'messages.play_button'), callback_data=callback_data)]
    ])


def create_lang_selection_markup() -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{locales[lang]['config']['loc_flag']} {locales[lang]['config']['loc_name']}",
            callback_data=f"lang:{lang}"
        )]
        for lang in locales
    ])


async def create_games_and_events_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for games and events selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await tr(user_id, 'messages.games'), callback_data='games')],
        [InlineKeyboardButton(text=await tr(user_id, 'messages.events'), callback_data='events')]
    ])


async def create_main_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for main menu navigation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=await tr(user_id, 'messages.games'), callback_data='games')],
        [InlineKeyboardButton(text=await tr(user_id, 'messages.stats'), callback_data='full_info')],
        [InlineKeyboardButton(text=await tr(user_id, 'messages.referral'), callback_data='referral')],
        [InlineKeyboardButton(text=await tr(user_id, 'messages.changelang'), callback_data='changelang')]
    ])
