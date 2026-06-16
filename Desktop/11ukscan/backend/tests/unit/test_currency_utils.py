"""
Unit tests for currency utility functions.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.utils.currency import format_amount, normalize_amount_string, parse_amount


class TestParseAmount:
    """Tests for parse_amount() — the primary currency string parser."""

    def test_simple_positive(self):
        assert parse_amount("£1,234.56") == Decimal("1234.56")

    def test_simple_negative(self):
        assert parse_amount("-£50.00") == Decimal("-50.00")

    def test_no_currency_symbol(self):
        assert parse_amount("1234.56") == Decimal("1234.56")

    def test_accounting_parentheses(self):
        assert parse_amount("(250.00)") == Decimal("-250.00")

    def test_zero(self):
        assert parse_amount("£0.00") == Decimal("0.00")

    def test_large_amount_with_comma(self):
        assert parse_amount("£10,000.00") == Decimal("10000.00")

    def test_empty_string_returns_none(self):
        assert parse_amount("") is None

    def test_non_numeric_returns_none(self):
        assert parse_amount("N/A") is None

    def test_whitespace_stripped(self):
        assert parse_amount("  £99.99  ") == Decimal("99.99")


class TestFormatAmount:
    """Tests for format_amount() display formatting."""

    def test_positive_format(self):
        assert format_amount(Decimal("1234.56")) == "£1,234.56"

    def test_negative_format(self):
        assert format_amount(Decimal("-50.00")) == "-£50.00"

    def test_zero_format(self):
        assert format_amount(Decimal("0.00")) == "£0.00"

    def test_custom_symbol(self):
        assert format_amount(Decimal("100.00"), symbol="$") == "$100.00"


class TestNormalizeAmountString:
    """Tests for normalize_amount_string() pre-processing."""

    def test_strips_pound_symbol(self):
        assert normalize_amount_string("£1,234.56") == "1234.56"

    def test_strips_commas(self):
        assert normalize_amount_string("1,234.56") == "1234.56"

    def test_preserves_negative_sign(self):
        assert normalize_amount_string("-£50.00") == "-50.00"

    def test_already_clean_string(self):
        assert normalize_amount_string("9.99") == "9.99"
