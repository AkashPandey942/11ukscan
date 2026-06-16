"""
Logging configuration for BankScan.

Provides structured JSON logging in production and human-readable
coloured output in development (DEBUG mode).

Usage:
    Call ``configure_logging()`` once inside the FastAPI lifespan handler.
    Then use ``logging.getLogger(__name__)`` in every module.

Design notes:
- In production (DEBUG=False), every log record is serialised as a
  single-line JSON object with a consistent schema — ideal for log
  aggregation platforms (Datadog, AWS CloudWatch, GCP Logging).
- In development (DEBUG=True), records are printed in a readable format
  with colour-coded severity levels.
- A ``request_id`` field is injected via a logging filter when running
  inside a FastAPI request context (see middleware.py).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class _JSONFormatter(logging.Formatter):
    """
    Custom log formatter that serialises records as single-line JSON.

    Every record includes:
    - timestamp  (ISO-8601, UTC)
    - level      (DEBUG / INFO / WARNING / ERROR / CRITICAL)
    - logger     (dotted module path)
    - message    (formatted log message)
    - request_id (injected by middleware when available)
    - exc_info   (exception traceback string, if applicable)
    """

    def format(self, record: logging.LogRecord) -> str:
        log_object: Dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Inject request ID if present (set by RequestIDMiddleware)
        request_id: Optional[str] = getattr(record, "request_id", None)
        if request_id:
            log_object["request_id"] = request_id

        # Serialise exception info when present
        if record.exc_info:
            log_object["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_object["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_object, ensure_ascii=False)


class _DevFormatter(logging.Formatter):
    """
    Human-readable formatter for development environments.

    Example output:
        2024-01-15 10:23:45 | INFO     | app.services.statement_service | Processing job abc-123
    """

    LEVEL_COLOURS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.LEVEL_COLOURS.get(record.levelname, "")
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        level = f"{colour}{record.levelname:<8}{self.RESET}"
        base = f"{timestamp} | {level} | {record.name} | {record.getMessage()}"
        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"
        return base


def configure_logging(log_level: str = "INFO", debug: bool = False) -> None:
    """
    Configure application-wide logging.

    Must be called once during application startup (lifespan handler).
    After this call, all modules should obtain loggers via
    ``logging.getLogger(__name__)`` — they will automatically use
    the configured handlers and formatters.

    Args:
        log_level: Python logging level string (DEBUG, INFO, WARNING, …).
        debug:     When True, uses human-readable development formatter.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Remove any pre-existing handlers to avoid duplicate log output
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level, logging.INFO))

    if debug:
        handler.setFormatter(_DevFormatter())
    else:
        handler.setFormatter(_JSONFormatter())

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers at WARNING level
    for noisy in ("uvicorn.access", "multipart", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("bankscan").info(
        "Logging configured",
        extra={"log_level": log_level, "debug_mode": debug},
    )
