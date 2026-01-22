from aiogram.types import Message

from utils import logger
import game.constants as constants
from db.database import Database

db = Database()


async def get_user(user_id: int) -> tuple | None:
    """Получить данные пользователя из базы данных."""
    logger.debug(f"Fetching user data for user_id {user_id}.")
    user = await db.get_user(user_id)
    logger.info(f"Retrieved user data for user ID {user_id}")
    if user is None:
        logger.warning(f"User with ID {user_id} does not exist.")
        return None
    return user


async def is_banned(user_id: int) -> bool:
    """Проверить, забанен ли пользователь."""
    logger.debug(f"Checking ban status for user_id {user_id}.")
    return await db.is_banned(user_id)


async def get_ban_date(user_id: int) -> str | None:
    """Получить дату окончания бана пользователя."""
    logger.debug(f"Fetching ban date for user_id {user_id}.")
    return await db.get_ban_date(user_id)


async def create_user(user_id: int, message: Message) -> None:
    """Создать нового пользователя. Пока пустая функция для будущей реализации."""
    logger.debug(f"Creating new user for user_id {user_id}.")
    pass


async def get_full_stats(user_id: int) -> dict | None:
    """Получить все статистики пользователя в одном словаре."""
    logger.debug(f"Fetching full stats for user_id {user_id}.")
    user_data = await db.get_user(user_id)
    if user_data is None:
        logger.warning(f"User data not found for user_id {user_id} in get_full_stats.")
        return None

    wins = user_data[11]
    total_matches = user_data[13]
    win_rate = (wins / total_matches) * 100 if total_matches > 0 else 0.0

    victories = user_data[11]
    defeats = user_data[12]
    small_packs = user_data[22]
    medium_packs = user_data[23]
    big_packs = user_data[24]
    referrals_count = user_data[16]

    skill = victories * constants.VICTORY_COEFFICIENT + defeats * constants.DEFEAT_COEFFICIENT
    resources = (small_packs * constants.SMALL_PACK_COEFFICIENT +
                 medium_packs * constants.MEDIUM_PACK_COEFFICIENT +
                 big_packs * constants.BIG_PACK_COEFFICIENT)
    bonus = referrals_count * constants.REFERRALS_COEFFICIENT

    ghost_small_packs = user_data[19]
    ghost_medium_packs = user_data[20]
    ghost_big_packs = user_data[21]
    ghost_success = (ghost_small_packs * constants.GHOST_SMALL_PACKS_COEFFICIENT +
                     ghost_medium_packs * constants.GHOST_MEDIUM_PACKS_COEFFICIENT +
                     ghost_big_packs * constants.GHOST_BIG_PACKS_COEFFICIENT)

    success = skill + resources + bonus - ghost_success
    position = await db.get_user_position(user_id)

    logger.debug(f"Calculated stats for user_id {user_id}: success={success}, position={position}.")
    return {
        "user_data": user_data,
        "win_rate": win_rate,
        "success": success,
        "ghost_success": ghost_success,
        "position": position
    }
