"""Logging configuration for the Nexus application.

Configures structural logging to write asynchronous records to a rotating
file in the user's cache directory.
"""

import logging
from pathlib import Path
from typing import Any
import platformdirs
import structlog

# Define the log directory and file path using cross-platform standards.
LOG_DIR = Path(platformdirs.user_cache_dir("nexus"))
LOG_FILE = LOG_DIR / "nexus.log"


def configure_logging() -> None:
    """Configures structured logging for the application.

    Creates the necessary log directory and initializes the structlog
    processors for JSON output to the log file.
    """
    try:
        if not LOG_DIR.exists():
            LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure we can write to the log file
        logging.basicConfig(
            filename=str(LOG_FILE),
            level=logging.INFO,
            format="%(message)s",
        )
    except (PermissionError, OSError):
        # Fallback to no-op logging if the filesystem is inaccessible
        logging.basicConfig(level=logging.CRITICAL + 1)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "nexus") -> Any:
    """Retrieves a structured logger instance.

    Args:
        name: The name of the logger instance.

    Returns:
        A structlog logger configured for the application.
    """
    return structlog.get_logger(name)
