from typing import Any
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import zipfile
from datetime import datetime, timedelta
from loguru import logger

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

LOGS_DIR = os.getenv("LOGS_DIR")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME")
RETENTION_DAYS_RAW = os.getenv("RETENTION_DAYS")

try:
    if RETENTION_DAYS_RAW is None:
        raise ValueError("RETENTION_DAYS environment variable is not set")
    RETENTION_DAYS = int(RETENTION_DAYS_RAW)
    if RETENTION_DAYS < 0:
        raise ValueError(f"RETENTION_DAYS must be non-negative, got {RETENTION_DAYS}")
except ValueError as e:
    logger.critical(f"Invalid RETENTION_DAYS: {e}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Unexpected error parsing RETENTION_DAYS: {e}")
    sys.exit(1)

base_dir = Path(__file__).parent.parent.parent
if not Path(LOGS_DIR).is_absolute():
    LOGS_DIR = (base_dir / LOGS_DIR).resolve()

LOGS_DIR_PATH = Path(LOGS_DIR)
ARCHIVE_DIR_PATH = LOGS_DIR_PATH / "archive"
LOGS_DIR_PATH.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOGS_DIR_PATH / LOG_FILE_NAME

logger.remove()
logger.level("DEBUG", color="<dim>")
logger.level("INFO", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<bold><white><red>")

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

logger.add(
    sys.stderr,
    format=(
        "<white>{time:YYYY-MM-DD HH:mm:ss}</white> "
        "<level>{level: <8}</level> "
        "<cyan>{module: <15}:{function: <25}</cyan> │ "
        "<level>{message}</level>"
    ),
    colorize=True,
    level=LOG_LEVEL,
)

def _archive_previous_log():
    """Archives the previous log file if it exists and has content."""
    if LOG_FILE_PATH.exists() and LOG_FILE_PATH.stat().st_size > 0:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = LOG_FILE_PATH.stem
        archive_name = f"{base_name}_{ts}.zip"
        archive_path = ARCHIVE_DIR_PATH / archive_name
        try:
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(LOG_FILE_PATH, arcname=LOG_FILE_PATH.name)
            LOG_FILE_PATH.unlink()
        except Exception as e:
            logger.opt(depth=1).error(f"Failed to archive previous log: {e}")

def _cleanup_old_archives():
    """Cleans up old archived log files based on retention days."""
    if RETENTION_DAYS == 0:
        return
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    try:
        with os.scandir(ARCHIVE_DIR_PATH) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(".zip"):
                    try:
                        mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                        if mtime < cutoff:
                            os.remove(entry.path)
                    except Exception:
                        pass
    except Exception:
        pass

_archive_previous_log()
_cleanup_old_archives()

LOG_FILE_PATH.touch()

logger.add(
    str(LOG_FILE_PATH),
    format="{time:YYYY-MM-DD HH:mm:ss} {level: <8} {module: <15}:{function: <25} │ {message}",
    colorize=False,
    level="DEBUG",
    enqueue=True,
)

def critical(message: Any):
    """Logs a critical message."""
    logger.opt(depth=1).critical(message)

def error(message: Any):
    """Logs an error message."""
    logger.opt(depth=1).error(message)

def warning(message: Any):
    """Logs a warning message."""
    logger.opt(depth=1).warning(message)

def info(message: Any):
    """Logs an info message."""
    logger.opt(depth=1).info(message)

def debug(message: Any):
    """Logs a debug message."""
    logger.opt(depth=1).debug(message)