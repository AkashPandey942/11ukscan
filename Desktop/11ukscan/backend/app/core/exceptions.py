"""
Domain exception hierarchy for BankScan.

Design principles:
- All exceptions carry a machine-readable ``error_code`` string
  and an HTTP ``status_code`` integer so the global exception handler
  can produce consistent, structured JSON responses without any
  conditional logic.
- Exceptions are grouped by domain: file validation, parsing, export.
- Never raise raw Exception in business logic — always raise a
  BankScanException subclass so the handler can catch it.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Optional


class BankScanException(Exception):
    """
    Base class for all domain exceptions in BankScan.

    Attributes:
        message:     Human-readable description of the error.
        error_code:  Machine-readable uppercase snake_case identifier.
        status_code: HTTP status code to return to the client.
        detail:      Optional additional technical detail (not exposed
                     in production responses, used for internal logging).
    """

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"error_code={self.error_code!r}, "
            f"status_code={self.status_code}, "
            f"message={self.message!r})"
        )


# ------------------------------------------------------------------ #
# File Validation Exceptions
# ------------------------------------------------------------------ #


class FileValidationError(BankScanException):
    """Raised when an uploaded file fails validation checks."""

    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR") -> None:
        super().__init__(message, error_code=error_code, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


class InvalidFileTypeError(FileValidationError):
    """Raised when the uploaded file is not a valid PDF."""

    def __init__(self, message: str = "Only PDF files are accepted.") -> None:
        super().__init__(message, error_code="INVALID_FILE_TYPE")


class FileTooLargeError(FileValidationError):
    """Raised when the uploaded file exceeds the configured size limit."""

    def __init__(self, max_mb: int, actual_mb: float) -> None:
        super().__init__(
            message=f"File size ({actual_mb:.1f} MB) exceeds the {max_mb} MB limit.",
            error_code="FILE_TOO_LARGE",
        )


class PageLimitExceededError(FileValidationError):
    """Raised when the PDF contains more pages than the configured maximum."""

    def __init__(self, max_pages: int, actual_pages: int) -> None:
        super().__init__(
            message=(
                f"PDF has {actual_pages} pages; the maximum allowed is {max_pages}."
            ),
            error_code="PAGE_LIMIT_EXCEEDED",
        )


class EmptyDocumentError(FileValidationError):
    """Raised when the PDF contains no extractable text content."""

    def __init__(self, message: str = "PDF contains no extractable text content.") -> None:
        super().__init__(message, error_code="EMPTY_PDF")


# ------------------------------------------------------------------ #
# Parse Exceptions
# ------------------------------------------------------------------ #


class ParseError(BankScanException):
    """Base class for all parsing-related failures."""

    def __init__(self, message: str, error_code: str = "PARSE_ERROR") -> None:
        super().__init__(message, error_code=error_code, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


class UnsupportedBankFormatError(ParseError):
    """Raised when the parser registry cannot identify the bank format."""

    def __init__(self, message: str = "Could not identify a supported bank statement format in this PDF.") -> None:
        super().__init__(message, error_code="UNSUPPORTED_BANK_FORMAT")


class HeaderExtractionError(ParseError):
    """Raised when required header fields cannot be extracted from page 1."""

    def __init__(self, field: str) -> None:
        super().__init__(
            message=f"Could not extract required header field: '{field}'.",
            error_code="HEADER_EXTRACTION_FAILED",
        )


class TransactionExtractionError(ParseError):
    """Raised when no transactions can be extracted from the statement."""

    def __init__(self, message: str = "No transactions could be extracted from the PDF.") -> None:
        super().__init__(message, error_code="TRANSACTION_EXTRACTION_FAILED")


# ------------------------------------------------------------------ #
# Export Exceptions
# ------------------------------------------------------------------ #


class ExportError(BankScanException):
    """Base class for all export-related failures."""

    def __init__(self, message: str, error_code: str = "EXPORT_ERROR") -> None:
        super().__init__(message, error_code=error_code, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


class CSVExportError(ExportError):
    """Raised when CSV generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="CSV_EXPORT_FAILED")


class ExcelExportError(ExportError):
    """Raised when Excel (.xlsx) generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, error_code="EXCEL_EXPORT_FAILED")


# ------------------------------------------------------------------ #
# Repository Exceptions
# ------------------------------------------------------------------ #


class RepositoryError(BankScanException):
    """Base class for repository / persistence failures."""

    def __init__(self, message: str, error_code: str = "REPOSITORY_ERROR") -> None:
        super().__init__(message, error_code=error_code, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


class RecordNotFoundError(RepositoryError):
    """Raised when a requested record does not exist in the repository."""

    def __init__(self, job_id: str) -> None:
        super().__init__(
            message=f"No statement found for job ID '{job_id}'.",
            error_code="RECORD_NOT_FOUND",
        )
        self.status_code = HTTPStatus.NOT_FOUND


# ------------------------------------------------------------------ #
# Admin Exceptions
# ------------------------------------------------------------------ #


class AdminAuthError(BankScanException):
    """Raised when an admin endpoint is called without a valid X-Admin-Token."""

    def __init__(self, message: str = "Missing or invalid admin token.") -> None:
        super().__init__(message, error_code="ADMIN_AUTH_FAILED", status_code=HTTPStatus.UNAUTHORIZED)
