import asyncio
from db.database import Database

import game.constants as constants
from game.stats import calculate_success, calculate_win_rate
from utils.logging import logger
from utils.user_fields import *

db = Database()


async def get_user(user_id: int) -> tuple | None:
    """Retrieve user data from the database by user ID, logging the process."""
    logger.debug(f"Fetching user data for user_id {user_id}.")
    user = await db.get_user(user_id)
    logger.info(f"Retrieved user data for user ID {user_id}")
    if user is None:
        logger.warning(f"User with ID {user_id} does not exist.")
        return None
    return user


async def is_banned(user_id: int) -> bool:
    """Check if a user is banned by querying the database."""
    logger.debug(f"Checking ban status for user_id {user_id}.")
    return await db.is_banned(user_id)


async def get_ban_date(user_id: int) -> str | None:
    """Retrieve the ban end date for a user from the database."""
    logger.debug(f"Fetching ban date for user_id {user_id}.")
    return await db.get_ban_date(user_id)


async def create_user(user_id: int, name: str, lang: str) -> None:
    """Create a new user in the database with the provided name and language."""
    logger.debug(f"Creating new user for user_id {user_id}.")
    await db.create_user(user_id, name, lang)


async def get_full_stats(user_id: int) -> dict | None:
    """Calculate and return comprehensive user statistics including win rate, success, and position by
    gathering data from database and computing values."""
    logger.debug(f"Fetching full stats for user_id {user_id}.")
    user_data, position = await asyncio.gather(db.get_user(user_id), db.get_user_position(user_id))
    if user_data is None:
        logger.warning(f"User data not found for user_id {user_id} in get_full_stats.")
        return None

    wins = user_data[VICTORIES]
    total_matches = user_data[GAMES_PLAYED]
    win_rate = calculate_win_rate(wins, total_matches)

    success = calculate_success(user_data)

    ghost_success = sum(user_data[i] * getattr(constants, f'GHOST_{["SMALL", "MEDIUM", "BIG"][i-GHOST_SMALL_PACKS]}_PACKS_COEFFICIENT')
                       for i in range(GHOST_SMALL_PACKS, GHOST_BIG_PACKS + 1))

    logger.debug(f"Calculated stats for user_id {user_id}: success={success}, position={position}.")
    return {
        "user_data": user_data,
        "win_rate": win_rate,
        "success": success,
        "ghost_success": ghost_success,
        "position": position
    }


async def change_user_lang(user_id: int, lang: str) -> None:
    """Change the user's language in the database and update the cache."""
    logger.debug(f"Changing language for user_id {user_id} to {lang}.")
    await db.update_user_lang(user_id, lang)
    from utils.i18n import update_user_lang_cache
    update_user_lang_cache(user_id, lang)
