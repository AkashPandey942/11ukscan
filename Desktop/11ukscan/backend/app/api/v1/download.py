"""
Download endpoints.

GET /api/v1/download/csv/{job_id}
GET /api/v1/download/excel/{job_id}

Serves generated export files as streaming file responses.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import RecordNotFoundError
from app.utils.sanitize import build_output_path

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_output_file(job_id: UUID, extension: str, settings: Settings) -> Path:
    """
    Resolve the output file path for a given job and extension.

    Args:
        job_id:    UUID of the processing job.
        extension: File extension (".csv" or ".xlsx").
        settings:  Application settings.

    Returns:
        Path to the output file.

    Raises:
        RecordNotFoundError: If the file does not exist on disk.
    """
    path = build_output_path(settings.OUTPUT_DIR, str(job_id), extension)
    if not path.exists():
        raise RecordNotFoundError(str(job_id))
    return path


@router.get(
    "/download/csv/{job_id}",
    tags=["Downloads"],
    summary="Download CSV export",
    description="Download the CSV export for a previously processed statement.",
    response_class=FileResponse,
)
async def download_csv(
    job_id: UUID,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """
    Serve the CSV export file for a given job ID.

    Args:
        job_id:   UUID of the processing job.
        settings: Application settings.

    Returns:
        FileResponse streaming the CSV file.

    Raises:
        RecordNotFoundError: If no CSV exists for this job ID.
    """
    file_path = _get_output_file(job_id, ".csv", settings)
    logger.info("Serving CSV download: job_id=%s, file=%s", job_id, file_path.name)
    return FileResponse(
        path=str(file_path),
        media_type="text/csv",
        filename=f"statement_{job_id}.csv",
        headers={"Content-Disposition": f'attachment; filename="statement_{job_id}.csv"'},
    )


@router.get(
    "/download/excel/{job_id}",
    tags=["Downloads"],
    summary="Download Excel export",
    description="Download the Excel (.xlsx) export for a previously processed statement.",
    response_class=FileResponse,
)
async def download_excel(
    job_id: UUID,
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    """
    Serve the Excel export file for a given job ID.

    Args:
        job_id:   UUID of the processing job.
        settings: Application settings.

    Returns:
        FileResponse streaming the .xlsx file.

    Raises:
        RecordNotFoundError: If no Excel file exists for this job ID.
    """
    file_path = _get_output_file(job_id, ".xlsx", settings)
    logger.info("Serving Excel download: job_id=%s, file=%s", job_id, file_path.name)
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"statement_{job_id}.xlsx",
        headers={
            "Content-Disposition": f'attachment; filename="statement_{job_id}.xlsx"'
        },
    )
