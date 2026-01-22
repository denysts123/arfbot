import yaml
from pathlib import Path
from typing import Dict, Any

from utils import logger
from db.database import Database

db = Database()

LOC_DIR = Path(__file__).parent.parent / "loc"
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

# Cache for user languages to avoid repeated DB queries
user_lang_cache: Dict[int, str] = {}

def _get_value(lang: str, keys: list[str]) -> str:
    """Retrieve a nested value from locales with fallback to en_US."""
    value = locales.get(lang, locales.get('en_US', {}))
    try:
        for k in keys:
            value = value[k]
        return value
    except KeyError:
        logger.warning(f"Translation key '{'.'.join(keys)}' not found for lang '{lang}', falling back to en_US")
        try:
            value = locales['en_US']
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return '.'.join(keys)

async def tr(user_id: int, key: str) -> str:
    """Translate a key for the user's language, using cached language if available."""
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
    """Update the cached language for a user."""
    user_lang_cache[user_id] = lang

def get_translation(lang: str, key: str) -> str:
    """Get translation for a specific language."""
    if lang not in locales:
        lang = 'en_US'
    
    keys = key.split('.')
    return _get_value(lang, keys)
