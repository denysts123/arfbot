"""
Pytest configuration and shared fixtures.
"""
import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_user_data():
    """Create mock user data tuple matching database schema."""
    return (
        123456789,      # USER_ID = 0
        "TestUser",     # USERNAME = 1
        "Test info",    # USER_INFO = 2
        None,           # USER_AVATAR_ID = 3
        "testuser",     # TELEGRAM_USERNAME = 4
        "Test",         # TELEGRAM_FIRST_NAME = 5
        "User",         # TELEGRAM_LAST_NAME = 6
        None,           # TELEGRAM_PHONE_NUMBER = 7
        50000,          # COINS = 8
        10,             # TICKETS = 9
        100,            # CUPS = 10
        15,             # VICTORIES = 11
        5,              # DEFEATS = 12
        20,             # GAMES_PLAYED = 13
        3,              # PENALTY_LEFT = 14
        10,             # PENALTY_SCORED = 15
        2,              # REFERRALS_COUNT = 16
        75000,          # RECEIVED_COINS = 17
        25,             # RECEIVED_TICKETS = 18
        5,              # SMALL_PACKS = 19
        3,              # MEDIUM_PACKS = 20
        1,              # BIG_PACKS = 21
        1,              # GHOST_SMALL_PACKS = 22
        0,              # GHOST_MEDIUM_PACKS = 23
        0,              # GHOST_BIG_PACKS = 24
        0,              # IS_BANNED = 25
        None,           # BAN_END = 26
        0,              # WARNS = 27
        1,              # LEVEL = 28
        "2026-01-01",   # REGISTER_DATE = 29
        "en_US",        # LANG = 30
        30000,          # SUCCESS = 31
    )


@pytest.fixture
def mock_user_data_zero_games():
    """Create mock user data with zero games played."""
    return (
        999999999, "NewUser", None, None, "newuser", "New", "User", None,
        10000, 15, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None, 0, 1,
        "2026-02-01", "en_US", 0
    )

