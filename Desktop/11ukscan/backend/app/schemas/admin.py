"""
API Response Pydantic Schemas for the admin endpoints.

Schemas are separate from domain models intentionally:
- Models represent domain truth (internal).
- Schemas represent the API contract (external, versioned).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class ScanSummarySchema(BaseModel):
    """One row in the admin scan list — summary only, no transaction lines."""

    job_id: UUID = Field(..., description="Unique job identifier")
    bank_name: str = Field(..., description="Detected bank format")
    account_holder: str = Field(..., description="Account holder name")
    period_start: date = Field(..., description="Statement period start")
    period_end: date = Field(..., description="Statement period end")
    transaction_count: int = Field(..., description="Number of extracted transactions", ge=0)
    page_count: int = Field(..., description="Number of pages in the source PDF", ge=1)
    warnings_count: int = Field(..., description="Number of non-fatal parsing warnings", ge=0)
    processed_at: datetime = Field(..., description="UTC timestamp when parsing completed")


class AdminStatsSchema(BaseModel):
    """Aggregate counters shown on the admin dashboard."""

    total_scans: int = Field(..., description="Total scans processed since the process started", ge=0)
    total_transactions: int = Field(..., description="Sum of transactions across all scans", ge=0)
    total_warnings: int = Field(..., description="Sum of parsing warnings across all scans", ge=0)
    banks: List[str] = Field(default_factory=list, description="Distinct bank formats seen")


class ScanDetailSchema(ScanSummarySchema):
    """Full scan detail — adds account identifiers and financial totals."""

    account_number: str = Field(..., description="Bank account number")
    sort_code: str = Field(..., description="Sort code in XX-XX-XX format")
    statement_type: str = Field(..., description="Account type")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal parsing warnings")
    total_credits: Decimal = Field(..., description="Sum of credit transaction amounts")
    total_debits: Decimal = Field(..., description="Sum of debit transaction amounts")
