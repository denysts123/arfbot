from utils import logger
from db.database import Database
import game.constants as constants

class User:
    def __init__(self, user_id: int):
        self.db = Database()
        self.user_id = user_id
    
    async def get_user(self) -> tuple | None:
        """Retrieve user data."""
        user = await self.db.get_user(self.user_id)
        logger.info(f"Retrieved user data for user ID {self.user_id}")
        if user is None:
            logger.warning(f"User with ID {self.user_id} does not exist.")
            return None
        return user
    
    async def get_user_position(self) -> int:
        """Retrieve user's position in the leaderboard."""
        position = await self.db.get_user_position(self.user_id)
        return position
    
    async def get_win_rate_percent(self) -> float:
        """Calculate and return the win rate percentage."""
        user_data = await self.db.get_user(self.user_id)
        if user_data is None:
            return 0.0
        wins = user_data[11]
        total_matches = user_data[13]
        if total_matches == 0:
            return 0.0
        return (wins / total_matches) * 100
    
    async def calculate_success(self) -> int:
        """Calculate and return the user's success."""
        user_data = await self.db.get_user(self.user_id)
        if user_data is None:
            return 0
    
        victories = user_data[11]
        defeats = user_data[12]
        small_packs = user_data[22]
        medium_packs = user_data[23]
        big_packs = user_data[24]
        referrals_count = user_data[16]
    
        skill = victories * constants.VICTORY_COEFFICIENT + defeats * constants.DEFEAT_COEFFICIENT
        resources = (small_packs * constants.SMALL_PACK_COEFFICIENT +
                     medium_packs * constants.MEDIUM_PACK_COEFFICIENT +
                     big_packs * constants.BIG_PACK_COEFFICIENT)
        bonus = referrals_count * constants.REFERRALS_COEFFICIENT
    
        return skill + resources + bonus - await self.calculate_ghost_success()

    async def calculate_ghost_success(self) -> int:
        """Calculate and return the ghost success."""
        user_data = await self.db.get_user(self.user_id)
        if user_data is None:
            return 0
    
        ghost_small_packs = user_data[19]
        ghost_medium_packs = user_data[20]
        ghost_big_packs = user_data[21]
    
        return (ghost_small_packs * constants.GHOST_SMALL_PACKS_COEFFICIENT +
                ghost_medium_packs * constants.GHOST_MEDIUM_PACKS_COEFFICIENT +
                ghost_big_packs * constants.GHOST_BIG_PACKS_COEFFICIENT)
    
    async def is_banned(self) -> bool:
        """Check if the user is banned."""
        return await self.db.is_banned(self.user_id)
    
    async def get_ban_date(self) -> str | None:
        """Retrieve the ban end date for the user."""
        return await self.db.get_ban_date(self.user_id)
