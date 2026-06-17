"""
API Router aggregator.

Combines all versioned routers into a single router that is
mounted on the FastAPI application in main.py.

Adding a new API version:
1. Create backend/app/api/v2/ with new route modules.
2. Import and include v2_router here with prefix="/api/v2".
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, download, health, upload

api_router = APIRouter()

api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(upload.router, prefix="/api/v1")
api_router.include_router(download.router, prefix="/api/v1")
api_router.include_router(admin.router, prefix="/api/v1")
