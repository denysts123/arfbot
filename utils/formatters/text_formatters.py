from db.database import Database

from utils.i18n import tr
from utils.user_fields import *

db = Database()


async def format_welcome_message(user_id: int, user_data: tuple) -> str:
    """Format the welcome message for a user using their data and translated text."""
    text = await tr(user_id, 'messages.welcome')
    return text.format(
        user_id=user_data[USER_ID],
        username=user_data[USERNAME],
        coins=user_data[COINS],
        tickets=user_data[TICKETS],
        cups=user_data[CUPS],
        user_info=user_data[USER_INFO]
    )


async def format_full_info_message(user_id: int, stats: dict) -> str:
    """Format the full info message for a user using their stats and translated text."""
    text = await tr(user_id, 'messages.full_info')
    return text.format(
        username=stats["user_data"][USERNAME],
        coins=stats["user_data"][COINS],
        tickets=stats["user_data"][TICKETS],
        cups=stats["user_data"][CUPS],
        received_coins=stats["user_data"][RECEIVED_COINS],
        received_tickets=stats["user_data"][RECEIVED_TICKETS],
        games_played=stats["user_data"][GAMES_PLAYED],
        victories=stats["user_data"][VICTORIES],
        win_rate=stats['win_rate'],
        defeats=stats["user_data"][DEFEATS],
        draws=stats["user_data"][GAMES_PLAYED] - (stats["user_data"][VICTORIES] + stats["user_data"][DEFEATS]),
        small_packs=stats["user_data"][SMALL_PACKS],
        medium_packs=stats["user_data"][MEDIUM_PACKS],
        big_packs=stats["user_data"][BIG_PACKS],
        referrals=stats["user_data"][REFERRALS_COUNT],
        register_date=stats["user_data"][REGISTER_DATE],
        ghost_small=stats["user_data"][GHOST_SMALL_PACKS],
        ghost_medium=stats["user_data"][GHOST_MEDIUM_PACKS],
        ghost_big=stats["user_data"][GHOST_BIG_PACKS],
        ghost_success=stats['ghost_success'],
        success=stats['success'],
        position=stats['position'],
        rank=None,
        fp_level=None
    )
