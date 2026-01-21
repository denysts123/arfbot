from typing import Any
from utils import logger
from db.database import Database

class User:
    def __init__(self, user_id: int):
        self.db = Database()
        self.user_id = user_id
    
    async def get_user(self) -> Any:
        """Retrieve user data."""
        user = await self.db.get_user(self.user_id)
        logger.info(f"Retrieved user data for user ID {self.user_id}")
        if user is None:
            logger.warning(f"User with ID {self.user_id} does not exist.")
            return False
        return user