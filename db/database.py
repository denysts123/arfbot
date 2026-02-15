"""
Database module for handling all database operations.
Provides async methods for user management and queries.
"""
from os import getenv
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
import aiosqlite

from core.logger import logger

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


class Database:
    """Handles all database operations for the application."""
    
    def __init__(self):
        """Initialize the database connection path."""
        self.db_path = getenv("DB_PATH")
    
    async def _execute(self, query: str, params: tuple = (), fetch: str = None):
        """
        Execute a query with optional parameters.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: 'one' for fetchone, 'all' for fetchall, None for no fetch
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, params)
                if fetch == "one":
                    result = await cursor.fetchone()
                elif fetch == "all":
                    result = await cursor.fetchall()
                else:
                    await db.commit()
                    result = None
                await cursor.close()
                return result
        except Exception as e:
            logger.error(f"Database error: {e}")
            return None

    async def get_user(self, user_id: int) -> Optional[tuple]:
        """Retrieve user data from the database by user ID."""
        logger.debug(f"Fetching user {user_id}")
        return await self._execute("SELECT * FROM Users WHERE UserId = ?", (user_id,), fetch="one")

    async def get_user_position(self, user_id: int) -> Optional[int]:
        """Retrieve user's position in the leaderboard based on Success score."""
        logger.debug(f"Getting leaderboard position for user {user_id}")
        result = await self._execute(
            "SELECT COUNT(*) + 1 FROM Users WHERE Success > (SELECT Success FROM Users WHERE UserId = ?)",
            (user_id,), fetch="one"
        )
        return result[0] if result else None
    
    async def is_banned(self, user_id: int) -> bool:
        """Check if a user is banned."""
        result = await self._execute("SELECT IsBanned FROM Users WHERE UserId = ?", (user_id,), fetch="one")
        return result[0] == 1 if result else False
    
    async def get_ban_date(self, user_id: int) -> Optional[str]:
        """Retrieve the ban end date for a user."""
        result = await self._execute("SELECT BanEnd FROM Users WHERE UserId = ?", (user_id,), fetch="one")
        return result[0] if result else None

    async def get_user_lang(self, user_id: int) -> Optional[str]:
        """Retrieve the language preference for a user."""
        result = await self._execute("SELECT Lang FROM Users WHERE UserId = ?", (user_id,), fetch="one")
        return result[0] if result else None

    async def create_user(self, user_id: int, username: str, lang: str) -> None:
        """Create a new user in the database."""
        logger.info(f"Creating new user {user_id} with username '{username}'")
        await self._execute(
            "INSERT INTO Users (UserId, Username, Lang) VALUES (?, ?, ?)",
            (user_id, username, lang)
        )

    async def update_user_lang(self, user_id: int, lang: str) -> None:
        """Update the language preference for a user."""
        logger.info(f"Updating language for user {user_id} to {lang}")
        await self._execute("UPDATE Users SET Lang = ? WHERE UserId = ?", (lang, user_id))

    async def get_all_user_ids(self) -> list[int]:
        """Get list of all user IDs."""
        rows = await self._execute("SELECT UserId FROM Users", fetch="all")
        return [row[0] for row in rows] if rows else []

    async def update_user(self, query: str, params: tuple = ()) -> None:
        """Execute an update query on Users table."""
        logger.debug(f"Executing update: {query[:50]}...")
        await self._execute(query, params)

    async def get_nearby_opponents(self, user_id: int) -> list[int]:
        """Get list of nearby opponents based on Success score (within 2 positions)."""
        logger.debug(f"Getting nearby opponents for user {user_id}")
        position = await self.get_user_position(user_id)
        if position is None:
            return []
        
        start_pos = max(1, position - 2)
        end_pos = position + 2
        limit = end_pos - start_pos + 1
        offset = start_pos - 1
        
        rows = await self._execute(
            "SELECT UserId FROM Users ORDER BY Success DESC LIMIT ? OFFSET ?",
            (limit, offset), fetch="all"
        )
        return [row[0] for row in rows if row[0] != user_id] if rows else []

    async def log_action(self, user_id: int, action_type: str, amount: int = None, message: str = None) -> None:
        """Log a user action to the History table."""
        await self._execute(
            "INSERT INTO History (TargetUserId, ActionType, Amount, LogMessage) VALUES (?, ?, ?, ?)",
            (user_id, action_type, amount, message)
        )
