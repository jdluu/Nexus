"""Logging configuration for Nexus.

Configures structlog to write asynchronous logs to a rotating file in the user's
cache directory, ensuring it does not interfere with the TUI.
"""

import logging

from pathlib import Path
from typing import Any

import structlog

# Define log path
LOG_DIR = Path.home() / ".cache" / "nexus"
LOG_FILE = LOG_DIR / "nexus.log"


def configure_logging() -> None:
    """Configures structural logging."""
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Configure standard logging to file
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format="%(message)s",
    )

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
    """Returns a structured logger instance."""
    return structlog.get_logger(name)
