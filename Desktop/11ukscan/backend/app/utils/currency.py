"""
Currency normalisation utilities.

Handles parsing of UK-formatted monetary strings from PDF text into
Python Decimal values. The Decimal type is mandatory for all monetary
values — never use float for financial calculations.

Supported input formats:
    £1,234.56    →  Decimal('1234.56')
    -£1,234.56   →  Decimal('-1234.56')
    1,234.56     →  Decimal('1234.56')
    (1,234.56)   →  Decimal('-1234.56')   ← accounting notation
    1234.56      →  Decimal('1234.56')
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional


# Regex: optional leading minus or open-paren, optional £, digits/commas/dot
_CURRENCY_PATTERN = re.compile(
    r"(?P<neg_sign>-|\()?"       # Leading minus or opening paren for negatives
    r"£?"                         # Optional pound symbol
    r"(?P<digits>[\d,]+\.?\d*)"  # Numeric value with optional thousand separators
    r"\)?"                        # Optional closing paren (accounting notation)
)


def parse_amount(raw: str) -> Optional[Decimal]:
    """
    Parse a UK currency string from PDF text into a signed Decimal.

    Args:
        raw: Raw string extracted from the PDF, e.g. "£1,234.56" or "-£50.00".

    Returns:
        A Decimal representing the monetary value, or None if the input
        cannot be parsed (triggers a parser warning, not a crash).

    Examples:
        >>> parse_amount("£1,234.56")
        Decimal('1234.56')
        >>> parse_amount("-£50.00")
        Decimal('-50.00')
        >>> parse_amount("(250.00)")
        Decimal('-250.00')
    """
    if not raw:
        return None

    cleaned = raw.strip()
    match = _CURRENCY_PATTERN.search(cleaned)
    if not match:
        return None

    digits_str = match.group("digits").replace(",", "")
    neg_sign = match.group("neg_sign")

    try:
        value = Decimal(digits_str)
    except InvalidOperation:
        return None

    # Apply negative sign if present (either "-" prefix or "()" accounting)
    if neg_sign:
        value = -value

    return value


def format_amount(value: Decimal, symbol: str = "£") -> str:
    """
    Format a Decimal amount for display in reports or Excel summaries.

    Args:
        value:  Monetary Decimal value (may be negative).
        symbol: Currency symbol prefix. Defaults to "£".

    Returns:
        A formatted string like "£1,234.56" or "-£50.00".

    Examples:
        >>> format_amount(Decimal('1234.56'))
        '£1,234.56'
        >>> format_amount(Decimal('-50.00'))
        '-£50.00'
    """
    if value < 0:
        return f"-{symbol}{abs(value):,.2f}"
    return f"{symbol}{value:,.2f}"


def normalize_amount_string(raw: str) -> str:
    """
    Strip currency symbols and thousand separators from a raw string.

    Useful for pre-processing before Decimal conversion.

    Args:
        raw: Raw currency string.

    Returns:
        Cleaned numeric string with sign preserved.

    Examples:
        >>> normalize_amount_string("£1,234.56")
        '1234.56'
        >>> normalize_amount_string("-£1,234.56")
        '-1234.56'
    """
    cleaned = raw.strip().replace("£", "").replace(",", "")
    return cleaned
