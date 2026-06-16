"""
Middleware and global exception handler configuration.

Registers:
1. CORSMiddleware       — Configurable allowed origins.
2. RequestIDMiddleware  — Injects X-Request-ID header for log correlation.
3. SecurityHeadersMiddleware — Adds production security response headers.
4. Global exception handlers — Converts domain exceptions to JSON.

Call ``register_middleware(app, settings)`` once from main.py.
"""

from __future__ import annotations

import logging
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import Settings
from app.core.exceptions import BankScanException

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Request ID Middleware
# ------------------------------------------------------------------ #


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique ``X-Request-ID`` header into every request/response.

    The ID is also stored in request.state so route handlers and
    downstream services can reference it for log correlation.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Propagate to logging records via a logging filter
        _request_id_ctx_var.set(request_id)

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Context variable for request-scoped logging (Python 3.7+)
import contextvars
_request_id_ctx_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIDFilter(logging.Filter):
    """Injects request_id into every LogRecord within a request context."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx_var.get("")  # type: ignore[attr-defined]
        return True


# ------------------------------------------------------------------ #
# Security Headers Middleware
# ------------------------------------------------------------------ #


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security-oriented HTTP response headers to every response.

    Headers set:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Cache-Control: no-store (for API responses)
    - Permissions-Policy: minimal set
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        # Only set Cache-Control on API routes to avoid breaking static asset caching
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        return response


# ------------------------------------------------------------------ #
# Global Exception Handlers
# ------------------------------------------------------------------ #


def _domain_exception_handler(request: Request, exc: BankScanException) -> JSONResponse:
    """
    Convert any BankScanException subclass to a structured JSON response.

    Response body schema:
        {
            "status": "error",
            "code": "<ERROR_CODE>",
            "message": "<human-readable message>",
            "request_id": "<uuid>"
        }
    """
    request_id = getattr(request.state, "request_id", "")

    logger.warning(
        "Domain exception caught: %s",
        exc.error_code,
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "request_id": request_id,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.error_code,
            "message": exc.message,
            "request_id": request_id,
        },
    )


def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any unexpected exceptions.

    Logs the full traceback for debugging, but returns a generic
    error message to the client (never expose internal details).
    """
    request_id = getattr(request.state, "request_id", "")
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "request_id": request_id,
        },
    )


# ------------------------------------------------------------------ #
# Registration Helper
# ------------------------------------------------------------------ #


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """
    Register all middleware and exception handlers on the FastAPI app.

    Args:
        app:      The FastAPI application instance.
        settings: Application settings (used for CORS origins).
    """
    # Order matters — middleware is applied in reverse registration order
    # for requests (LIFO), so register CORS first (outermost).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Content-Disposition"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # Exception handlers
    app.add_exception_handler(BankScanException, _domain_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_exception_handler)  # type: ignore[arg-type]

    # Attach logging filter to root logger so request_id is in every record
    request_id_filter = RequestIDFilter()
    logging.getLogger().addFilter(request_id_filter)
