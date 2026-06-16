"""
API Request and Response Pydantic Schemas for the upload endpoint.

Schemas are separate from domain models intentionally:
- Models represent domain truth (internal).
- Schemas represent the API contract (external, versioned).

This separation allows internal model changes without breaking
the API contract, and vice versa.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StatementInfoSchema(BaseModel):
    """Statement header metadata as returned in the API response."""

    bank_name: str = Field(..., description="Bank identifier")
    account_holder: str = Field(..., description="Account holder name")
    period_start: date = Field(..., description="Statement period start")
    period_end: date = Field(..., description="Statement period end")
    account_number: str = Field(..., description="Bank account number")
    sort_code: str = Field(..., description="Sort code in XX-XX-XX format")
    statement_type: str = Field(..., description="Account type")


class UploadSuccessResponse(BaseModel):
    """Successful upload response schema — returned after PDF processing."""

    status: str = Field(default="success")
    job_id: UUID = Field(..., description="Unique job identifier for downloads")
    bank_name: str = Field(..., description="Detected bank format")
    statement_info: StatementInfoSchema
    transaction_count: int = Field(..., description="Number of extracted transactions", ge=0)
    page_count: int = Field(..., description="Number of pages in the PDF", ge=1)
    warnings: List[str] = Field(default_factory=list, description="Non-fatal parsing warnings")
    download_csv: str = Field(..., description="Relative URL to download CSV file")
    download_excel: str = Field(..., description="Relative URL to download Excel file")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    status: str = Field(default="error")
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    request_id: Optional[str] = Field(default=None, description="Request correlation ID")
