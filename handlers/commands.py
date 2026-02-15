"""
Command handlers module.
Registers all bot commands and callback handlers.
"""
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.types import Message, CallbackQuery

from db.database import Database
from utils.logging import logger
from utils.user import get_user, get_full_stats, change_user_lang, is_banned
from utils.i18n import tr
from utils.formatters import format_welcome_message, format_full_info_message
from utils.auth import check_user
from utils.keyboards import (
    create_games_markup, create_play_button_markup,
    create_lang_selection_markup, create_games_and_events_markup,
    create_main_menu_markup, create_referral_markup
)
from handlers.registration import RegistrationStates, process_name
from game.penalty import play_penalty, check_penalty_access
from game.matches import play_match
from utils.user_fields import REFERRALS_COUNT

db = Database()


def checked_handler(dp, *filters):
    """
    Decorator to combine @check_user and register handlers for given filters.
    Automatically determines if handler should be message or callback based.
    """
    def decorator(func):
        func = check_user(func)
        for f in filters:
            if isinstance(f, Command) or 'Command' in str(type(f)):
                dp.message.register(func, f)
            elif hasattr(f, 'data') or 'F.' in str(f) or isinstance(f, type(F.data == "test")):
                dp.callback_query.register(func, f)
            else:
                dp.message.register(func, f)
        return func
    return decorator


async def send_welcome(message: Message):
    """
    Handle the /start command.
    Shows welcome message to existing users.
    """
    user_id = message.from_user.id
    logger.info(f"User {user_id} used /start command")
    user_data = await get_user(user_id)
    text = await format_welcome_message(user_id, user_data)
    await message.answer(text, reply_markup=await create_main_menu_markup(user_id))


async def send_full_info(update: Message | CallbackQuery):
    """
    Handle full_info command or callback by sending detailed user statistics.
    """
    user_id = update.from_user.id
    logger.info(f"User {user_id} viewed full stats")
    
    stats = await get_full_stats(user_id)
    if stats is None:
        text = await tr(user_id, 'messages.user_not_found')
    else:
        text = await format_full_info_message(user_id, stats)
    
    if isinstance(update, CallbackQuery):
        await update.answer()
        await update.message.answer(text)
    else:
        await update.answer(text)


async def send_change_lang(message: Message):
    """
    Handle language change by showing language selection keyboard.
    """
    user_id = message.from_user.id
    logger.info(f"User {user_id} opened language selection")
    keyboard = create_lang_selection_markup()
    text = await tr(user_id, 'messages.select_lang')
    await message.answer(text, reply_markup=keyboard)


async def handle_lang_change(callback: CallbackQuery):
    """
    Handle language change callback.
    """
    user_id = callback.from_user.id
    lang = callback.data.split(":")[1]
    logger.info(f"User {user_id} changed language to {lang}")
    await change_user_lang(user_id, lang)
    confirm_text = await tr(user_id, 'messages.lang_changed')
    await callback.answer(confirm_text, show_alert=True)
    await callback.message.edit_text(confirm_text)


async def send_games_menu(update: Message | CallbackQuery):
    """
    Send games menu with available game options.
    """
    user_id = update.from_user.id
    logger.info(f"User {user_id} opened games menu")
    markup = await create_games_markup(user_id)
    title = await tr(user_id, 'messages.games')
    if isinstance(update, CallbackQuery):
        await update.answer(title)
        await update.message.answer(title, reply_markup=markup)
    else:
        await update.answer(title, reply_markup=markup)


async def send_games_and_events_menu(callback: CallbackQuery):
    """
    Send games and events selection menu.
    """
    user_id = callback.from_user.id
    logger.info(f"User {user_id} opened games and events menu")
    markup = await create_games_and_events_markup(user_id)
    title = await tr(user_id, 'messages.games_and_events')
    await callback.answer(title)
    await callback.message.answer(title, reply_markup=markup)


async def send_penalty_menu(callback: CallbackQuery):
    """
    Send penalty menu with access check.
    """
    user_id = callback.from_user.id
    if not await check_penalty_access(user_id):
        msg = await tr(user_id, 'messages.penalty_start')
        await callback.answer(msg, show_alert=True)
        return
    logger.info(f"User {user_id} opened penalty menu")
    msg = await tr(user_id, 'messages.penalty')
    await callback.answer(msg)
    markup = await create_play_button_markup(user_id, "play_penalty")
    await callback.message.answer(msg, reply_markup=markup)


async def send_matches_menu(callback: CallbackQuery):
    """
    Send matches menu with requirements and play button.
    """
    user_id = callback.from_user.id
    logger.info(f"User {user_id} opened matches menu")
    markup = await create_play_button_markup(user_id, "play_match")
    await callback.answer(await tr(user_id, 'messages.matches'))
    req_msg = await tr(user_id, 'messages.match_requirements')
    await callback.message.answer(req_msg, reply_markup=markup)


async def play_game(callback: CallbackQuery, game_func):
    """
    Execute a game function and send start and result messages.
    """
    await callback.answer()
    user_id = callback.from_user.id
    game_data = await game_func(user_id)
    if "error" in game_data:
        await callback.message.answer(game_data["error"])
        return
    await callback.message.answer(game_data["start_msg"])
    await callback.message.answer(game_data["result"])


async def send_referral_info(update: Message | CallbackQuery):
    """
    Send referral info with link, statistics and convenient sharing buttons.
    """
    user_id = update.from_user.id
    logger.info(f"User {user_id} viewed referral info")
    user_data = await get_user(user_id)
    referrals_count = user_data[REFERRALS_COUNT]
    
    bot = update.bot
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    text = await tr(user_id, 'messages.referral_info')
    text = text.format(link=referral_link, count=referrals_count)
    markup = await create_referral_markup(user_id, referral_link)
    
    if isinstance(update, CallbackQuery):
        await update.answer()
        await update.message.answer(text, reply_markup=markup)
    else:
        await update.answer(text, reply_markup=markup)


def setup_handlers(dp):
    """
    Register all message and callback handlers with the dispatcher.
    """
    dp.message.register(process_name, RegistrationStates.waiting_for_name)

    @checked_handler(dp, CommandStart())
    async def start_handler(message: Message, state=None):
        await send_welcome(message)

    @checked_handler(dp, Command("full_info"), F.data == "full_info")
    async def full_info_handler(update: Message | CallbackQuery, state=None):
        await send_full_info(update)

    @checked_handler(dp, Command("changelang"))
    async def changelang_handler(message: Message, state=None):
        await send_change_lang(message)

    @checked_handler(dp, Command("games"))
    async def games_cmd_handler(message: Message, state=None):
        await send_games_menu(message)

    @checked_handler(dp, Command("stats"))
    async def stats_cmd_handler(message: Message, state=None):
        await send_full_info(message)

    @checked_handler(dp, Command("referral"))
    async def referral_cmd_handler(message: Message, state=None):
        await send_referral_info(message)

    @checked_handler(dp, F.data.startswith("lang:"))
    async def lang_change_handler(callback: CallbackQuery, state=None):
        await handle_lang_change(callback)

    @checked_handler(dp, F.data == "games_and_events")
    async def games_and_events_handler(callback: CallbackQuery, state=None):
        await send_games_and_events_menu(callback)

    @checked_handler(dp, F.data == "games")
    async def games_handler(callback: CallbackQuery, state=None):
        await send_games_menu(callback)

    @checked_handler(dp, F.data == "penalty")
    async def penalty_handler(callback: CallbackQuery, state=None):
        await send_penalty_menu(callback)

    @checked_handler(dp, F.data == "play_penalty")
    async def play_penalty_handler(callback: CallbackQuery, state=None):
        await play_game(callback, play_penalty)

    @checked_handler(dp, F.data == "matches")
    async def matches_handler(callback: CallbackQuery, state=None):
        await send_matches_menu(callback)

    @checked_handler(dp, F.data == "play_match")
    async def play_match_handler(callback: CallbackQuery, state=None):
        await play_game(callback, play_match)

    @checked_handler(dp, F.data == "referral")
    async def referral_callback_handler(callback: CallbackQuery, state=None):
        await send_referral_info(callback)

    @checked_handler(dp, F.data == "changelang")
    async def changelang_callback_handler(callback: CallbackQuery, state=None):
        await callback.answer()
        if callback.message:
            await send_change_lang(callback.message)
