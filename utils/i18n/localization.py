import yaml
from pathlib import Path
from typing import Dict, Any

from db.database import Database

from utils.logging import logger

db = Database()

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

loaded_count = len(locales)
logger.info(f"Loaded {loaded_count} localizations.")
if loaded_count == 0:
    logger.warning("No localizations were loaded. Check the loc directory.")

user_lang_cache: Dict[int, str] = {}


def _get_value(lang: str, keys: list[str]) -> str:
    """Retrieve a nested value from locales with fallback to en_US.

    Args:
        lang (str): The language code.
        keys (list[str]): The list of keys representing the nested structure.

    Returns:
        str: The translated value or the key path if not found.
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
    """Translates a given key into the user's preferred language, retrieving the language from cache
    or database if necessary, with fallback to English.

    Args:
        user_id (int): The ID of the user.
        key (str): The translation key.

    Returns:
        str: The translated string.
    """
    if user_id not in user_lang_cache:
        try:
            user = await db.get_user(user_id)
            lang = user[30] if user and len(user) > 30 else 'en_US'
            user_lang_cache[user_id] = lang
        except Exception as e:
            logger.error(f"Error getting user lang for {user_id}: {e}")
            lang = 'en_US'
            user_lang_cache[user_id] = lang
    else:
        lang = user_lang_cache[user_id]

    if lang not in locales:
        lang = 'en_US'

    keys = key.split('.')
    return _get_value(lang, keys)


def update_user_lang_cache(user_id: int, lang: str):
    """Updates the in-memory cache with the new language preference for the specified user.

    Args:
        user_id (int): The ID of the user.
        lang (str): The new language code.
    """
    user_lang_cache[user_id] = lang


def get_translation(lang: str, key: str) -> str:
    """Retrieves the translation for a specific key in the given language, falling back to English if
    the language is not available.

    Args:
        lang (str): The language code.
        key (str): The translation key.

    Returns:
        str: The translated string.
    """
    if lang not in locales:
        lang = 'en_US'

    keys = key.split('.')
    return _get_value(lang, keys)


def get_loss_reasons(user_id: int) -> list[str]:
    """Get the list of loss reasons for the user's language.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list[str]: The list of loss reasons in the user's language.
    """
    lang = user_lang_cache.get(user_id, 'en_US')
    if lang not in locales:
        lang = 'en_US'
    return locales[lang]['messages']['loss_reasons']
