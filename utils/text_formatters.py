from db.database import Database
from utils.localization import tr

db = Database()


async def format_welcome_message(user_id: int, user_data: tuple) -> str:
    """Format the welcome message for a user."""
    text = await tr(user_id, 'messages.welcome')
    return text.format(
        user_id=user_data[0],
        username=user_data[1],
        coins=user_data[8],
        tickets=user_data[9],
        cups=user_data[10],
        user_info=user_data[2]
    )


async def format_full_info_message(user_id: int, stats: dict) -> str:
    """Format the full info message for a user."""
    text = await tr(user_id, 'messages.full_info')
    return text.format(
        username=stats["user_data"][1],
        coins=stats["user_data"][8],
        tickets=stats["user_data"][9],
        cups=stats["user_data"][10],
        received_coins=stats["user_data"][17],
        received_tickets=stats["user_data"][18],
        games_played=stats["user_data"][13],
        victories=stats["user_data"][11],
        win_rate=stats['win_rate'],
        defeats=stats["user_data"][12],
        draws=stats["user_data"][13] - (stats["user_data"][11] + stats["user_data"][12]),
        small_packs=stats["user_data"][22],
        medium_packs=stats["user_data"][23],
        big_packs=stats["user_data"][24],
        referrals=stats["user_data"][16],
        register_date=stats["user_data"][29],
        ghost_small=stats["user_data"][19],
        ghost_medium=stats["user_data"][20],
        ghost_big=stats["user_data"][21],
        ghost_success=stats['ghost_success'],
        success=stats['success'],
        position=stats['position'],
        rank=None,
        fp_level=None
    )
