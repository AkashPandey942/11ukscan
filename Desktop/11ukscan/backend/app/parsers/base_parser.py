"""
Abstract base class for all bank statement parsers.

This is the foundation of the Open/Closed Principle in BankScan.
The base class is CLOSED for modification — it defines the contract
that all parsers must fulfil. It is OPEN for extension — new banks
are supported by subclassing and overriding the abstract methods.

Usage:
    class HSBCParser(AbstractBankStatementParser):
        bank_name = "HSBC"
        fingerprints = ["HSBC Bank plc", "HSBC Statement"]

        def extract_header(self, pages): ...
        def extract_transactions(self, pages): ...

Never modify this file to accommodate a specific bank's quirks.
Put all bank-specific logic in the concrete parser class.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List

from app.models.statement import StatementInfo
from app.models.transaction import Transaction
from app.parsers.pdf_reader import PageText

logger = logging.getLogger(__name__)


class AbstractBankStatementParser(ABC):
    """
    Abstract base class that defines the parser contract for all banks.

    Subclasses MUST implement:
    - ``bank_name``          (class attribute) — unique bank identifier string
    - ``fingerprints``       (class attribute) — list of text patterns from page 1
                             that uniquely identify this bank's statement format
    - ``extract_header()``   — extract StatementInfo from page 1 text
    - ``extract_transactions()`` — extract all Transaction rows from all pages

    Subclasses MAY override:
    - ``validate()``         — additional document-level validation
    - ``can_parse()``        — fingerprint matching logic

    The ``parse()`` template method orchestrates the full parsing pipeline
    and should NOT be overridden in most cases.
    """

    # ------------------------------------------------------------------ #
    # Abstract class attributes — must be defined by every subclass
    # ------------------------------------------------------------------ #

    bank_name: str = ""
    """Unique human-readable identifier for this bank format, e.g. 'Monzo Business'."""

    fingerprints: List[str] = []
    """
    List of text strings that appear on page 1 of this bank's statements.
    Used by ``BankParserRegistry`` to auto-detect the correct parser.
    All fingerprints must match for ``can_parse()`` to return True.
    """

    # ------------------------------------------------------------------ #
    # Abstract methods — MUST be implemented by subclasses
    # ------------------------------------------------------------------ #

    @abstractmethod
    def extract_header(self, pages: List[PageText]) -> StatementInfo:
        """
        Extract account metadata from the statement header.

        This typically reads page 1 and uses regex patterns to find
        account holder name, period, sort code, account number, etc.

        Args:
            pages: All extracted page text objects from the PDF.

        Returns:
            A populated ``StatementInfo`` instance.

        Raises:
            HeaderExtractionError: If a required field cannot be found.
        """
        ...

    @abstractmethod
    def extract_transactions(self, pages: List[PageText]) -> tuple[List[Transaction], List[str]]:
        """
        Extract all transaction rows from every page of the statement.

        Args:
            pages: All extracted page text objects from the PDF.

        Returns:
            A tuple of:
            - List of ``Transaction`` objects in chronological order.
            - List of warning strings for rows that could not be parsed.

        Raises:
            TransactionExtractionError: If no transactions could be found.
        """
        ...

    # ------------------------------------------------------------------ #
    # Concrete methods — may be overridden but have sensible defaults
    # ------------------------------------------------------------------ #

    def can_parse(self, pages: List[PageText]) -> bool:
        """
        Check if this parser can handle the given PDF pages.

        Default implementation checks if ALL configured fingerprints
        appear anywhere in page 1 text (case-insensitive).

        Args:
            pages: All extracted page text objects from the PDF.

        Returns:
            True if this parser recognises the document format.
        """
        if not pages or not self.fingerprints:
            return False

        page_one_text = pages[0].text.lower()
        return all(fp.lower() in page_one_text for fp in self.fingerprints)

    def validate(self, pages: List[PageText]) -> None:
        """
        Perform document-level validation before parsing begins.

        Default implementation is a no-op. Override in subclasses
        to enforce bank-specific structural requirements.

        Args:
            pages: All extracted page text objects from the PDF.

        Raises:
            ParseError: If the document fails validation.
        """
        pass

    def parse(self, pages: List[PageText]) -> tuple[StatementInfo, List[Transaction], List[str]]:
        """
        Template method — orchestrates the full parsing pipeline.

        Calls: validate() → extract_header() → extract_transactions()

        This method should NOT be overridden in subclasses. Override
        the individual steps instead.

        Args:
            pages: All extracted page text objects from the PDF.

        Returns:
            A tuple of:
            - StatementInfo from the header
            - List of Transaction objects
            - List of warning strings

        Raises:
            ParseError: If any required extraction step fails.
        """
        logger.info(
            "Starting parse with %s parser (%d pages)",
            self.bank_name,
            len(pages),
        )

        self.validate(pages)

        header = self.extract_header(pages)
        logger.info("Header extracted: account=%s, period=%s to %s",
                    header.account_holder, header.period_start, header.period_end)

        transactions, warnings = self.extract_transactions(pages)
        logger.info(
            "Transactions extracted: count=%d, warnings=%d",
            len(transactions),
            len(warnings),
        )

        return header, transactions, warnings

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(bank_name={self.bank_name!r})"
