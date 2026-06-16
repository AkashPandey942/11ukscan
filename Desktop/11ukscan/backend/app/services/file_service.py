"""
Secure file handling service.

Responsibilities:
- Validate uploaded files (MIME type, magic bytes, size, page count).
- Save files to the uploads directory with secure filenames.
- Clean up temporary files after processing.

SECURITY: All validation must pass before any file is written to disk.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from app.core.config import Settings
from app.core.exceptions import (
    EmptyDocumentError,
    FileTooLargeError,
    InvalidFileTypeError,
    PageLimitExceededError,
)
from app.utils.sanitize import build_secure_upload_path

logger = logging.getLogger(__name__)

# PDF magic bytes — fast validation before any parsing
_PDF_MAGIC_BYTES = b"%PDF-"


class FileService:
    """
    Service for secure file upload handling.

    Validates, saves, and cleans up uploaded PDF files.
    Injected via FastAPI dependency injection.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def validate_and_save(
        self, file_content: bytes, original_filename: str, job_id: str
    ) -> tuple[Path, int]:
        """
        Validate an uploaded file and save it to the upload directory.

        Validation steps (in order):
        1. File extension must be .pdf
        2. Magic bytes must start with %PDF-
        3. MIME type must be application/pdf
        4. File size must not exceed MAX_UPLOAD_SIZE_MB
        5. Page count must not exceed MAX_PDF_PAGES
        6. PDF must contain extractable text (not empty/image-only)

        Args:
            file_content:      Raw bytes of the uploaded file.
            original_filename: Original filename from the upload request.
            job_id:            UUID job ID for this processing run.

        Returns:
            Tuple of (saved file Path, page count).

        Raises:
            InvalidFileTypeError:    Extension or magic bytes mismatch.
            FileTooLargeError:       File exceeds size limit.
            PageLimitExceededError:  PDF has too many pages.
            EmptyDocumentError:      PDF has no extractable text.
        """
        # Step 1: Extension check
        self._validate_extension(original_filename)

        # Step 2: Magic bytes check (fast, before any decoding)
        self._validate_magic_bytes(file_content)

        # Step 3: File size check
        self._validate_file_size(file_content)

        # Step 4: Open as PDF and check page count + text content
        page_count = self._validate_pdf_content(file_content)

        # Step 5: Write to disk only after all validations pass
        save_path = build_secure_upload_path(
            self._settings.UPLOAD_DIR, original_filename, job_id
        )
        save_path.write_bytes(file_content)
        logger.info(
            "File saved: %s (%d bytes, %d pages)",
            save_path.name,
            len(file_content),
            page_count,
        )

        return save_path, page_count

    def _validate_extension(self, filename: str) -> None:
        """Ensure the file has a .pdf extension (case-insensitive)."""
        suffix = Path(filename).suffix.lower()
        if suffix != ".pdf":
            raise InvalidFileTypeError(
                f"Only PDF files are accepted. Received file with extension '{suffix}'."
            )

    def _validate_magic_bytes(self, content: bytes) -> None:
        """Verify the file starts with the PDF magic bytes %PDF-."""
        if not content[:5] == _PDF_MAGIC_BYTES:
            raise InvalidFileTypeError(
                "File does not appear to be a valid PDF (magic bytes check failed)."
            )

    def _validate_file_size(self, content: bytes) -> None:
        """Ensure the file does not exceed the configured size limit."""
        size_bytes = len(content)
        max_bytes = self._settings.max_upload_size_bytes
        if size_bytes > max_bytes:
            raise FileTooLargeError(
                max_mb=self._settings.MAX_UPLOAD_SIZE_MB,
                actual_mb=size_bytes / (1024 * 1024),
            )

    def _validate_pdf_content(self, content: bytes) -> int:
        """
        Open PDF with PyMuPDF to validate page count and text content.

        Returns:
            The number of pages in the PDF.
        """
        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise InvalidFileTypeError(
                f"File could not be opened as a PDF: {exc}"
            )

        try:
            page_count = len(doc)

            if page_count == 0:
                raise EmptyDocumentError("PDF contains no pages.")

            if page_count > self._settings.MAX_PDF_PAGES:
                raise PageLimitExceededError(
                    max_pages=self._settings.MAX_PDF_PAGES,
                    actual_pages=page_count,
                )

            # We explicitly DO NOT check for extractable text here anymore.
            # If the PDF is image-only (e.g. scanned), it will pass this validation
            # and the StatementService will automatically fallback to OCR processing.

            return page_count

        finally:
            doc.close()

    def cleanup(self, file_path: Path) -> None:
        """
        Delete a temporary uploaded file from disk.

        Called after processing is complete. Does not raise on errors —
        failure to clean up is logged as a warning only.

        Args:
            file_path: Path to the file to delete.
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.debug("Cleaned up temp file: %s", file_path.name)
        except OSError as exc:
            logger.warning("Could not delete temp file %s: %s", file_path.name, exc)
