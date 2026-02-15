"""
Tests for utils/user.py module.
"""
import pytest
from unittest.mock import AsyncMock, patch
from utils.user import _calculate_win_rate, get_full_stats
from core.config import VICTORIES, GAMES_PLAYED


class TestCalculateWinRate:
    """Tests for _calculate_win_rate function."""

    def test_normal_win_rate(self):
        """Test win rate calculation with normal values."""
        assert _calculate_win_rate(15, 20) == 75.0

    def test_zero_games(self):
        """Test returns 0.0 when no games played."""
        assert _calculate_win_rate(0, 0) == 0.0

    def test_all_wins(self):
        """Test 100% win rate."""
        assert _calculate_win_rate(50, 50) == 100.0

    def test_no_wins(self):
        """Test 0% win rate."""
        assert _calculate_win_rate(0, 10) == 0.0


class TestGetFullStats:
    """Tests for get_full_stats function."""

    @pytest.mark.asyncio
    async def test_returns_none_for_nonexistent_user(self):
        """Test returns None when user not found."""
        with patch("utils.user.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=None)
            mock_db.get_user_position = AsyncMock(return_value=None)
            result = await get_full_stats(999999)
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_dict_for_existing_user(self, mock_user_data):
        """Test returns dict with stats for existing user."""
        with patch("utils.user.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=mock_user_data)
            mock_db.get_user_position = AsyncMock(return_value=5)
            result = await get_full_stats(123456789)
            assert result is not None
            assert isinstance(result, dict)
            assert "user_data" in result
            assert "win_rate" in result
            assert "success" in result
            assert "ghost_success" in result
            assert "position" in result

    @pytest.mark.asyncio
    async def test_calculates_win_rate_correctly(self, mock_user_data):
        """Test win rate is calculated correctly."""
        with patch("utils.user.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=mock_user_data)
            mock_db.get_user_position = AsyncMock(return_value=1)
            result = await get_full_stats(123456789)
            expected = (mock_user_data[VICTORIES] / mock_user_data[GAMES_PLAYED]) * 100
            assert result["win_rate"] == expected

    @pytest.mark.asyncio
    async def test_includes_position(self, mock_user_data):
        """Test position is included in result."""
        with patch("utils.user.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=mock_user_data)
            mock_db.get_user_position = AsyncMock(return_value=42)
            result = await get_full_stats(123456789)
            assert result["position"] == 42

    @pytest.mark.asyncio
    async def test_zero_games_win_rate(self, mock_user_data_zero_games):
        """Test win rate is 0 for user with no games."""
        with patch("utils.user.db") as mock_db:
            mock_db.get_user = AsyncMock(return_value=mock_user_data_zero_games)
            mock_db.get_user_position = AsyncMock(return_value=100)
            result = await get_full_stats(999999999)
            assert result["win_rate"] == 0.0

