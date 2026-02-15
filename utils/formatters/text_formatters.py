"""
Text formatters module.
Provides functions for formatting user-facing messages.
"""

from utils.i18n import tr
from utils.user_fields import *


async def format_welcome_message(user_id: int, user_data: tuple) -> str:
    """Format the welcome message for a user using their data."""
    text = await tr(user_id, 'messages.welcome')
    return text.format(
        user_id=user_data[USER_ID],
        username=user_data[USERNAME],
        coins=user_data[COINS],
        tickets=user_data[TICKETS],
        cups=user_data[CUPS],
        user_info=user_data[USER_INFO] or ""
    )


async def format_full_info_message(user_id: int, stats: dict) -> str:
    """Format the full info message for a user using their stats."""
    ud = stats["user_data"]
    draws = ud[GAMES_PLAYED] - (ud[VICTORIES] + ud[DEFEATS])

    text = await tr(user_id, 'messages.full_info')
    return text.format(
        username=ud[USERNAME],
        coins=ud[COINS],
        tickets=ud[TICKETS],
        cups=ud[CUPS],
        received_coins=ud[RECEIVED_COINS],
        received_tickets=ud[RECEIVED_TICKETS],
        games_played=ud[GAMES_PLAYED],
        victories=ud[VICTORIES],
        win_rate=stats['win_rate'],
        defeats=ud[DEFEATS],
        draws=draws,
        small_packs=ud[SMALL_PACKS],
        medium_packs=ud[MEDIUM_PACKS],
        big_packs=ud[BIG_PACKS],
        referrals=ud[REFERRALS_COUNT],
        register_date=ud[REGISTER_DATE],
        ghost_small=ud[GHOST_SMALL_PACKS],
        ghost_medium=ud[GHOST_MEDIUM_PACKS],
        ghost_big=ud[GHOST_BIG_PACKS],
        ghost_success=stats['ghost_success'],
        success=stats['success'],
        position=stats['position'],
        rank=None,
        fp_level=None
    )
