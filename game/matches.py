"""
Match game module.
Provides functions for playing match against opponents.
"""

import asyncio
import random

import game.constants as constants
from db.database import Database
from utils.i18n import tr, get_loss_reasons
from utils.logging import logger
from utils.user import get_user
from utils.user_fields import COINS, TICKETS, USERNAME, SUCCESS

db = Database()


async def play_match(user_id: int) -> dict:
    """
    Simulate a match for the user.
    Deducts resources, finds opponent, simulates scores, updates database with results.
    """
    user_data = await get_user(user_id)
    if user_data[COINS] < constants.MATCH_COST_COINS or user_data[TICKETS] < constants.MATCH_COST_TICKETS:
        return {"error": await tr(user_id, 'messages.insufficient_resources')}

    logger.info(f"User {user_id} started match game")

    await db.update_user(
        "UPDATE Users SET Coins = Coins - ?, Tickets = Tickets - ? WHERE UserId = ?",
        (constants.MATCH_COST_COINS, constants.MATCH_COST_TICKETS, user_id)
    )

    nearby_opponents = await db.get_nearby_opponents(user_id)
    if not nearby_opponents:
        return {"error": await tr(user_id, 'messages.no_opponents')}

    opponent_id = random.choice(nearby_opponents)
    opp_data = await get_user(opponent_id)
    opp_name = opp_data[USERNAME]
    opp_success = opp_data[SUCCESS]

    match_start_msg = await tr(user_id, 'messages.match_start')

    await asyncio.sleep(random.randint(constants.MATCH_WAIT_MIN, constants.MATCH_WAIT_MAX))

    player1_score = random.randint(constants.MATCH_MIN_SCORE, constants.MATCH_MAX_SCORE)
    player2_score = random.randint(constants.MATCH_MIN_SCORE, constants.MATCH_MAX_SCORE)

    if player1_score > player2_score:
        await db.update_user(
            "UPDATE Users SET Coins = Coins + ?, Cups = Cups + ?, Victories = Victories + 1, GamesPlayed = GamesPlayed + 1 WHERE UserId = ?",
            (constants.MATCH_WIN_COINS_REWARD, constants.MATCH_WIN_CUPS_REWARD, user_id)
        )
        result_msg = await tr(user_id, 'messages.match_win')
        result = result_msg.format(score1=player1_score, score2=player2_score)
        logger.info(f"User {user_id} won match {player1_score}:{player2_score}")
        await db.log_action(user_id, "match_win", constants.MATCH_WIN_COINS_REWARD, f"Won {player1_score}:{player2_score}")

    elif player1_score < player2_score:
        loss_reasons = await get_loss_reasons(user_id)
        reason = random.choice(loss_reasons) if loss_reasons else "Bad luck"
        await db.update_user(
            "UPDATE Users SET Defeats = Defeats + 1, GamesPlayed = GamesPlayed + 1 WHERE UserId = ?",
            (user_id,)
        )
        result_msg = await tr(user_id, 'messages.match_lose')
        result = result_msg.format(score1=player1_score, score2=player2_score, reason=reason)
        logger.info(f"User {user_id} lost match {player1_score}:{player2_score}")
        await db.log_action(user_id, "match_lose", 0, f"Lost {player1_score}:{player2_score}")

    else:
        await db.update_user(
            "UPDATE Users SET GamesPlayed = GamesPlayed + 1 WHERE UserId = ?",
            (user_id,)
        )
        result_msg = await tr(user_id, 'messages.match_draw')
        result = result_msg.format(score1=player1_score, score2=player2_score)
        logger.info(f"User {user_id} drew match {player1_score}:{player2_score}")
        await db.log_action(user_id, "match_draw", 0, f"Draw {player1_score}:{player2_score}")

    return {"start_msg": match_start_msg.format(opponent=opp_name, success=opp_success), "result": result}
