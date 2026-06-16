"""
Unit tests for MonzoBusinessParser.

Tests header extraction, transaction extraction, fingerprint detection,
multi-line description handling, and graceful error handling.
"""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import date

from app.parsers.monzo_parser import MonzoBusinessParser
from app.parsers.pdf_reader import PageText
from app.core.exceptions import HeaderExtractionError, TransactionExtractionError
from tests.conftest import MONZO_PAGE_1_TEXT, MONZO_PAGE_2_TEXT


class TestMonzoParserFingerprint:
    """Tests for bank format auto-detection (fingerprint matching)."""

    def test_can_parse_valid_monzo_page(self, monzo_pages):
        parser = MonzoBusinessParser()
        assert parser.can_parse(monzo_pages) is True

    def test_cannot_parse_empty_pages(self):
        parser = MonzoBusinessParser()
        assert parser.can_parse([]) is False

    def test_cannot_parse_non_monzo_page(self):
        parser = MonzoBusinessParser()
        pages = [PageText(page_number=1, text="HSBC Bank Statement\nSome other content")]
        assert parser.can_parse(pages) is False

    def test_cannot_parse_page_missing_business_account(self):
        parser = MonzoBusinessParser()
        pages = [PageText(page_number=1, text="Monzo Statement")]
        assert parser.can_parse(pages) is False


class TestMonzoHeaderExtraction:
    """Tests for page 1 header field extraction."""

    @pytest.fixture(autouse=True)
    def setup(self, monzo_pages):
        self.parser = MonzoBusinessParser()
        self.info = self.parser.extract_header(monzo_pages)

    def test_account_holder_extracted(self):
        assert self.info.account_holder == "Acme Ltd"

    def test_bank_name_set(self):
        assert self.info.bank_name == "Monzo Business"

    def test_period_start_extracted(self):
        assert self.info.period_start == date(2024, 1, 1)

    def test_period_end_extracted(self):
        assert self.info.period_end == date(2024, 1, 31)

    def test_account_number_extracted(self):
        assert self.info.account_number == "12345678"

    def test_sort_code_extracted(self):
        assert self.info.sort_code == "04-00-04"

    def test_statement_type_extracted(self):
        assert "Business Current Account" in self.info.statement_type


class TestMonzoTransactionExtraction:
    """Tests for transaction row parsing across multiple pages."""

    @pytest.fixture(autouse=True)
    def setup(self, monzo_pages):
        self.parser = MonzoBusinessParser()
        self.transactions, self.warnings = self.parser.extract_transactions(monzo_pages)

    def test_correct_number_of_transactions(self):
        assert len(self.transactions) == 5

    def test_first_transaction_date(self):
        assert self.transactions[0].date == date(2024, 1, 3)

    def test_first_transaction_description(self):
        assert "Amazon Prime" in self.transactions[0].description

    def test_first_transaction_amount_is_debit(self):
        assert self.transactions[0].amount == Decimal("-9.99")
        assert self.transactions[0].is_debit is True

    def test_second_transaction_is_credit(self):
        assert self.transactions[1].amount == Decimal("2500.00")
        assert self.transactions[1].is_credit is True

    def test_balance_tracked_correctly(self):
        assert self.transactions[0].balance == Decimal("1090.01")

    def test_page_2_transactions_extracted(self):
        # Transactions from page 2 should be present
        descriptions = [t.description for t in self.transactions]
        assert any("Stripe Payout" in d for d in descriptions)
        assert any("AWS Invoice" in d for d in descriptions)

    def test_no_warnings_for_clean_data(self):
        # Clean fixture data should produce no warnings
        assert len(self.warnings) == 0


class TestMonzoParserFullPipeline:
    """Integration tests for the full parse() template method."""

    def test_parse_returns_complete_result(self, monzo_pages):
        parser = MonzoBusinessParser()
        info, transactions, warnings = parser.parse(monzo_pages)

        assert info is not None
        assert len(transactions) == 5
        assert isinstance(warnings, list)

    def test_raises_on_empty_pages(self):
        parser = MonzoBusinessParser()
        with pytest.raises(HeaderExtractionError):
            parser.extract_header([])

    def test_raises_transaction_error_on_no_transactions(self):
        parser = MonzoBusinessParser()
        pages = [PageText(page_number=1, text=MONZO_PAGE_1_TEXT.split("Date")[0])]
        with pytest.raises(TransactionExtractionError):
            parser.extract_transactions(pages)
