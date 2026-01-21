from typing import Any
import sys
import os
from dotenv import load_dotenv
import zipfile
from datetime import datetime, timedelta
from loguru import logger

load_dotenv(dotenv_path="../.env")

LOGS_DIR = os.getenv("LOGS_DIR")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME")
RETENTION_DAYS_RAW = os.getenv("RETENTION_DAYS")

logger.remove()
logger.add(
    sys.stderr,
    format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> <level>{level: <8}</level> {message}",
    colorize=True,
    level="DEBUG",
)

missing = []
if not LOGS_DIR:
    missing.append("LOGS_DIR")
if not LOG_FILE_NAME:
    missing.append("LOG_FILE_NAME")
if not RETENTION_DAYS_RAW:
    missing.append("RETENTION_DAYS")

if missing:
    logger.critical(f"Missing required environment variables: {', '.join(missing)}")
    sys.exit(1)

try:
    RETENTION_DAYS = int(RETENTION_DAYS_RAW)
    if RETENTION_DAYS < 0:
        raise ValueError("negative")
except Exception:
    logger.critical("RETENTION_DAYS must be a non-negative integer")
    sys.exit(1)

base_dir = os.path.dirname(__file__)
if not os.path.isabs(LOGS_DIR):
    LOGS_DIR = os.path.abspath(os.path.join(base_dir, LOGS_DIR))

os.makedirs(LOGS_DIR, exist_ok=True)
ARCHIVE_DIR = os.path.join(LOGS_DIR, "archive")
os.makedirs(ARCHIVE_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, LOG_FILE_NAME)

logger.remove()
logger.level("DEBUG", color="<cyan>")
logger.level("INFO", color="<green>")
logger.level("WARNING", color="<yellow>")
logger.level("ERROR", color="<red>")
logger.level("CRITICAL", color="<bold><white><red>")

logger.add(
    sys.stderr,
    format=(
        "<white>{time:YYYY-MM-DD HH:mm:ss}</white> "
        "<level>{level: <8}</level> "
        "<cyan>{module}:{function: <20}</cyan> │ "
        "<level>{message}</level>"
    ),
    colorize=True,
    level="DEBUG",
)

def _archive_previous_log():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(LOG_FILE_NAME)[0]
        archive_name = f"{base_name}_{ts}.zip"
        archive_path = os.path.join(ARCHIVE_DIR, archive_name)
        try:
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(LOG_FILE, arcname=os.path.basename(LOG_FILE))
            os.remove(LOG_FILE)
        except Exception as e:
            logger.opt(depth=1).error(f"Failed to archive previous log: {e}")

def _cleanup_old_archives():
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    for fname in os.listdir(ARCHIVE_DIR):
        if not fname.lower().endswith(".zip"):
            continue
        path = os.path.join(ARCHIVE_DIR, fname)
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            if mtime < cutoff:
                os.remove(path)
        except Exception:
            pass

_archive_previous_log()
_cleanup_old_archives()

open(LOG_FILE, "a").close()

logger.add(
    LOG_FILE,
    format="{time:YYYY-MM-DD HH:mm:ss} {level: <8} {module}:{function: <20} │ {message}",
    colorize=False,
    level="DEBUG",
    enqueue=True,
)

def critical(message: Any, _exit: bool = True):
    logger.opt(depth=1).critical(message)
    if _exit:
        try:
            input("Press enter to exit...")
        except Exception:
            pass
        sys.exit(1)


def error(message: Any):
    logger.opt(depth=1).error(message)


def warning(message: Any):
    logger.opt(depth=1).warning(message)


def info(message: Any):
    logger.opt(depth=1).info(message)


def debug(message: Any):
    logger.opt(depth=1).debug(message)
