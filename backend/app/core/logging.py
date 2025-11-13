from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .settings import settings


def setup_logging() -> None:
    """Configure root logger with console + optional rotating file handler."""
    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    storage_logs = settings.DATA_STORAGE_PATH / "logs"
    storage_logs.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        storage_logs / "backend.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


__all__ = ["setup_logging"]
