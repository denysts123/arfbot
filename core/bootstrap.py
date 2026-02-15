"""
Pre-startup system validator.
Performs essential system checks before the main application starts.
Verifies dependencies, environment variables, and database structure.
"""
import asyncio
import os
import sys
import sqlite3
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PKGS = ["aiogram", "aiosqlite", "loguru", "python-dotenv", "pyyaml"]
VARS = ["BOT_TOKEN", "DB_PATH", "LOGS_DIR", "LOG_FILE_NAME", "RETENTION_DAYS", "ADMIN_IDS", "LOG_LEVEL"]

RED = '\033[31m'
YELLOW = '\033[33m'
RESET = '\033[0m'

cached_schema_hash = None


def _load_dotenv_from(path: Path):
    """Read key=value pairs from .env file and set them in os.environ if not already set."""
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip().upper(), v.strip().strip("'\""))
    except Exception:
        pass


def read_dotenv():
    """Search and load .env file if it exists."""
    base_dir = Path(__file__).parent.parent
    for env_path in [base_dir / ".env", Path.cwd() / ".env"]:
        if env_path.exists():
            _load_dotenv_from(env_path)
            break


def check_package(name):
    """Return version string if package is installed, else None."""
    try:
        return version(name)
    except (PackageNotFoundError, Exception):
        return None


def check_packages(packages):
    """Check for required packages, return list of error messages."""
    return [f"Missing package: {p}" for p in packages if not check_package(p)]


def check_env_vars(vars_list):
    """Check for required environment variables, return list of error messages."""
    return [f"Missing variable: {v.upper()}" for v in vars_list if not os.environ.get(v.upper())]


def get_schema_items(db_path, init_sql=None):
    """Return set of (type, name) tuples for tables and indexes."""
    conn = sqlite3.connect(":memory:" if init_sql else db_path)
    if init_sql:
        conn.executescript(init_sql)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%'"
        )
        return set(cursor.fetchall())
    finally:
        conn.close()


def check_and_get_db_info(db_path):
    """Check database and return errors list and differences string."""
    global cached_schema_hash
    if not db_path:
        return ["Database path not set"], "Database path not set"
    
    db_file = Path(db_path)
    if not db_file.exists():
        msg = f"Database file does not exist: {db_path}"
        return [msg], msg
    
    init_sql_path = Path(__file__).parent.parent / "db" / "init.sql"
    if not init_sql_path.exists():
        msg = f"init.sql file not found: {init_sql_path}"
        return [msg], msg
    
    try:
        init_sql = init_sql_path.read_text(encoding='utf-8')
        expected_items = get_schema_items(":memory:", init_sql)
        current_items = get_schema_items(db_path)
        
        hash_current = hash(str(sorted(current_items)))
        if cached_schema_hash is not None and cached_schema_hash == hash_current:
            return [], "No differences"
        cached_schema_hash = hash_current
        
        missing = expected_items - current_items
        extra = current_items - expected_items
        
        missing_tables = sorted([n for t, n in missing if t == 'table'])
        missing_indexes = sorted([n for t, n in missing if t == 'index'])
        extra_tables = sorted([n for t, n in extra if t == 'table'])
        extra_indexes = sorted([n for t, n in extra if t == 'index'])
        
        errors = []
        if missing_tables:
            errors.append(f"Missing Tables: {', '.join(missing_tables)}")
        if missing_indexes:
            errors.append(f"Missing Indexes: {', '.join(missing_indexes)}")
        
        diff_parts = []
        for label, items in [
            ("Missing Tables", missing_tables),
            ("Missing Indexes", missing_indexes),
            ("Extra Tables", extra_tables),
            ("Extra Indexes", extra_indexes)
        ]:
            if items:
                diff_parts.append(f"{label}: {', '.join(items)}")
        
        return errors, "\n".join(diff_parts) if diff_parts else "No differences"
    except sqlite3.Error as e:
        msg = f"Database error: {e}"
        return [msg], msg
    except Exception as e:
        msg = f"Error checking database structure: {e}"
        return [msg], msg


def check_database(db_path):
    """Check if database exists and has required schema."""
    errors, _ = check_and_get_db_info(db_path)
    return errors


def get_db_differences(db_path):
    """Return string describing differences between current DB and expected schema."""
    _, diff_str = check_and_get_db_info(db_path)
    return diff_str


async def bootstrap():
    """Main bootstrap function to perform all checks asynchronously."""
    read_dotenv()

    db_path = os.environ.get("DB_PATH")
    errors_lists = await asyncio.gather(
        asyncio.to_thread(check_packages, PKGS),
        asyncio.to_thread(check_env_vars, VARS),
        asyncio.to_thread(check_database, db_path)
    )
    errors = [error for sublist in errors_lists for error in sublist]

    if errors:
        error_msg = "Unable to start bot:\n" + "\n".join(errors)
        print(f"{RED}{error_msg}{RESET}")
        sys.exit(1)
    elif db_path:
        diff_msg = await asyncio.to_thread(get_db_differences, db_path)
        if diff_msg != "No differences":
            print(f"{YELLOW}Warning: DB does not match the schema, additional elements detected{RESET}")
            print(f"{YELLOW}{diff_msg}{RESET}")

