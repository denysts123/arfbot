import asyncio
import random

import game.constants as constants
from db.database import Database
from utils.i18n import tr
from utils.user import get_user, get_full_stats
from utils.user_fields import *


async def play_penalty(user_id: int) -> dict:
    """Simulate a penalty series for the user, checking attempts, deducting one attempt, waiting a random time, simulating goals, updating coins and received coins, and returning messages for start and result."""
    user_data = await get_user(user_id)
    if user_data[PENALTY_LEFT] <= 0:
        return {"error": await tr(user_id, 'messages.no_attempts_left')}

    match_started_msg = await tr(user_id, 'messages.match_started')

    db = Database()
    await db.execute_update("UPDATE users SET PenaltyLeft = PenaltyLeft - 1 WHERE UserId = ?", (user_id,))
    wait_time = random.randint(constants.PENALTY_WAIT_MIN, constants.PENALTY_WAIT_MAX)
    await asyncio.sleep(wait_time)

    success_goals = random.randint(constants.PENALTY_MIN_GOALS, constants.PENALTY_MAX_GOALS)
    reward = success_goals * constants.PENALTY_GOAL_REWARD
    await db.execute_update("UPDATE users SET Coins = Coins + ?, ReceivedCoins = ReceivedCoins + ? WHERE UserId = ?", (reward, reward, user_id))
    left = user_data[PENALTY_LEFT] - 1
    penalty_result_msg = await tr(user_id, 'messages.penalty_result')
    result = penalty_result_msg.format(goals=success_goals, reward=reward, left=left)

    return {"start_msg": match_started_msg, "result": result}


async def check_penalty_access(user_id: int) -> bool:
    """Check if the user has enough success to access penalty mode."""
    stats = await get_full_stats(user_id)
    return stats['success'] >= constants.PENALTY_SUCCESS_REQUIREMENT
