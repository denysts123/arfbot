"""
Tests for game/stats.py module.
"""
import pytest
from game.stats import calculate_success, calculate_win_rate
from core.config import (
    VICTORIES, DEFEATS, SMALL_PACKS, MEDIUM_PACKS, BIG_PACKS,
    GHOST_SMALL_PACKS, REFERRALS_COUNT,
    VICTORY_COEFFICIENT, DEFEAT_COEFFICIENT,
    SMALL_PACK_COEFFICIENT, MEDIUM_PACK_COEFFICIENT, BIG_PACK_COEFFICIENT,
    REFERRALS_COEFFICIENT
)


class TestCalculateWinRate:
    """Tests for calculate_win_rate function."""

    def test_normal_win_rate(self):
        """Test win rate calculation with normal values."""
        assert calculate_win_rate(15, 20) == 75.0

    def test_zero_games_played(self):
        """Test win rate returns 0.0 when no games played."""
        assert calculate_win_rate(0, 0) == 0.0

    def test_all_victories(self):
        """Test win rate when all games are victories."""
        assert calculate_win_rate(10, 10) == 100.0

    def test_no_victories(self):
        """Test win rate when no victories."""
        assert calculate_win_rate(0, 10) == 0.0

    def test_fractional_win_rate(self):
        """Test win rate with fractional result."""
        result = calculate_win_rate(1, 3)
        assert abs(result - 33.333333) < 0.001


class TestCalculateSuccess:
    """Tests for calculate_success function."""

    def test_success_with_victories(self, mock_user_data):
        """Test success calculation includes victories."""
        result = calculate_success(mock_user_data)
        victories_contribution = mock_user_data[VICTORIES] * VICTORY_COEFFICIENT
        assert result >= victories_contribution - abs(mock_user_data[DEFEATS] * DEFEAT_COEFFICIENT)

    def test_success_with_zero_stats(self, mock_user_data_zero_games):
        """Test success calculation with zero stats returns 0."""
        result = calculate_success(mock_user_data_zero_games)
        assert result == 0

    def test_success_subtracts_ghost_packs(self, mock_user_data):
        """Test that ghost packs are subtracted from success."""
        skill = mock_user_data[VICTORIES] * VICTORY_COEFFICIENT + mock_user_data[DEFEATS] * DEFEAT_COEFFICIENT
        resources = (
            mock_user_data[SMALL_PACKS] * SMALL_PACK_COEFFICIENT +
            mock_user_data[MEDIUM_PACKS] * MEDIUM_PACK_COEFFICIENT +
            mock_user_data[BIG_PACKS] * BIG_PACK_COEFFICIENT
        )
        bonus = mock_user_data[REFERRALS_COUNT] * REFERRALS_COEFFICIENT
        expected_without_ghost = skill + resources + bonus
        result = calculate_success(mock_user_data)
        assert result < expected_without_ghost

