from os import getenv
from dotenv import load_dotenv

import aiosqlite

from utils import logger

load_dotenv(dotenv_path="../.env")

class Database:
    def __init__(self):
        self.db_path = getenv("DB_PATH")
        if not self.db_path:
            logger.critical(f"DB_PATH environment variable not set.")
    
    async def get_user(self, user_id: int) -> tuple | None:
        """Retrieve user data from the database by user ID."""
        logger.debug(f"Executing query to get user {user_id}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT * FROM Users WHERE UserId = ?", (user_id,))
                user = await cursor.fetchone()
                await cursor.close()
                if user:
                    logger.debug(f"User {user_id} found in database.")
                    return user
                else:
                    logger.debug(f"User {user_id} not found in database.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None

    async def get_user_position(self, user_id: int) -> int | None:
        """Retrieve user's position in the leaderboard."""
        logger.debug(f"Executing query to get position for user {user_id}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT COUNT(*) + 1 FROM LeaderboardUsers WHERE Success > (SELECT Success "
                                          "FROM LeaderboardUsers WHERE UserId = ?)", (user_id,))
                position = await cursor.fetchone()
                await cursor.close()
                if position:
                    logger.debug(f"Position for user {user_id}: {position[0]}.")
                    return position[0]
                else:
                    logger.debug(f"No position found for user {user_id}.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving position for user {user_id}: {e}")
            return None
    
    async def is_banned(self, user_id: int) -> bool:
        """Check if a user is banned."""
        logger.debug(f"Executing query to check ban status for user {user_id}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT IsBanned FROM Users WHERE UserId = ?", (user_id,))
                result = await cursor.fetchone()
                await cursor.close()
                if result:
                    logger.debug(f"Ban status for user {user_id}: {result[0] == 1}.")
                    return result[0] == 1
                else:
                    logger.debug(f"No ban data found for user {user_id}.")
                    return False
        except Exception as e:
            logger.error(f"Error checking ban status for user {user_id}: {e}")
            return False
    
    async def get_ban_date(self, user_id: int) -> str | None:
        """Retrieve the ban date for a user."""
        logger.debug(f"Executing query to get ban date for user {user_id}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT BanEnd FROM Users WHERE UserId = ?", (user_id,))
                result = await cursor.fetchone()
                await cursor.close()
                if result:
                    logger.debug(f"Ban date for user {user_id}: {result[0]}.")
                    return result[0]
                else:
                    logger.debug(f"No ban date found for user {user_id}.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving ban date for user {user_id}: {e}")
            return None
