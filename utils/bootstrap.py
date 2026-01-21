"""
Pre-startup system validator
----------------------------------
This module performs essential system checks before the main application starts.
It verifies dependencies, environment variables, and database structure.
"""

import os
import sys
import sqlite3
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

PKGS = ["aiogram", "aiosqlite", "loguru", "colorama", "python-dotenv"]
VARS = ["BOT_TOKEN", "DB_PATH", "LOGS_DIR", "LOG_FILE_NAME", "RETENTION_DAYS"]

RED = '\033[31m'
YELLOW = '\033[33m'
RESET = '\033[0m'

def _load_dotenv_from(path):
    """Simple .env loader: reads key=value pairs and sets them in os.environ if not already set."""
    if not path or not path.exists():
        return
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip().upper(), v.strip().strip("'\""))
    except Exception:
        return

def read_dotenv():
    """Search and load .env file if it exists."""
    base_dir = Path(__file__).parent.parent
    parent_env = base_dir / ".env"
    cwd_env = Path.cwd() / ".env"
    if parent_env.exists():
        _load_dotenv_from(parent_env)
    elif cwd_env.exists():
        _load_dotenv_from(cwd_env)

def check_package(name):
    """Returns version string if package is installed, else None."""
    try:
        return version(name)
    except PackageNotFoundError:
        return None
    except Exception:
        return None

def check_packages(packages):
    """Checks for required packages, returns list of error messages."""
    return [f"Missing package: {p}" for p in packages if not check_package(p)]

def check_env_vars(vars_list):
    """Checks for required environment variables, returns list of error messages."""
    return [f"Missing variable: {v.upper()}" for v in vars_list if not os.environ.get(v.upper())]

def check_and_get_db_info(db_path):
    """Checks database and returns errors list and differences string."""
    if not db_path:
        return ["Database path not set"], "Database path not set"
    db_file = Path(db_path)
    if not db_file.exists():
        msg = f"Database file does not exist: {db_path}"
        return [msg], msg
    
    base_dir = Path(__file__).parent.parent
    init_sql_path = base_dir / "db" / "init.sql"
    if not init_sql_path.exists():
        msg = f"init.sql file not found: {init_sql_path}"
        return [msg], msg
    
    try:
        init_sql = init_sql_path.read_text(encoding='utf-8')
        
        with sqlite3.connect(":memory:") as conn_temp:
            conn_temp.executescript(init_sql)
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%'")
            expected_items = set(cursor_temp.fetchall())
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table', 'index') AND name NOT LIKE 'sqlite_%'")
            current_items = set(cursor.fetchall())
        
        missing = expected_items - current_items
        extra = current_items - expected_items
        errors = [f"Missing database items: {missing}"] if missing else []
        missing_tables = sorted([n for t, n in missing if t == 'table'])
        missing_indexes = sorted([n for t, n in missing if t == 'index'])
        extra_tables = sorted([n for t, n in extra if t == 'table'])
        extra_indexes = sorted([n for t, n in extra if t == 'index'])
        diff_parts = []
        if missing_tables:
            diff_parts.append(f"Missing Tables: {', '.join(missing_tables)}")
        if missing_indexes:
            diff_parts.append(f"Missing Indexes: {', '.join(missing_indexes)}")
        if extra_tables:
            diff_parts.append(f"Extra Tables: {', '.join(extra_tables)}")
        if extra_indexes:
            diff_parts.append(f"Extra Indexes: {', '.join(extra_indexes)}")
        diff_str = "\n".join(diff_parts) if diff_parts else "No differences"
        return errors, diff_str
    except sqlite3.Error as e:
        msg = f"Database error: {e}"
        return [msg], msg
    except Exception as e:
        msg = f"Error checking database structure: {e}"
        return [msg], msg

def check_database(db_path):
    """Checks if the SQLite database file exists, is accessible, and has the required tables and indexes as per init.sql, returns list of error messages."""
    errors, _ = check_and_get_db_info(db_path)
    return errors

def get_db_differences(db_path):
    """Returns a string describing differences between current DB and expected schema."""
    _, diff_str = check_and_get_db_info(db_path)
    return diff_str

def bootstrap():
    """Main bootstrap function to perform all checks."""
    read_dotenv()

    errors = []
    errors.extend(check_packages(PKGS))
    errors.extend(check_env_vars(VARS))
    db_path = os.environ.get("DB_PATH")
    errors.extend(check_database(db_path))

    if errors:
        error_msg = "Unable to start bot:\n" + "\n".join(errors)
        print(f"{RED}{error_msg}{RESET}")
        if db_path:
            diff_msg = get_db_differences(db_path)
            print(f"{YELLOW}DB differences: {diff_msg}{RESET}")
        sys.exit(1)
    elif db_path:
        diff_msg = get_db_differences(db_path)
        if diff_msg != "No differences":
            print(f"{YELLOW}Warning: DB does not match the schema, additional elements detected{RESET}")
            print(f"{YELLOW}{diff_msg}{RESET}")


bootstrap()