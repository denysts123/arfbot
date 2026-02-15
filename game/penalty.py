"""
Penalty game module.
Provides functions for playing penalty mini-game.
"""

import asyncio
import random

import game.constants as constants
from db.database import Database
from utils.i18n import tr
from utils.logging import logger
from utils.user import get_user
from utils.user_fields import PENALTY_LEFT, SUCCESS

db = Database()


async def play_penalty(user_id: int) -> dict:
    """
    Simulate a penalty series for the user.
    Checks attempts, deducts one, simulates goals, updates coins and returns result messages.
    """
    user_data = await get_user(user_id)
    if user_data[PENALTY_LEFT] <= 0:
        return {"error": await tr(user_id, 'messages.no_attempts_left')}

    logger.info(f"User {user_id} started penalty game")

    await db.update_user("UPDATE Users SET PenaltyLeft = PenaltyLeft - 1 WHERE UserId = ?", (user_id,))

    match_started_msg = await tr(user_id, 'messages.match_started')

    wait_time = random.randint(constants.PENALTY_WAIT_MIN, constants.PENALTY_WAIT_MAX)
    await asyncio.sleep(wait_time)

    success_goals = random.randint(constants.PENALTY_MIN_GOALS, constants.PENALTY_MAX_GOALS)
    reward = success_goals * constants.PENALTY_GOAL_REWARD

    await db.update_user(
        "UPDATE Users SET Coins = Coins + ?, ReceivedCoins = ReceivedCoins + ?, PenaltyScored = PenaltyScored + ? WHERE UserId = ?",
        (reward, reward, success_goals, user_id),
    )

    logger.info(f"User {user_id} scored {success_goals} goals in penalty, earned {reward} coins")
    await db.log_action(user_id, "penalty", reward, f"Scored {success_goals} goals")

    left = user_data[PENALTY_LEFT] - 1
    penalty_result_msg = await tr(user_id, 'messages.penalty_result')
    result = penalty_result_msg.format(goals=success_goals, reward=reward, left=left)

    return {"start_msg": match_started_msg, "result": result}


async def check_penalty_access(user_id: int) -> bool:
    """Check if the user has enough success to access penalty mode."""
    user_data = await get_user(user_id)
    if user_data is None:
        return False
    return user_data[SUCCESS] >= constants.PENALTY_SUCCESS_REQUIREMENT
