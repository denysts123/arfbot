import game.constants as constants
from utils.user_fields import *


def calculate_success(user_data: tuple) -> int:
    """Calculate the user's success score based on victories, defeats, packs, and referrals, subtracting ghost success."""
    victories, defeats = user_data[VICTORIES], user_data[DEFEATS]
    small_packs, medium_packs, big_packs = user_data[SMALL_PACKS], user_data[MEDIUM_PACKS], user_data[BIG_PACKS]
    referrals_count = user_data[REFERRALS_COUNT]

    skill = victories * constants.VICTORY_COEFFICIENT + defeats * constants.DEFEAT_COEFFICIENT
    resources = (small_packs * constants.SMALL_PACK_COEFFICIENT +
                 medium_packs * constants.MEDIUM_PACK_COEFFICIENT +
                 big_packs * constants.BIG_PACK_COEFFICIENT)
    bonus = referrals_count * constants.REFERRALS_COEFFICIENT

    ghost_success = sum(user_data[i] * getattr(constants, f'GHOST_{["SMALL", "MEDIUM", "BIG"][i-GHOST_SMALL_PACKS]}_PACKS_COEFFICIENT')
                       for i in range(GHOST_SMALL_PACKS, GHOST_BIG_PACKS + 1))

    return skill + resources + bonus - ghost_success


def calculate_win_rate(victories: int, games_played: int) -> float:
    """Calculate the win rate percentage from victories and total games played."""
    return (victories / games_played) * 100 if games_played > 0 else 0.0
