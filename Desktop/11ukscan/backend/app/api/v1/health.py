"""
Health check endpoint.

GET /api/v1/health

Returns application status, version, and timestamp.
Used by load balancers, Docker HEALTHCHECK, and monitoring systems.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    registered_parsers: list[str]


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
    description="Returns application health status, version, and registered bank parsers.",
)
async def health_check() -> HealthResponse:
    """
    Application health check endpoint.

    Returns:
        HealthResponse with status, version, and registered parsers.
    """
    from app.parsers.parser_registry import BankParserRegistry
    # Import monzo parser to ensure registration has occurred
    import app.parsers.monzo_parser  # noqa: F401

    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        registered_parsers=BankParserRegistry.list_registered_banks(),
    )
