"""
Upload endpoint — POST /api/v1/upload

Accepts a multipart PDF upload, validates it, processes it through
the parsing pipeline, and returns download links for CSV and Excel.

Design:
- File bytes are read entirely into memory for validation (up to 50 MB).
- FastAPI async endpoint awaits the parsing pipeline directly.
- Temporary upload file is always cleaned up in the finally block.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import BankScanException
from app.models.statement import ParsedStatement
from app.repositories.in_memory_repository import get_shared_repository
from app.schemas.upload import StatementInfoSchema, UploadSuccessResponse
from app.services.file_service import FileService
from app.services.statement_service import StatementService
from app.utils.id_generator import generate_job_uuid

logger = logging.getLogger(__name__)
router = APIRouter()


def get_file_service(settings: Settings = Depends(get_settings)) -> FileService:
    """FastAPI dependency — returns a FileService instance."""
    return FileService(settings)


def get_statement_service(settings: Settings = Depends(get_settings)) -> StatementService:
    """
    FastAPI dependency — returns a StatementService instance.

    In a production app with DI container (e.g. dependency-injector),
    this would resolve the full object graph. For MVP, we build it here.
    The singleton repository is shared across requests via module-level state.
    """
    return StatementService(settings, repository=get_shared_repository())


@router.post(
    "/upload",
    response_model=UploadSuccessResponse,
    tags=["Statement Processing"],
    summary="Upload and process a bank statement PDF",
    description=(
        "Upload a PDF bank statement (Monzo Business supported). "
        "Returns structured transaction data and download links for CSV and Excel exports."
    ),
    responses={
        200: {"description": "Statement successfully processed"},
        422: {"description": "Validation error — invalid file, too large, or unsupported format"},
        500: {"description": "Internal server error"},
    },
)
async def upload_statement(
    request: Request,
    file: UploadFile = File(..., description="PDF bank statement file"),
    settings: Settings = Depends(get_settings),
    file_service: FileService = Depends(get_file_service),
    statement_service: StatementService = Depends(get_statement_service),
) -> UploadSuccessResponse:
    """
    Upload and process a PDF bank statement.

    Steps:
    1. Read file bytes from multipart form.
    2. Validate and save to uploads/ directory.
    3. Run PDF parsing pipeline (offloaded to thread pool).
    4. Return structured response with download URLs.
    5. Clean up temp file.

    Args:
        request:           FastAPI request (for request_id access).
        file:              Uploaded PDF file.
        settings:          Application settings.
        file_service:      File validation and storage service.
        statement_service: Statement processing orchestrator.

    Returns:
        UploadSuccessResponse with job_id, statement info, and download URLs.
    """
    job_id = generate_job_uuid()
    original_filename = file.filename or "upload.pdf"
    saved_path: Path | None = None

    logger.info(
        "Upload received: filename=%s, content_type=%s, job_id=%s",
        original_filename,
        file.content_type,
        job_id,
    )

    try:
        # Read all bytes (bounded by MAX_UPLOAD_SIZE validation)
        file_bytes = await file.read()

        # Validate and persist to uploads/ directory
        saved_path, page_count = await file_service.validate_and_save(
            file_content=file_bytes,
            original_filename=original_filename,
            job_id=str(job_id),
        )

        # Process the statement — CPU-bound PDF parsing runs in async context.
        # FastAPI runs async endpoints in the event loop; PyMuPDF is thread-safe
        # for concurrent reads but runs synchronously. The statement_service
        # orchestration is lightweight async (awaits repo saves only).
        statement: ParsedStatement = await statement_service.process_statement(
            saved_path, job_id
        )

        # Build response
        info = statement.info
        return UploadSuccessResponse(
            job_id=statement.job_id,
            bank_name=info.bank_name,
            statement_info=StatementInfoSchema(
                bank_name=info.bank_name,
                account_holder=info.account_holder,
                period_start=info.period_start,
                period_end=info.period_end,
                account_number=info.account_number,
                sort_code=info.sort_code,
                statement_type=info.statement_type,
            ),
            transaction_count=statement.transaction_count,
            page_count=statement.page_count,
            warnings=statement.warnings,
            download_csv=f"/api/v1/download/csv/{statement.job_id}",
            download_excel=f"/api/v1/download/excel/{statement.job_id}",
        )

    finally:
        # Always clean up the temp upload file, regardless of success or failure
        if saved_path is not None:
            file_service.cleanup(saved_path)
