"""
Admin endpoints.

GET /api/v1/admin/scans           — list every scan processed by this process
GET /api/v1/admin/scans/{job_id}  — full detail for one scan
GET /api/v1/admin/stats           — aggregate counters for an admin dashboard

All endpoints require a valid X-Admin-Token header (see Settings.ADMIN_API_TOKEN).
Backed by the same in-memory repository used by the upload pipeline, so data
is only visible for the lifetime of the running process (resets on restart) —
identical lifetime guarantee to everything else this app currently stores.
"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Header

from app.core.config import Settings, get_settings
from app.core.exceptions import AdminAuthError, RecordNotFoundError
from app.models.statement import ParsedStatement
from app.repositories.base_repository import AbstractRepository
from app.repositories.in_memory_repository import get_shared_repository
from app.schemas.admin import AdminStatsSchema, ScanDetailSchema, ScanSummarySchema

logger = logging.getLogger(__name__)
router = APIRouter()


def get_repository() -> AbstractRepository[ParsedStatement]:
    """FastAPI dependency — returns the shared in-memory statement repository."""
    return get_shared_repository()


def require_admin_token(
    x_admin_token: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """FastAPI dependency — raises AdminAuthError unless the header matches ADMIN_API_TOKEN."""
    if not x_admin_token or x_admin_token != settings.ADMIN_API_TOKEN:
        raise AdminAuthError()


def _to_summary(statement: ParsedStatement) -> ScanSummarySchema:
    info = statement.info
    return ScanSummarySchema(
        job_id=statement.job_id,
        bank_name=info.bank_name,
        account_holder=info.account_holder,
        period_start=info.period_start,
        period_end=info.period_end,
        transaction_count=statement.transaction_count,
        page_count=statement.page_count,
        warnings_count=len(statement.warnings),
        processed_at=statement.processed_at,
    )


@router.get(
    "/admin/scans",
    response_model=list[ScanSummarySchema],
    tags=["Admin"],
    summary="List all processed scans",
    dependencies=[Depends(require_admin_token)],
)
async def list_scans(
    repository: AbstractRepository[ParsedStatement] = Depends(get_repository),
) -> list[ScanSummarySchema]:
    """Return a summary of every scan processed since the process started, newest first."""
    statements = await repository.list_all()
    statements.sort(key=lambda s: s.processed_at, reverse=True)
    return [_to_summary(s) for s in statements]


@router.get(
    "/admin/scans/{job_id}",
    response_model=ScanDetailSchema,
    tags=["Admin"],
    summary="Get full detail for one scan",
    dependencies=[Depends(require_admin_token)],
)
async def get_scan(
    job_id: UUID,
    repository: AbstractRepository[ParsedStatement] = Depends(get_repository),
) -> ScanDetailSchema:
    """Return full detail (including financial totals) for a single scan."""
    statement = await repository.get_by_id(job_id)
    if statement is None:
        raise RecordNotFoundError(str(job_id))

    info = statement.info
    return ScanDetailSchema(
        job_id=statement.job_id,
        bank_name=info.bank_name,
        account_holder=info.account_holder,
        period_start=info.period_start,
        period_end=info.period_end,
        transaction_count=statement.transaction_count,
        page_count=statement.page_count,
        warnings_count=len(statement.warnings),
        processed_at=statement.processed_at,
        account_number=info.account_number,
        sort_code=info.sort_code,
        statement_type=info.statement_type,
        warnings=statement.warnings,
        total_credits=statement.total_credits,
        total_debits=statement.total_debits,
    )


@router.get(
    "/admin/stats",
    response_model=AdminStatsSchema,
    tags=["Admin"],
    summary="Aggregate counters for the admin dashboard",
    dependencies=[Depends(require_admin_token)],
)
async def get_stats(
    repository: AbstractRepository[ParsedStatement] = Depends(get_repository),
) -> AdminStatsSchema:
    """Return total scans, total transactions, total warnings, and distinct banks seen."""
    statements = await repository.list_all()
    return AdminStatsSchema(
        total_scans=len(statements),
        total_transactions=sum(s.transaction_count for s in statements),
        total_warnings=sum(len(s.warnings) for s in statements),
        banks=sorted({s.info.bank_name for s in statements}),
    )
