from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Tuple

import aiosqlite

from utils.logging import logger

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Database:
    """Handles all database operations for the application."""
    
    def __init__(self):
        """Initialize the database connection path."""
        self.db_path = getenv("DB_PATH")
        if not self.db_path:
            logger.critical("DB_PATH environment variable not set.")
    
    async def _execute_query(self, query: str, params: tuple = (), fetchone: bool = False, fetchall: bool = False):
        """Execute a query with optional parameters, returning results if specified."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                if fetchone:
                    result = await cursor.fetchone()
                elif fetchall:
                    result = await cursor.fetchall()
                else:
                    result = None
                await cursor.close()
                return result
        except Exception as e:
            logger.error(f"Error executing query '{query}': {e}")
            return None

    async def get_user(self, user_id: int) -> Optional[Tuple] | None:
        """Retrieve user data from the database by user ID."""
        logger.debug(f"Executing query to get user {user_id}.")
        user = await self._execute_query("SELECT * FROM Users WHERE UserId = ?", (user_id,), fetchone=True)
        if user:
            logger.debug(f"User {user_id} found in database.")
            return user
        else:
            logger.debug(f"User {user_id} not found in database.")
            return None

    async def get_user_position(self, user_id: int) -> Optional[int] | None:
        """Retrieve user's position in the leaderboard based on success score."""
        logger.debug(f"Executing query to get position for user {user_id}.")
        position = await self._execute_query("SELECT COUNT(*) + 1 FROM LeaderboardUsers WHERE Success > "
                                             "(SELECT Success FROM LeaderboardUsers WHERE UserId = ?)",
                                             (user_id,), fetchone=True)
        if position:
            logger.debug(f"Position for user {user_id}: {position[0]}.")
            return position[0]
        else:
            logger.debug(f"No position found for user {user_id}.")
            return None
    async def is_banned(self, user_id: int) -> bool:
        """Check if a user is banned by querying the IsBanned field."""
        logger.debug(f"Executing query to check ban status for user {user_id}.")
        result = await self._execute_query("SELECT IsBanned FROM Users WHERE UserId = ?", (user_id,),
                                           fetchone=True)
        if result:
            logger.debug(f"Ban status for user {user_id}: {result[0] == 1}.")
            return result[0] == 1
        else:
            logger.debug(f"No ban data found for user {user_id}.")
            return False
    
    async def get_ban_date(self, user_id: int) -> Optional[str] | None:
        """Retrieve the ban end date for a user."""
        logger.debug(f"Executing query to get ban date for user {user_id}.")
        result = await self._execute_query("SELECT BanEnd FROM Users WHERE UserId = ?", (user_id,),
                                           fetchone=True)
        if result:
            logger.debug(f"Ban date for user {user_id}: {result[0]}.")
            return result[0]
        else:
            logger.debug(f"No ban date found for user {user_id}.")
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
                await db.execute("UPDATE users SET Lang = ? WHERE UserId = ?", (lang, user_id))
                await db.commit()
                logger.info(f"Language updated for user {user_id} to {lang}.")
        except Exception as e:
            logger.error(f"Error updating language for user {user_id}: {e}")

    async def get_all_users(self) -> list[int]:
        """Get list of all user IDs."""
        logger.debug("Getting all user IDs.")
        rows = await self._execute_query("SELECT UserId FROM users", fetchall=True)
        return [row[0] for row in rows] if rows else []

    async def execute_update(self, query: str, params: tuple = ()) -> None:
        """Execute an update query."""
        logger.debug(f"Executing update: {query} with params {params}")
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(query, params)
                await db.commit()
        except Exception as e:
            logger.error(f"Error executing update: {e}")

    async def get_nearby_opponents(self, user_id: int) -> list[int]:
        """Get list of nearby opponents based on leaderboard position (within 2 places up or down)."""
        logger.debug(f"Getting nearby opponents for user {user_id}.")
        position = await self.get_user_position(user_id)
        if position is None:
            return []
        
        start_pos = max(1, position - 2)
        end_pos = position + 2
        limit = end_pos - start_pos + 1
        offset = start_pos - 1
        
        rows = await self._execute_query("SELECT UserId FROM LeaderboardUsers ORDER BY Success DESC "
                                         "LIMIT ? OFFSET ?", (limit, offset), fetchall=True)
        opponents = [row[0] for row in rows if row[0] != user_id] if rows else []
        return opponents

