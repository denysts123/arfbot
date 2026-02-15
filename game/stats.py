"""
Game statistics calculation module.
Provides functions for calculating success scores and win rates.
"""
from core.config import (
    VICTORIES, DEFEATS, SMALL_PACKS, MEDIUM_PACKS, BIG_PACKS,
    GHOST_SMALL_PACKS, GHOST_BIG_PACKS, REFERRALS_COUNT,
    VICTORY_COEFFICIENT, DEFEAT_COEFFICIENT,
    SMALL_PACK_COEFFICIENT, MEDIUM_PACK_COEFFICIENT, BIG_PACK_COEFFICIENT,
    GHOST_SMALL_PACKS_COEFFICIENT, GHOST_MEDIUM_PACKS_COEFFICIENT, GHOST_BIG_PACKS_COEFFICIENT,
    REFERRALS_COEFFICIENT
)


def calculate_success(user_data: tuple) -> int:
    """
    Calculate the user's success score based on victories, defeats, packs, and referrals.
    Ghost packs are subtracted from the total.
    """
    skill = user_data[VICTORIES] * VICTORY_COEFFICIENT + user_data[DEFEATS] * DEFEAT_COEFFICIENT

    resources = (
        user_data[SMALL_PACKS] * SMALL_PACK_COEFFICIENT +
        user_data[MEDIUM_PACKS] * MEDIUM_PACK_COEFFICIENT +
        user_data[BIG_PACKS] * BIG_PACK_COEFFICIENT
    )

    bonus = user_data[REFERRALS_COUNT] * REFERRALS_COEFFICIENT

    ghost_coefficients = [
        GHOST_SMALL_PACKS_COEFFICIENT,
        GHOST_MEDIUM_PACKS_COEFFICIENT,
        GHOST_BIG_PACKS_COEFFICIENT
    ]
    ghost_success = sum(
        user_data[i] * ghost_coefficients[i - GHOST_SMALL_PACKS]
        for i in range(GHOST_SMALL_PACKS, GHOST_BIG_PACKS + 1)
    )

    return skill + resources + bonus - ghost_success


def calculate_win_rate(victories: int, games_played: int) -> float:
    """Calculate the win rate percentage from victories and total games played."""
    return (victories / games_played) * 100 if games_played > 0 else 0.0
