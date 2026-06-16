"""
Date parsing and validation utilities.

Handles the various date formats that appear in UK bank statement PDFs.
Falls back gracefully and logs warnings rather than crashing.

Supported formats (Monzo Business):
    "01 Jan 2024"   — transaction dates
    "1 January 2024" — statement period in header
    "01/01/2024"    — alternative formats
    "2024-01-01"    — ISO 8601
"""

from __future__ import annotations

import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Ordered list of date format strings to try (most specific first)
_DATE_FORMATS = [
    "%d %b %Y",       # 01 Jan 2024  — Monzo transaction dates
    "%d %B %Y",       # 01 January 2024  — Monzo header period dates
    "%d/%m/%Y",       # 01/01/2024
    "%Y-%m-%d",       # 2024-01-01  — ISO 8601
    "%-d %b %Y",      # 1 Jan 2024  (Linux/Mac only — kept as fallback)
    "%d-%b-%Y",       # 01-Jan-2024
]


def parse_date(raw: str) -> Optional[datetime.date]:
    """
    Attempt to parse a date string using multiple known formats.

    Tries each format in ``_DATE_FORMATS`` in order, returning the
    first successful parse. Returns None if no format matches —
    the caller should log a warning and skip or flag the row.

    Args:
        raw: Raw date string extracted from the PDF.

    Returns:
        A ``datetime.date`` object, or None if parsing fails.
    """
    if not raw:
        return None

    cleaned = raw.strip()

    for fmt in _DATE_FORMATS:
        try:
            return datetime.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    logger.warning("Could not parse date string: %r", cleaned)
    return None


def format_date_display(d: datetime.date) -> str:
    """
    Format a date for human-readable display in Excel summaries.

    Args:
        d: A datetime.date object.

    Returns:
        Formatted string, e.g. "01 Jan 2024".
    """
    return d.strftime("%d %b %Y")


def format_period(start: datetime.date, end: datetime.date) -> str:
    """
    Format a statement period range for display.

    Args:
        start: Period start date.
        end:   Period end date.

    Returns:
        Formatted string, e.g. "01 Jan 2024 – 31 Jan 2024".
    """
    return f"{format_date_display(start)} \u2013 {format_date_display(end)}"
