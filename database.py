from os import getenv
from typing import Any

import aiosqlite

import logger

class Database:
    def __init__(self):
        self.db_path = getenv("DB_PATH")
        if not self.db_path:
            logger.critical(f"DB_PATH environment variable not set.")
    
    async def get_user(self, user_id: int):
        """Retrieve user data from the database by user ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT * FROM Users WHERE UserId = ?", (user_id,))
                user = await cursor.fetchone()
                await cursor.close()
                if user:
                    logger.info(f"User {user_id} successfully retrieved from database.")
                    return user
                else:
                    logger.warning(f"User {user_id} not found in database.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None
    
    async def get_user_field(self, user_id: int, field: str):
        """Retrieve a specific field of user data from the database by user ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = f"SELECT {field} FROM Users WHERE UserId = ?"
                cursor = await db.execute(query, (user_id,))
                result = await cursor.fetchone()
                await cursor.close()
                if result:
                    logger.info(f"Field '{field}' for user {user_id} successfully retrieved from database.")
                    return result[0]
                else:
                    logger.warning(f"User {user_id} not found in database.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving field '{field}' for user {user_id}: {e}")
            return None
    
    async def update_user_field(self, user_id: int, field: str, value: Any):
        """Update a specific field of user data in the database by user ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = f"UPDATE Users SET {field} = ? WHERE UserId = ?"
                await db.execute(query, (value, user_id))
                await db.commit()
                logger.info(f"Field '{field}' for user {user_id} successfully updated to '{value}'.")
        except Exception as e:
            logger.error(f"Error updating field '{field}' for user {user_id}: {e}")