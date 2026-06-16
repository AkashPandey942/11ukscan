"""
Monzo Business Bank Statement Parser.

Implements ``AbstractBankStatementParser`` for Monzo Business current
account statements (PDF format as of 2023–2025).
"""

from __future__ import annotations

import datetime
import logging
import re
from decimal import Decimal
from typing import List, Optional, Tuple

from app.core.exceptions import HeaderExtractionError, TransactionExtractionError
from app.models.statement import StatementInfo
from app.models.transaction import Transaction
from app.parsers.base_parser import AbstractBankStatementParser
from app.parsers.parser_registry import BankParserRegistry
from app.parsers.pdf_reader import PageText
from app.utils.currency import parse_amount
from app.utils.date_utils import parse_date

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Compiled regex patterns — compiled once at class load time
# ------------------------------------------------------------------ #

# Transaction date anchor: "01 Jan 2024" at start of line
_RE_TRANSACTION_DATE = re.compile(
    r"^(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
    re.MULTILINE,
)

# Header: Account holder name after "Account name" label
_RE_ACCOUNT_HOLDER = re.compile(
    r"Account\s+name[\s\n:]+([^\n]+)",
    re.IGNORECASE,
)

# Header: Statement period "DD Month YYYY to DD Month YYYY"
_RE_PERIOD = re.compile(
    r"(\d{1,2}\s+[A-Za-z]+\s+\d{4})\s+to\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
    re.IGNORECASE,
)

# Header: Account number (8 digits)
_RE_ACCOUNT_NUMBER = re.compile(
    r"Account\s+number[\s\n:]+(\d{8})",
    re.IGNORECASE,
)

# Header: Sort code XX-XX-XX
_RE_SORT_CODE = re.compile(
    r"Sort\s+code[\s\n:]+(\d{2}-\d{2}-\d{2})",
    re.IGNORECASE,
)

# Header: Statement type (Business Current Account, etc.)
_RE_STATEMENT_TYPE = re.compile(
    r"(Business\s+Current\s+Account|Personal\s+Current\s+Account|Business\s+Account)",
    re.IGNORECASE,
)

# Transaction amount: optional minus, optional £, digits with optional
# thousands separator and decimal. Captures the full amount string.
_RE_AMOUNT = re.compile(
    r"(-?£?[\d,]+\.\d{2})",
)


@BankParserRegistry.register
class MonzoBusinessParser(AbstractBankStatementParser):
    """
    Parser for Monzo Business Current Account PDF statements.

    Fingerprint strategy: Page 1 must contain both "Monzo" and
    "Business Current Account" (case-insensitive). This uniquely
    identifies Monzo Business statements without false positives.

    Extraction strategy:
    1. Header: Named-capture regex on page 1 full text.
    2. Transactions: Line-by-line scan with date-anchor detection.
       Continuation lines (no date at start) are appended to the
       previous transaction's description.
    """

    bank_name: str = "Monzo Business"
    fingerprints: List[str] = ["Monzo", "Business Current Account"]

    # ------------------------------------------------------------------ #
    # Header extraction
    # ------------------------------------------------------------------ #

    def extract_header(self, pages: List[PageText]) -> StatementInfo:
        """
        Extract account metadata from page 1 of a Monzo Business statement.

        Args:
            pages: All extracted page text objects.

        Returns:
            Populated StatementInfo instance.

        Raises:
            HeaderExtractionError: If account holder or period cannot be found.
        """
        if not pages:
            raise HeaderExtractionError("page content")

        # Use first two pages for header extraction in case content wraps
        header_text = "\n".join(p.text for p in pages[:2])

        account_holder = self._extract_account_holder(header_text)
        period_start, period_end = self._extract_period(header_text)
        account_number = self._extract_account_number(header_text)
        sort_code = self._extract_sort_code(header_text)
        statement_type = self._extract_statement_type(header_text)

        return StatementInfo(
            bank_name=self.bank_name,
            account_holder=account_holder,
            period_start=period_start,
            period_end=period_end,
            account_number=account_number,
            sort_code=sort_code,
            statement_type=statement_type,
        )

    def _extract_account_holder(self, text: str) -> str:
        """Extract account holder name from header text."""
        match = _RE_ACCOUNT_HOLDER.search(text)
        if match:
            return match.group(1).strip()
        # Fallback: try looking for a name-like pattern after "Name:"
        fallback = re.search(r"Name[\s:]+([A-Z][a-zA-Z\s&'.-]{2,60})", text)
        if fallback:
            return fallback.group(1).strip()
        raise HeaderExtractionError("account_holder")

    def _extract_period(self, text: str) -> Tuple[datetime.date, datetime.date]:
        """Extract statement period start and end dates."""
        match = _RE_PERIOD.search(text)
        if not match:
            raise HeaderExtractionError("statement_period")

        start = parse_date(match.group(1))
        end = parse_date(match.group(2))

        if start is None:
            raise HeaderExtractionError("period_start_date")
        if end is None:
            raise HeaderExtractionError("period_end_date")

        return start, end

    def _extract_account_number(self, text: str) -> str:
        """Extract 8-digit account number from header text."""
        match = _RE_ACCOUNT_NUMBER.search(text)
        if match:
            return match.group(1).strip()
        logger.warning("Account number not found in header — using empty string")
        return ""

    def _extract_sort_code(self, text: str) -> str:
        """Extract sort code (XX-XX-XX) from header text."""
        match = _RE_SORT_CODE.search(text)
        if match:
            return match.group(1).strip()
        logger.warning("Sort code not found in header — using empty string")
        return ""

    def _extract_statement_type(self, text: str) -> str:
        """Extract statement type description from header text."""
        match = _RE_STATEMENT_TYPE.search(text)
        if match:
            return match.group(1).strip()
        return "Business Current Account"

    # ------------------------------------------------------------------ #
    # Transaction extraction
    # ------------------------------------------------------------------ #

    def extract_transactions(
        self, pages: List[PageText]
    ) -> Tuple[List[Transaction], List[str]]:
        """
        Extract all transactions from all pages.

        Algorithm:
        1. Iterate every page line-by-line.
        2. A line starting with a date pattern begins a new transaction row.
        3. Lines without a date prefix are accumulated as description
           continuation (Monzo sometimes wraps merchant names).
        4. When a new date is found, parse the pending row first.
        5. Parse amount and balance from right side of the line.

        Args:
            pages: All extracted page text objects.

        Returns:
            Tuple of (transactions list, warnings list).

        Raises:
            TransactionExtractionError: If zero transactions are extracted.
        """
        transactions: List[Transaction] = []
        warnings: List[str] = []

        # Pending row accumulator
        pending_date_str: Optional[str] = None
        pending_desc_parts: List[str] = []
        pending_amounts: List[str] = []

        def flush_pending() -> None:
            """Parse and commit the current pending transaction."""
            nonlocal pending_date_str, pending_desc_parts, pending_amounts

            if pending_date_str is None:
                return

            tx = self._parse_transaction_row(
                date_str=pending_date_str,
                description=" ".join(pending_desc_parts),
                amounts=pending_amounts,
                warnings=warnings,
            )
            if tx is not None:
                transactions.append(tx)

            pending_date_str = None
            pending_desc_parts = []
            pending_amounts = []

        for page in pages:
            for raw_line in page.lines:
                line = raw_line.strip()
                if not line:
                    continue

                date_match = _RE_TRANSACTION_DATE.match(line)

                if date_match:
                    # Flush the previous pending transaction before starting new
                    flush_pending()
                    pending_date_str = date_match.group(1)
                    remainder = line[date_match.end():].strip()
                    amounts_in_line = _RE_AMOUNT.findall(remainder)
                    # Everything before the first amount is part of description
                    desc_part = _RE_AMOUNT.sub("", remainder).strip()
                    if desc_part:
                        pending_desc_parts.append(desc_part)
                    pending_amounts = amounts_in_line

                elif pending_date_str is not None:
                    # Continuation line — may contain more description or amounts
                    amounts_in_line = _RE_AMOUNT.findall(line)
                    if amounts_in_line:
                        pending_amounts.extend(amounts_in_line)
                    desc_part = _RE_AMOUNT.sub("", line).strip()
                    if desc_part and not self._is_page_header(desc_part):
                        pending_desc_parts.append(desc_part)

        # Flush the last pending transaction after the final page
        flush_pending()

        if not transactions:
            raise TransactionExtractionError()

        logger.info("Extracted %d transactions with %d warnings", len(transactions), len(warnings))
        return transactions, warnings

    def _parse_transaction_row(
        self,
        date_str: str,
        description: str,
        amounts: List[str],
        warnings: List[str],
    ) -> Optional[Transaction]:
        """
        Parse a single accumulated transaction row into a Transaction model.

        Monzo statement amount columns: AMOUNT (change) and BALANCE (running).
        Typically the last two numbers on a row are amount and balance.

        Args:
            date_str:    Date string from the date-anchor match.
            description: Accumulated description text.
            amounts:     All numeric strings found on this row.
            warnings:    Mutable list to append warning messages to.

        Returns:
            A Transaction instance, or None if parsing fails.
        """
        raw_row = f"{date_str} {description} {' '.join(amounts)}"

        # Parse date
        tx_date = parse_date(date_str)
        if tx_date is None:
            warnings.append(f"Could not parse date '{date_str}' in row: {raw_row!r}")
            return None

        # Require at least 2 amounts: amount + balance
        if len(amounts) < 2:
            warnings.append(f"Expected 2 amounts, found {len(amounts)} in row: {raw_row!r}")
            # If exactly 1 amount, try treating it as the transaction amount with unknown balance
            if len(amounts) == 1:
                amount = parse_amount(amounts[0])
                if amount is None:
                    warnings.append(f"Could not parse single amount in row: {raw_row!r}")
                    return None
                warnings.append(f"Balance unknown for row: {raw_row!r}")
                return None
            return None

        # Last amount is balance, second-to-last is transaction amount
        amount = parse_amount(amounts[-2])
        balance = parse_amount(amounts[-1])

        if amount is None:
            warnings.append(f"Could not parse amount from '{amounts[-2]}' in row: {raw_row!r}")
            return None
        if balance is None:
            warnings.append(f"Could not parse balance from '{amounts[-1]}' in row: {raw_row!r}")
            return None

        cleaned_desc = description.strip() or "N/A"

        try:
            return Transaction(
                date=tx_date,
                description=cleaned_desc,
                amount=amount,
                balance=balance,
                raw_row=raw_row,
            )
        except Exception as exc:
            warnings.append(f"Model validation failed for row {raw_row!r}: {exc}")
            return None

    @staticmethod
    def _is_page_header(text: str) -> bool:
        """
        Return True if the text looks like a page header/footer, not a description.

        Used to filter out repeated table column headers ("Date", "Description",
        "Amount", "Balance") that appear on every page.
        """
        normalized = text.strip().lower()
        page_artifacts = {"date", "description", "amount", "balance", "transaction", "page"}
        return normalized in page_artifacts or normalized.startswith("page ")
