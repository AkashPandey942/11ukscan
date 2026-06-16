"""
BankScan FastAPI Application Entry Point.

This module:
1. Creates the FastAPI application instance.
2. Configures logging and middleware.
3. Registers all API routers.
4. Handles application lifespan (startup / shutdown).

Never put business logic here — this is pure wiring.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.core.middleware import register_middleware

# Trigger parser registration at import time
import app.parsers.monzo_parser  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    FastAPI lifespan context manager.

    Runs startup logic before the first request and shutdown
    logic after the last request.

    Startup:
    - Configure logging.
    - Ensure upload/output directories exist.
    - Log registered bank parsers.

    Shutdown:
    - Log graceful shutdown message.
    """
    settings = get_settings()
    configure_logging(log_level=settings.LOG_LEVEL, debug=settings.DEBUG)

    logger.info("=" * 60)
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Debug mode: %s", settings.DEBUG)

    # Ensure required directories exist
    settings.ensure_directories()
    logger.info("Upload directory: %s", settings.UPLOAD_DIR)
    logger.info("Output directory: %s", settings.OUTPUT_DIR)

    # Log registered parsers
    from app.parsers.parser_registry import BankParserRegistry
    registered = BankParserRegistry.list_registered_banks()
    logger.info("Registered parsers: %s", registered)
    logger.info("=" * 60)

    yield

    logger.info("%s shutting down gracefully.", settings.APP_NAME)


def create_app() -> FastAPI:
    """
    FastAPI application factory.

    Returns a fully configured application instance.
    Using a factory function (rather than a module-level ``app = FastAPI()``)
    makes the app testable — tests can call ``create_app()`` to get a
    fresh, isolated instance.

    Returns:
        Configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "BankScan — Enterprise PDF Bank Statement Parser. "
            "Upload Monzo Business PDFs and download structured CSV / Excel exports."
        ),
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
        openapi_url="/api/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Register middleware and global exception handlers
    register_middleware(app, settings)

    # Mount all API routes
    app.include_router(api_router)

    return app


# Module-level app instance for Uvicorn
app = create_app()
