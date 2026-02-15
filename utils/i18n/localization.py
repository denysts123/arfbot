"""
Localization module.
Provides translation functions with English as default (localization temporarily frozen).
"""
import yaml
from pathlib import Path
from typing import Dict, Any

from utils.logging import logger

LOC_DIR = Path(__file__).parent.parent.parent / "loc"
locales: Dict[str, Dict[str, Any]] = {}

for loc_file in LOC_DIR.glob("*.yaml"):
    lang_code = loc_file.stem
    try:
        with open(loc_file, encoding='utf-8') as f:
            locales[lang_code] = yaml.safe_load(f)
        logger.debug(f"Loaded localization for {lang_code}")
    except Exception as e:
        logger.error(f"Failed to load localization for {lang_code}: {e}")

logger.info(f"Loaded {len(locales)} localizations")


def _get_value(lang: str, keys: list[str]) -> str:
    """
    Retrieve a nested value from locales with fallback to en_US.
    Returns the key path if translation not found.
    """
    for l in [lang, 'en_US']:
        value = locales.get(l, {})
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            continue
    logger.warning(f"Translation key '{'.'.join(keys)}' not found for lang '{lang}'")
    return '.'.join(keys)


async def tr(user_id: int, key: str) -> str:
    """
    Translate a key for the given user.
    Currently frozen to English (en_US).
    """
    lang = 'en_US'
    keys = key.split('.')
    return _get_value(lang, keys)


def get_translation(lang: str, key: str) -> str:
    """
    Get translation for a specific language and key.
    Falls back to en_US if language not available.
    """
    if lang not in locales:
        lang = 'en_US'
    keys = key.split('.')
    return _get_value(lang, keys)


def get_loss_reasons(user_id: int) -> list[str]:
    """
    Get the list of loss reasons.
    Currently frozen to English (en_US).
    """
    return locales.get('en_US', {}).get('messages', {}).get('loss_reasons', [])
