from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.i18n import tr, locales


async def create_games_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for games selection with translated buttons."""
    penalty_text = await tr(user_id, 'messages.penalty')
    matches_text = await tr(user_id, 'messages.matches')
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=penalty_text, callback_data='penalty')],
        [InlineKeyboardButton(text=matches_text, callback_data='matches')]
    ])


async def create_play_button_markup(user_id: int, callback_data: str) -> InlineKeyboardMarkup:
    """Create inline keyboard with play button using translated text."""
    play_text = await tr(user_id, 'messages.play_button')
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=play_text, callback_data=callback_data)]
    ])


def create_lang_selection_markup() -> InlineKeyboardMarkup:
    """Create inline keyboard for language selection using available locales."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{locales[lang]['config']['loc_flag']} {locales[lang]['config']['loc_name']}", callback_data=f"lang:{lang}")]
        for lang in locales
    ])
    return keyboard


async def create_games_and_events_markup(user_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard for games and events selection with translated buttons."""
    games_text = await tr(user_id, 'messages.games')
    events_text = await tr(user_id, 'messages.events')
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=games_text, callback_data='games')],
        [InlineKeyboardButton(text=events_text, callback_data='events')]
    ])
