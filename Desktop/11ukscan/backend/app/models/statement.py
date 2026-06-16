"""
Statement domain models.

StatementInfo    — Metadata extracted from the statement header (page 1).
ParsedStatement  — Complete output of a parsing job: info + transactions.

Both models are Pydantic v2 for serialisation and validation.
"""

import datetime
import uuid
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.models.transaction import Transaction


class StatementInfo(BaseModel):
    """
    Metadata extracted from the first page of a bank statement.

    Attributes:
        bank_name:       Name of the bank (e.g. "Monzo Business").
        account_holder:  Full name of the account holder or company.
        period_start:    First date of the statement period.
        period_end:      Last date of the statement period.
        account_number:  Bank account number (8 digits for UK accounts).
        sort_code:       UK sort code in XX-XX-XX format.
        statement_type:  Type of account (e.g. "Business Current Account").
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    bank_name: str = Field(..., description="Bank identifier, e.g. 'Monzo Business'")
    account_holder: str = Field(..., description="Account holder full name or company name")
    period_start: datetime.date = Field(..., description="Statement period start date")
    period_end: datetime.date = Field(..., description="Statement period end date")
    account_number: str = Field(..., description="Bank account number")
    sort_code: str = Field(..., description="UK sort code in XX-XX-XX format")
    statement_type: str = Field(default="", description="Account type description")


class ParsedStatement(BaseModel):
    """
    Complete result of a single PDF parsing job.

    This is the central aggregate that flows through the system
    from the parser → repository → export → API response.

    Attributes:
        job_id:        Unique identifier for this processing job.
        info:          Header metadata (account holder, period, etc.).
        transactions:  All extracted transactions, sorted by date ascending.
        page_count:    Total number of pages in the source PDF.
        warnings:      Non-fatal issues encountered during parsing.
        processed_at:  UTC timestamp of when parsing completed.
    """

    job_id: UUID = Field(default_factory=uuid.uuid4, description="Unique job identifier")
    info: StatementInfo = Field(..., description="Statement header metadata")
    transactions: List[Transaction] = Field(default_factory=list, description="All extracted transactions")
    page_count: int = Field(..., ge=1, description="Number of pages in source PDF")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal parsing warnings")
    processed_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
        description="UTC timestamp when parsing completed",
    )

    # ------------------------------------------------------------------ #
    # Computed properties (Pydantic v2 @computed_field)
    # ------------------------------------------------------------------ #

    @computed_field  # type: ignore[misc]
    @property
    def transaction_count(self) -> int:
        """Total number of extracted transactions."""
        return len(self.transactions)

    @computed_field  # type: ignore[misc]
    @property
    def total_credits(self) -> Decimal:
        """Sum of all credit (positive) transaction amounts."""
        return sum(
            (t.amount for t in self.transactions if t.is_credit),
            Decimal("0"),
        )

    @computed_field  # type: ignore[misc]
    @property
    def total_debits(self) -> Decimal:
        """Sum of all debit (negative) transaction amounts."""
        return sum(
            (t.amount for t in self.transactions if t.is_debit),
            Decimal("0"),
        )

    @computed_field  # type: ignore[misc]
    @property
    def closing_balance(self) -> Optional[Decimal]:
        """
        Balance after the last transaction.

        Returns None if no transactions were extracted.
        """
        if self.transactions:
            return self.transactions[-1].balance
        return None
