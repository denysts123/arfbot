"""
Tests for core/bootstrap.py module.
"""
import pytest
import os
import tempfile
import sqlite3
from pathlib import Path
from core.bootstrap import (
    check_package, check_packages, check_env_vars,
    get_schema_items, _load_dotenv_from
)


class TestCheckPackage:
    """Tests for check_package function."""

    def test_installed_package(self):
        """Test returns version for installed package."""
        result = check_package("pytest")
        assert result is not None
        assert isinstance(result, str)

    def test_not_installed_package(self):
        """Test returns None for not installed package."""
        result = check_package("definitely_not_a_real_package_12345")
        assert result is None


class TestCheckPackages:
    """Tests for check_packages function."""

    def test_all_installed(self):
        """Test returns empty list when all packages installed."""
        assert check_packages(["pytest"]) == []

    def test_missing_packages(self):
        """Test returns error messages for missing packages."""
        result = check_packages(["fake_package_xyz"])
        assert len(result) == 1
        assert "fake_package_xyz" in result[0]

    def test_mixed_packages(self):
        """Test handles mix of installed and missing packages."""
        result = check_packages(["pytest", "fake_package_abc"])
        assert len(result) == 1
        assert "fake_package_abc" in result[0]


class TestCheckEnvVars:
    """Tests for check_env_vars function."""

    def test_all_vars_set(self):
        """Test returns empty list when all vars set."""
        os.environ["TEST_VAR_123"] = "value"
        result = check_env_vars(["TEST_VAR_123"])
        assert result == []
        del os.environ["TEST_VAR_123"]

    def test_missing_vars(self):
        """Test returns error messages for missing vars."""
        result = check_env_vars(["DEFINITELY_NOT_SET_VAR_XYZ"])
        assert len(result) == 1
        assert "DEFINITELY_NOT_SET_VAR_XYZ" in result[0]


class TestGetSchemaItems:
    """Tests for get_schema_items function."""

    def test_creates_schema_from_sql(self):
        """Test creates schema from SQL script."""
        init_sql = """
        CREATE TABLE TestTable (id INTEGER PRIMARY KEY, name TEXT);
        CREATE INDEX idx_test ON TestTable(name);
        """
        result = get_schema_items(":memory:", init_sql)
        assert ("table", "TestTable") in result
        assert ("index", "idx_test") in result

    def test_reads_existing_db(self):
        """Test reads schema from existing database."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE ExistingTable (id INTEGER)")
            conn.commit()
            conn.close()

            result = get_schema_items(db_path)
            assert ("table", "ExistingTable") in result
        finally:
            os.unlink(db_path)


class TestLoadDotenvFrom:
    """Tests for _load_dotenv_from function."""

    def test_loads_simple_vars(self):
        """Test loads simple key=value pairs."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("TEST_DOTENV_VAR=test_value\n")
            env_path = Path(f.name)

        try:
            if "TEST_DOTENV_VAR" in os.environ:
                del os.environ["TEST_DOTENV_VAR"]
            _load_dotenv_from(env_path)
            assert os.environ.get("TEST_DOTENV_VAR") == "test_value"
        finally:
            os.unlink(env_path)
            if "TEST_DOTENV_VAR" in os.environ:
                del os.environ["TEST_DOTENV_VAR"]

    def test_handles_nonexistent_file(self):
        """Test handles nonexistent file gracefully."""
        _load_dotenv_from(Path("/nonexistent/path/.env"))

    def test_strips_quotes(self):
        """Test strips quotes from values."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write('QUOTED_VAR="quoted_value"\n')
            env_path = Path(f.name)

        try:
            if "QUOTED_VAR" in os.environ:
                del os.environ["QUOTED_VAR"]
            _load_dotenv_from(env_path)
            assert os.environ.get("QUOTED_VAR") == "quoted_value"
        finally:
            os.unlink(env_path)
            if "QUOTED_VAR" in os.environ:
                del os.environ["QUOTED_VAR"]

