from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.types import Message, CallbackQuery

from utils.logging import logger
from utils.user import get_user, get_full_stats, change_user_lang
from utils.i18n import tr
from utils.formatters import format_welcome_message, format_full_info_message
from utils.auth import check_user
from utils.keyboards import (create_games_markup, create_play_button_markup,
                             create_lang_selection_markup, create_games_and_events_markup)
from handlers.registration import RegistrationStates, process_name
from game.penalty import play_penalty, check_penalty_access
from game.matches import play_match


async def send_welcome(message: Message):
    """Handle the /start command by retrieving user data, formatting a welcome message with user info
    and commands list, and sending it."""
    user_id = message.from_user.id
    logger.debug(f"Handling /start command for user {user_id}.")
    user_data = await get_user(user_id)
    logger.debug(f"Sending welcome message to user {user_id}.")
    text = await format_welcome_message(user_id, user_data)
    commands_text = await tr(user_id, 'messages.commands_list')
    await message.answer(text + "\n\n" + commands_text)


async def send_full_info(update: Message | CallbackQuery):
    """Handle the /full_info command or callback by retrieving user stats, formatting full info message,
    and sending it, distinguishing between Message and CallbackQuery."""
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
    """Handle the /changelang command by creating language selection keyboard and sending it with
    select_lang message."""
    user_id = message.from_user.id
    logger.debug(f"Handling /changelang command for user {user_id}.")
    keyboard = create_lang_selection_markup()
    text = await tr(user_id, 'messages.select_lang')
    await message.answer(text, reply_markup=keyboard)


async def handle_lang_change(callback: CallbackQuery):
    """Handle language change callback by extracting new language, updating user language, and sending
    confirmation."""
    user_id = callback.from_user.id
    lang = callback.data.split(":")[1]
    logger.debug(f"Handling language change for user {user_id} to {lang}.")
    await change_user_lang(user_id, lang)
    confirm_text = await tr(user_id, 'messages.lang_changed')
    await callback.answer(confirm_text, show_alert=True)
    await callback.message.edit_text(confirm_text)


def setup_handlers(dp):
    """Register all handlers with the dispatcher, including message and callback query handlers for
    commands and interactions."""
    dp.message.register(process_name, RegistrationStates.waiting_for_name)

    @dp.message(CommandStart())
    @check_user
    async def start_handler(message: Message, state = None):
        """Handle the /start command by sending a welcome message to the user."""
        await send_welcome(message)

    @dp.message(Command("full_info"))
    @dp.callback_query(F.data == "full_info")
    @check_user
    async def full_info_handler(update: Message | CallbackQuery, state = None):
        """Handle the /full_info command or full_info callback query by sending detailed user
        information."""
        await send_full_info(update)

    @dp.message(Command("changelang"))
    @check_user
    async def changelang_handler(message: Message, state = None):
        """Handle the /changelang command by initiating the language change process."""
        await send_change_lang(message)

    @dp.message(Command("games"))
    @check_user
    async def games_cmd_handler(message: Message, state = None):
        """Handle /games command by creating games markup and sending games title."""
        user_id = message.from_user.id
        markup = await create_games_markup(user_id)
        title = await tr(user_id, 'messages.games')
        await message.answer(title, reply_markup=markup)

    @dp.message(Command("stats"))
    @check_user
    async def stats_cmd_handler(message: Message, state = None):
        """Handle /stats command by sending full user info."""
        await send_full_info(message)

    @dp.callback_query(F.data.startswith("lang:"))
    @check_user
    async def lang_change_handler(callback: CallbackQuery, state = None):
        """Handle callback queries for language selection, updating the user's language preference."""
        await handle_lang_change(callback)

    @dp.callback_query(F.data == "games_and_events")
    @check_user
    async def games_and_events_handler(callback: CallbackQuery, state = None):
        """Handle games_and_events callback by creating markup and sending title."""
        user_id = callback.from_user.id
        markup = await create_games_and_events_markup(user_id)
        title = await tr(user_id, 'messages.games_and_events')
        await callback.answer(title)
        await callback.message.answer(title, reply_markup=markup)

    @dp.callback_query(F.data == "games")
    @check_user
    async def games_handler(callback: CallbackQuery, state = None):
        """Handle games callback by creating games markup and sending title."""
        user_id = callback.from_user.id
        markup = await create_games_markup(user_id)
        title = await tr(user_id, 'messages.games')
        await callback.answer(title)
        await callback.message.answer(title, reply_markup=markup)

    @dp.callback_query(F.data == "penalty")
    @check_user
    async def penalty_handler(callback: CallbackQuery, state = None):
        """Handle penalty callback by checking access, sending penalty message and play button."""
        user_id = callback.from_user.id
        if not await check_penalty_access(user_id):
            msg = await tr(user_id, 'messages.penalty_start')
            await callback.answer(msg, show_alert=True)
            return
        msg = await tr(user_id, 'messages.penalty')
        await callback.answer(msg)
        markup = await create_play_button_markup(user_id, "play_penalty")
        await callback.message.answer(msg, reply_markup=markup)

    @dp.callback_query(F.data == "play_penalty")
    @check_user
    async def play_penalty_handler(callback: CallbackQuery, state = None):
        """Handle play_penalty callback by simulating penalty and sending start and result messages."""
        user_id = callback.from_user.id
        penalty_data = await play_penalty(user_id)
        if "error" in penalty_data:
            await callback.message.answer(penalty_data["error"])
            return
        await callback.message.answer(penalty_data["start_msg"])
        await callback.message.answer(penalty_data["result"])

    @dp.callback_query(F.data == "matches")
    @check_user
    async def matches_handler(callback: CallbackQuery, state = None):
        """Handle matches callback by creating play button markup and sending requirements."""
        user_id = callback.from_user.id
        markup = await create_play_button_markup(user_id, "play_match")
        await callback.answer(await tr(user_id, 'messages.matches'))
        req_msg = await tr(user_id, 'messages.match_requirements')
        await callback.message.answer(req_msg, reply_markup=markup)

    @dp.callback_query(F.data == "play_match")
    @check_user
    async def play_match_handler(callback: CallbackQuery, state = None):
        """Handle play_match callback by simulating match and sending start and result messages."""
        user_id = callback.from_user.id
        match_data = await play_match(user_id)
        if "error" in match_data:
            await callback.message.answer(match_data["error"])
            return
        await callback.message.answer(match_data["start_msg"])
        await callback.message.answer(match_data["result"])
