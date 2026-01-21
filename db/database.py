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
    
    async def get_user(self, user_id: int):
        """Retrieve user data from the database by user ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT * FROM Users WHERE UserId = ?", (user_id,))
                user = await cursor.fetchone()
                await cursor.close()
                if user:
                    return user
                else:
                    return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {e}")
            return None