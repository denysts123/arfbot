"""
Localization module.
Dynamically loads all localizations from loc/ folder.
Falls back to en_US if translation not found.
"""
import yaml
from pathlib import Path
from typing import Any

from utils.logging import logger

DEFAULT_LANG = "en_US"
LOC_DIR = Path(__file__).parent.parent.parent / "loc"
locales: dict[str, dict[str, Any]] = {}
user_lang_cache: dict[int, str] = {}


def _load_locales() -> None:
    """Load all .yaml files from localization folder into locales dict."""
    for loc_file in LOC_DIR.glob("*.yaml"):
        lang_code = loc_file.stem
        try:
            with open(loc_file, encoding="utf-8") as f:
                locales[lang_code] = yaml.safe_load(f) or {}
            logger.debug(f"Loaded localization: {lang_code}")
        except Exception as e:
            logger.error(f"Failed to load {lang_code}: {e}")
    logger.info(f"Loaded {len(locales)} localizations: {list(locales.keys())}")


_load_locales()


def _get_nested(data: dict[str, Any], keys: list[str]) -> Any:
    """Retrieve nested value from dict by key path."""
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)  # type: ignore[assignment]
    return data


def _get_value(lang: str, keys: list[str]) -> str:
    """
    Get translation by keys with fallback to DEFAULT_LANG.
    Returns key path if translation not found anywhere.
    """
    for try_lang in (lang, DEFAULT_LANG):
        if try_lang not in locales:
            continue
        value = _get_nested(locales[try_lang], keys)
        if value is not None:
            return str(value)
    
    key_path = ".".join(keys)
    logger.warning(f"Translation '{key_path}' not found for '{lang}'")
    return key_path


async def get_user_lang(user_id: int) -> str:
    """
    Get user language from cache or database.
    Returns DEFAULT_LANG if not found or unsupported.
    """
    if user_id in user_lang_cache:
        return user_lang_cache[user_id]
    
    from db.database import Database
    db = Database()
    lang = await db.get_user_lang(user_id)
    
    if not lang or lang not in locales:
        lang = DEFAULT_LANG
    
    user_lang_cache[user_id] = lang
    return lang


async def tr(user_id: int, key: str) -> str:
    """Translate key for user based on their language preference."""
    lang = await get_user_lang(user_id)
    return _get_value(lang, key.split("."))


def get_translation(lang: str, key: str) -> str:
    """Get translation for specified language and key."""
    if lang not in locales:
        lang = DEFAULT_LANG
    return _get_value(lang, key.split("."))


def update_user_lang_cache(user_id: int, lang: str) -> None:
    """Update language cache for user."""
    user_lang_cache[user_id] = lang


def get_available_locales() -> list[str]:
    """Return list of all available localizations."""
    return list(locales.keys())


async def get_loss_reasons(user_id: int) -> list[str]:
    """Get list of loss reasons in user's language."""
    lang = await get_user_lang(user_id)
    reasons = _get_nested(locales.get(lang, {}), ["messages", "loss_reasons"])
    return reasons if isinstance(reasons, list) else []

