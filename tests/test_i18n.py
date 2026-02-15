"""
Tests for core/i18n.py module.
"""
import pytest
from core.i18n import (
    _get_nested, _get_value, get_translation,
    update_user_lang_cache, get_available_locales,
    user_lang_cache, locales, DEFAULT_LANG
)


class TestGetNested:
    """Tests for _get_nested function."""

    def test_simple_key(self):
        """Test getting simple key from dict."""
        data = {"key": "value"}
        assert _get_nested(data, ["key"]) == "value"

    def test_nested_keys(self):
        """Test getting deeply nested value."""
        data = {"level1": {"level2": {"level3": "deep_value"}}}
        assert _get_nested(data, ["level1", "level2", "level3"]) == "deep_value"

    def test_missing_key(self):
        """Test returns None for missing key."""
        data = {"key": "value"}
        assert _get_nested(data, ["missing"]) is None

    def test_non_dict_intermediate(self):
        """Test returns None when intermediate value is not a dict."""
        data = {"key": "not_a_dict"}
        assert _get_nested(data, ["key", "subkey"]) is None

    def test_empty_keys(self):
        """Test returns data when no keys provided."""
        data = {"key": "value"}
        assert _get_nested(data, []) == data


class TestGetValue:
    """Tests for _get_value function."""

    def test_existing_translation(self):
        """Test getting existing translation."""
        result = _get_value("en_US", ["config", "loc_name"])
        assert result == "English (US)"

    def test_fallback_to_default(self):
        """Test fallback to DEFAULT_LANG when key not in specified lang."""
        result = _get_value("nonexistent_lang", ["config", "loc_name"])
        assert result == "English (US)"

    def test_returns_key_path_if_not_found(self):
        """Test returns key path if translation not found anywhere."""
        result = _get_value("en_US", ["nonexistent", "key", "path"])
        assert result == "nonexistent.key.path"


class TestGetTranslation:
    """Tests for get_translation function."""

    def test_valid_language_and_key(self):
        """Test getting translation for valid language and key."""
        result = get_translation("en_US", "config.loc_name")
        assert result == "English (US)"

    def test_invalid_language_fallback(self):
        """Test fallback to DEFAULT_LANG for invalid language."""
        result = get_translation("invalid_lang", "config.loc_name")
        assert result == "English (US)"


class TestUpdateUserLangCache:
    """Tests for update_user_lang_cache function."""

    def test_cache_updated(self):
        """Test that cache is updated correctly."""
        test_user_id = 999888777
        update_user_lang_cache(test_user_id, "uk_UA")
        assert user_lang_cache[test_user_id] == "uk_UA"
        del user_lang_cache[test_user_id]

    def test_cache_overwrites(self):
        """Test that cache overwrites existing value."""
        test_user_id = 999888776
        update_user_lang_cache(test_user_id, "en_US")
        update_user_lang_cache(test_user_id, "ru_RU")
        assert user_lang_cache[test_user_id] == "ru_RU"
        del user_lang_cache[test_user_id]


class TestGetAvailableLocales:
    """Tests for get_available_locales function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        assert isinstance(get_available_locales(), list)

    def test_contains_default_lang(self):
        """Test that list contains default language."""
        assert DEFAULT_LANG in get_available_locales()

    def test_not_empty(self):
        """Test that list is not empty."""
        assert len(get_available_locales()) > 0

    def test_matches_locales_keys(self):
        """Test that result matches locales dict keys."""
        assert set(get_available_locales()) == set(locales.keys())

