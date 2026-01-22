from os import getenv
from dotenv import load_dotenv
from typing import Optional, Tuple

import aiosqlite

from utils import logger

load_dotenv(dotenv_path="../.env")

class Database:
    """Handles all database operations for the application."""
    
    def __init__(self):
        """Initialize the database connection path."""
        self.db_path = getenv("DB_PATH")
        if not self.db_path:
            logger.critical("DB_PATH environment variable not set.")
    
    async def get_user(self, user_id: int) -> Optional[Tuple] | None:
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

    async def get_user_position(self, user_id: int) -> Optional[int] | None:
        """Retrieve user's position in the leaderboard based on success score."""
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
        """Check if a user is banned by querying the IsBanned field."""
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
    
    async def get_ban_date(self, user_id: int) -> Optional[str] | None:
        """Retrieve the ban end date for a user."""
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

    async def create_user(self, user_id: int, username: str, lang: str) -> None:
        """Create a new user in the database with the provided details."""
        logger.debug(f"Creating new user {user_id} with lang {lang}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO Users (UserId, Username, Lang, RegisterDate)
                    VALUES (?, ?, ?, datetime('now'))
                """, (user_id, username, lang))
                await db.commit()
                logger.info(f"User {user_id} created successfully.")
        except Exception as e:
            logger.error(f"Error creating user {user_id}: {e}")

    async def update_user_lang(self, user_id: int, lang: str) -> None:
        """Update the language for a user."""
        logger.debug(f"Updating language for user {user_id} to {lang}.")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE Users SET Lang = ? WHERE UserId = ?", (lang, user_id))
                await db.commit()
                logger.info(f"Language updated for user {user_id} to {lang}.")
        except Exception as e:
            logger.error(f"Error updating language for user {user_id}: {e}")
