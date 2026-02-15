"""
Game statistics calculation module.
Provides functions for calculating success scores and win rates.
"""

import game.constants as constants
from utils.user_fields import *


def calculate_success(user_data: tuple) -> int:
    """
    Calculate the user's success score based on victories, defeats, packs, and referrals.
    Ghost packs are subtracted from the total.
    """
    skill = user_data[VICTORIES] * constants.VICTORY_COEFFICIENT + user_data[DEFEATS] * constants.DEFEAT_COEFFICIENT

    resources = (
        user_data[SMALL_PACKS] * constants.SMALL_PACK_COEFFICIENT +
        user_data[MEDIUM_PACKS] * constants.MEDIUM_PACK_COEFFICIENT +
        user_data[BIG_PACKS] * constants.BIG_PACK_COEFFICIENT
    )

    bonus = user_data[REFERRALS_COUNT] * constants.REFERRALS_COEFFICIENT

    ghost_success = sum(
        user_data[i] * getattr(constants, f'GHOST_{["SMALL", "MEDIUM", "BIG"][i - GHOST_SMALL_PACKS]}_PACKS_COEFFICIENT')
        for i in range(GHOST_SMALL_PACKS, GHOST_BIG_PACKS + 1)
    )

    return skill + resources + bonus - ghost_success


def calculate_win_rate(victories: int, games_played: int) -> float:
    """Calculate the win rate percentage from victories and total games played."""
    return (victories / games_played) * 100 if games_played > 0 else 0.0
