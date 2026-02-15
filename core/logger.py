"""
Logging module for the application.
Provides configured loguru logger with file rotation and archiving.
"""
from typing import Any
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import zipfile
from datetime import datetime, timedelta
from loguru import logger as _loguru_logger

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

LOGS_DIR = os.getenv("LOGS_DIR")
LOG_FILE_NAME = os.getenv("LOG_FILE_NAME")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

base_dir = Path(__file__).parent.parent
if not Path(LOGS_DIR).is_absolute():
    LOGS_DIR = (base_dir / LOGS_DIR).resolve()

LOGS_DIR_PATH = Path(LOGS_DIR)
ARCHIVE_DIR_PATH = LOGS_DIR_PATH / "archive"
LOGS_DIR_PATH.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOGS_DIR_PATH / LOG_FILE_NAME

_loguru_logger.remove()
_loguru_logger.level("DEBUG", color="<dim>")
_loguru_logger.level("INFO", color="<green>")
_loguru_logger.level("WARNING", color="<yellow>")
_loguru_logger.level("ERROR", color="<red>")
_loguru_logger.level("CRITICAL", color="<bold><white><red>")

_loguru_logger.add(
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
    """Archive the previous log file if it exists and has content."""
    if LOG_FILE_PATH.exists() and LOG_FILE_PATH.stat().st_size > 0:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{LOG_FILE_PATH.stem}_{ts}.zip"
        archive_path = ARCHIVE_DIR_PATH / archive_name
        try:
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.write(LOG_FILE_PATH, arcname=LOG_FILE_PATH.name)
            LOG_FILE_PATH.unlink()
        except Exception as e:
            _loguru_logger.opt(depth=1).error(f"Failed to archive previous log: {e}")


def _cleanup_old_archives():
    """Clean up old archived log files based on retention days."""
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

_loguru_logger.add(
    str(LOG_FILE_PATH),
    format="{time:YYYY-MM-DD HH:mm:ss} {level: <8} {module: <15}:{function: <25} │ {message}",
    colorize=False,
    level="DEBUG",
    enqueue=True,
)


class Logger:
    """Logger wrapper providing depth-adjusted logging methods."""

    def critical(self, message: Any):
        """Log a critical message."""
        _loguru_logger.opt(depth=1).critical(message)

    def error(self, message: Any):
        """Log an error message."""
        _loguru_logger.opt(depth=1).error(message)

    def warning(self, message: Any):
        """Log a warning message."""
        _loguru_logger.opt(depth=1).warning(message)

    def info(self, message: Any):
        """Log an info message."""
        _loguru_logger.opt(depth=1).info(message)

    def debug(self, message: Any):
        """Log a debug message."""
        _loguru_logger.opt(depth=1).debug(message)


logger = Logger()

