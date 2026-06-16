"""
Transaction domain model.

Represents a single financial transaction extracted from a bank statement.
Using Pydantic v2 for runtime validation, serialisation, and clear schema
documentation. Decimal is used for all monetary values to avoid floating
point precision errors.
"""

import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Transaction(BaseModel):
    """
    Immutable representation of a single bank statement transaction.

    Attributes:
        date:        Effective date of the transaction.
        description: Cleaned merchant / payee name or narration.
        amount:      Credit (+) or debit (-) value. Always Decimal.
        balance:     Account running balance after this transaction.
        raw_row:     Original extracted text row for debugging / audit.
    """

    # model_config MUST be declared before fields in Pydantic v2
    model_config = ConfigDict(
        frozen=True,               # Immutable — transactions never mutate after parsing
        str_strip_whitespace=True,
    )

    date: datetime.date = Field(..., description="Effective date of the transaction")
    description: str = Field(..., min_length=1, description="Transaction narration or merchant name")
    amount: Decimal = Field(..., description="Signed transaction amount (+credit / -debit)")
    balance: Decimal = Field(..., description="Running balance after this transaction")
    raw_row: Optional[str] = Field(default=None, description="Raw text row as extracted from PDF (debug use)")

    @field_validator("description")
    @classmethod
    def clean_description(cls, v: str) -> str:
        """Collapse multiple whitespace characters into a single space."""
        return " ".join(v.split())

    @property
    def is_credit(self) -> bool:
        """Return True if this transaction is a credit (positive amount)."""
        return self.amount > Decimal("0")

    @property
    def is_debit(self) -> bool:
        """Return True if this transaction is a debit (negative amount)."""
        return self.amount < Decimal("0")

    def to_export_dict(self) -> dict:
        """
        Return a flat dictionary suitable for CSV/Excel export.

        Formats date as ISO string and amounts as plain floats
        (sufficient precision for financial reporting display).
        """
        return {
            "Date": self.date.isoformat(),
            "Description": self.description,
            "Amount": float(self.amount),
            "Balance": float(self.balance),
        }
