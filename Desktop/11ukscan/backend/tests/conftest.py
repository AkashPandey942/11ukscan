"""
Test fixtures and shared configuration for BankScan tests.

Provides reusable pytest fixtures for parsers, exporters, and mock data.
"""

from __future__ import annotations

import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import List

import pytest

from app.models.statement import ParsedStatement, StatementInfo
from app.models.transaction import Transaction
from app.parsers.pdf_reader import PageText


# ------------------------------------------------------------------ #
# Sample data fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def sample_statement_info() -> StatementInfo:
    """Return a populated StatementInfo for testing."""
    return StatementInfo(
        bank_name="Monzo Business",
        account_holder="Acme Ltd",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        account_number="12345678",
        sort_code="04-00-04",
        statement_type="Business Current Account",
    )


@pytest.fixture
def sample_transactions() -> List[Transaction]:
    """Return a list of sample Transaction objects for testing."""
    return [
        Transaction(
            date=date(2024, 1, 3),
            description="Amazon Prime",
            amount=Decimal("-9.99"),
            balance=Decimal("1090.01"),
        ),
        Transaction(
            date=date(2024, 1, 5),
            description="Client Payment - Invoice 001",
            amount=Decimal("2500.00"),
            balance=Decimal("3590.01"),
        ),
        Transaction(
            date=date(2024, 1, 8),
            description="Stripe Payout",
            amount=Decimal("750.00"),
            balance=Decimal("4340.01"),
        ),
        Transaction(
            date=date(2024, 1, 12),
            description="Office Supplies",
            amount=Decimal("-45.50"),
            balance=Decimal("4294.51"),
        ),
        Transaction(
            date=date(2024, 1, 15),
            description="AWS Invoice",
            amount=Decimal("-123.45"),
            balance=Decimal("4171.06"),
        ),
    ]


@pytest.fixture
def sample_parsed_statement(
    sample_statement_info: StatementInfo,
    sample_transactions: List[Transaction],
) -> ParsedStatement:
    """Return a complete ParsedStatement for testing exporters."""
    return ParsedStatement(
        info=sample_statement_info,
        transactions=sample_transactions,
        page_count=3,
        warnings=["Row 'N/A N/A' skipped — could not parse date"],
    )


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for export file output in tests."""
    output = tmp_path / "outputs"
    output.mkdir()
    return output


# ------------------------------------------------------------------ #
# Monzo PDF text fixtures
# ------------------------------------------------------------------ #

MONZO_PAGE_1_TEXT = """
Monzo Bank Ltd

Account name
Acme Ltd

Statement period
01 January 2024 to 31 January 2024

Account number
12345678

Sort code
04-00-04

Business Current Account

Date        Description                     Amount      Balance
03 Jan 2024 Amazon Prime                    -£9.99      £1,090.01
05 Jan 2024 Client Payment - Invoice 001    £2,500.00   £3,590.01
"""

MONZO_PAGE_2_TEXT = """
Date        Description                     Amount      Balance
08 Jan 2024 Stripe Payout                   £750.00     £4,340.01
12 Jan 2024 Office Supplies                 -£45.50     £4,294.51
15 Jan 2024 AWS Invoice                     -£123.45    £4,171.06
"""


@pytest.fixture
def monzo_pages() -> List[PageText]:
    """Return mock PageText objects simulating a Monzo Business statement."""
    return [
        PageText(page_number=1, text=MONZO_PAGE_1_TEXT, width=595.0, height=842.0),
        PageText(page_number=2, text=MONZO_PAGE_2_TEXT, width=595.0, height=842.0),
    ]
