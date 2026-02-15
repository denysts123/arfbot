"""
Tests for core/config.py module.
"""
import pytest
from core.config import (
    USER_ID, USERNAME, COINS, TICKETS, CUPS, VICTORIES, DEFEATS,
    GAMES_PLAYED, SUCCESS, GHOST_SMALL_PACKS, GHOST_BIG_PACKS,
    VICTORY_COEFFICIENT, DEFEAT_COEFFICIENT,
    SMALL_PACK_COEFFICIENT, MEDIUM_PACK_COEFFICIENT, BIG_PACK_COEFFICIENT,
    GHOST_SMALL_PACKS_COEFFICIENT, GHOST_MEDIUM_PACKS_COEFFICIENT, GHOST_BIG_PACKS_COEFFICIENT,
    COINS_START_BALANCE, TICKETS_START_BALANCE,
    PENALTY_SUCCESS_REQUIREMENT, MATCH_COST_COINS, MATCH_COST_TICKETS
)


class TestUserFieldIndices:
    """Tests for user field index constants."""

    def test_user_id_is_first(self):
        """Test USER_ID is index 0."""
        assert USER_ID == 0

    def test_username_follows_user_id(self):
        """Test USERNAME is index 1."""
        assert USERNAME == 1

    def test_indices_are_unique(self):
        """Test all field indices are unique."""
        indices = [
            USER_ID, USERNAME, COINS, TICKETS, CUPS,
            VICTORIES, DEFEATS, GAMES_PLAYED, SUCCESS
        ]
        assert len(indices) == len(set(indices))

    def test_ghost_packs_range(self):
        """Test ghost packs indices are contiguous."""
        assert GHOST_BIG_PACKS == GHOST_SMALL_PACKS + 2


class TestGameConstants:
    """Tests for game balance constants."""

    def test_victory_coefficient_positive(self):
        """Test victory coefficient is positive."""
        assert VICTORY_COEFFICIENT > 0

    def test_defeat_coefficient_negative(self):
        """Test defeat coefficient is negative."""
        assert DEFEAT_COEFFICIENT < 0

    def test_pack_coefficients_increasing(self):
        """Test pack coefficients increase with pack size."""
        assert SMALL_PACK_COEFFICIENT < MEDIUM_PACK_COEFFICIENT < BIG_PACK_COEFFICIENT

    def test_ghost_coefficients_match_regular(self):
        """Test ghost pack coefficients match regular pack coefficients."""
        assert GHOST_SMALL_PACKS_COEFFICIENT == SMALL_PACK_COEFFICIENT
        assert GHOST_MEDIUM_PACKS_COEFFICIENT == MEDIUM_PACK_COEFFICIENT
        assert GHOST_BIG_PACKS_COEFFICIENT == BIG_PACK_COEFFICIENT


class TestStartingBalances:
    """Tests for starting balance constants."""

    def test_coins_start_positive(self):
        """Test starting coins is positive."""
        assert COINS_START_BALANCE > 0

    def test_tickets_start_positive(self):
        """Test starting tickets is positive."""
        assert TICKETS_START_BALANCE > 0


class TestGameRequirements:
    """Tests for game requirement constants."""

    def test_penalty_requires_success(self):
        """Test penalty has success requirement."""
        assert PENALTY_SUCCESS_REQUIREMENT > 0

    def test_match_costs_positive(self):
        """Test match costs are positive."""
        assert MATCH_COST_COINS > 0
        assert MATCH_COST_TICKETS > 0

    def test_match_cost_affordable_at_start(self):
        """Test match is affordable with starting balance."""
        assert COINS_START_BALANCE >= MATCH_COST_COINS
        assert TICKETS_START_BALANCE >= MATCH_COST_TICKETS

