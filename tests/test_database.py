"""
Tests for db/database.py module.
"""
import pytest
import tempfile
import os
from unittest.mock import patch, AsyncMock


class TestDatabaseMethods:
    """Tests for Database public methods with mocked _execute."""

    @pytest.mark.asyncio
    async def test_is_banned_true(self):
        """Test is_banned returns True for banned user."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=(1,))
            result = await db.is_banned(123)
            assert result is True

    @pytest.mark.asyncio
    async def test_is_banned_false(self):
        """Test is_banned returns False for non-banned user."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=(0,))
            result = await db.is_banned(123)
            assert result is False

    @pytest.mark.asyncio
    async def test_is_banned_nonexistent_user(self):
        """Test is_banned returns False for nonexistent user."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=None)
            result = await db.is_banned(999)
            assert result is False

    @pytest.mark.asyncio
    async def test_get_ban_date(self):
        """Test get_ban_date returns date string."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=("2026-12-31",))
            result = await db.get_ban_date(123)
            assert result == "2026-12-31"

    @pytest.mark.asyncio
    async def test_get_user_lang(self):
        """Test get_user_lang returns language code."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=("uk_UA",))
            result = await db.get_user_lang(123)
            assert result == "uk_UA"

    @pytest.mark.asyncio
    async def test_get_all_user_ids(self):
        """Test get_all_user_ids returns list of IDs."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=[(1,), (2,), (3,)])
            result = await db.get_all_user_ids()
            assert result == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_all_user_ids_empty(self):
        """Test get_all_user_ids returns empty list when no users."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=None)
            result = await db.get_all_user_ids()
            assert result == []

    @pytest.mark.asyncio
    async def test_get_user_position(self):
        """Test get_user_position returns position number."""
        with patch.dict(os.environ, {"DB_PATH": ":memory:"}):
            from importlib import reload
            import db.database as db_module
            reload(db_module)

            db = db_module.Database()
            db._execute = AsyncMock(return_value=(5,))
            result = await db.get_user_position(123)
            assert result == 5

