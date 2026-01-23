import asyncio
import random

import game.constants as constants
from db.database import Database
from utils.i18n import tr, get_loss_reasons
from utils.user import get_user, get_full_stats
from utils.user_fields import *


async def play_match(user_id: int) -> dict:
    """Simulate a match for the user, deducting resources, finding a nearby opponent from the
    leaderboard, simulating scores, determining the result, updating the database, and returning
    messages for start and result."""
    user_data = await get_user(user_id)
    if user_data[COINS] < constants.MATCH_COST_COINS or user_data[TICKETS] < constants.MATCH_COST_TICKETS:
        return {"error": await tr(user_id, 'messages.insufficient_resources')}

    db = Database()
    await db.execute_update("UPDATE users SET Coins = Coins - ?, Tickets = Tickets - ? WHERE UserId = ?",
                            (constants.MATCH_COST_COINS, constants.MATCH_COST_TICKETS, user_id))

    nearby_opponents = await db.get_nearby_opponents(user_id)
    if not nearby_opponents:
        return {"error": await tr(user_id, 'messages.no_opponents')}

    best_opponent = random.choice(nearby_opponents)
    opp_data = await get_user(best_opponent)
    opp_name = opp_data[USERNAME]
    opp_stats = await get_full_stats(best_opponent)
    opp_success = opp_stats['success']
    match_start_msg = await tr(user_id, 'messages.match_start')

    await asyncio.sleep(random.randint(constants.MATCH_WAIT_MIN, constants.MATCH_WAIT_MAX))
    player1_score = random.randint(constants.MATCH_MIN_SCORE, constants.MATCH_MAX_SCORE)
    player2_score = random.randint(constants.MATCH_MIN_SCORE, constants.MATCH_MAX_SCORE)

    result = ""
    if player1_score > player2_score:
        update_query = ("UPDATE users SET Coins = Coins + ?, Cups = Cups + ?, Victories = Victories + 1, "
                        "GamesPlayed = GamesPlayed + 1 WHERE UserId = ?")
        params = (constants.MATCH_WIN_COINS_REWARD, constants.MATCH_WIN_CUPS_REWARD, user_id)
        result_msg = await tr(user_id, 'messages.match_win')
        result = result_msg.format(score1=player1_score, score2=player2_score)
    elif player1_score < player2_score:
        loss_reasons = get_loss_reasons(user_id)
        reason = random.choice(loss_reasons)
        update_query = ("UPDATE users SET Defeats = Defeats + 1, GamesPlayed = GamesPlayed + 1 WHERE "
                        "UserId = ?")
        params = (user_id,)
        result_msg = await tr(user_id, 'messages.match_lose')
        result = result_msg.format(score1=player1_score, score2=player2_score, reason=reason)
    else:
        update_query = "UPDATE users SET GamesPlayed = GamesPlayed + 1 WHERE UserId = ?"
        params = (user_id,)
        result_msg = await tr(user_id, 'messages.match_draw')
        result = result_msg.format(score1=player1_score, score2=player2_score)

    await db.execute_update(update_query, params)

    return {"start_msg": match_start_msg.format(opponent=opp_name, success=opp_success), "result": result}
