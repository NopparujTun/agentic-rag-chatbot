"""Centralized logging configuration for the backend application.

Provides a factory function that returns a named logger writing to both
the console (stdout) and a rotating log file.
"""

import logging
import os
import sys
from typing import Optional

LOG_DIRECTORY = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, "system.log")
LOG_MESSAGE_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(logger_name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger instance.

    On first call for a given name, the logger is set up with two handlers:
    1. Console — writes to `sys.stdout` at INFO level.
    2. File — appends to `logs/system.log` (UTF-8, auto-created).

    Subsequent calls with the same name return the same logger without
    adding duplicate handlers.

    Args:
        logger_name: The name for the logger. Typically `__name__` from the 
            calling module. Defaults to "EnterpriseKB".

    Returns:
        A configured logging.Logger instance ready to use.
    """
    logger = logging.getLogger(logger_name or "EnterpriseKB")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_formatter = logging.Formatter(LOG_MESSAGE_FORMAT, datefmt=LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    try:
        os.makedirs(LOG_DIRECTORY, exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not create log file at %s", LOG_FILE_PATH)

    return logger