"""
Statement Service — the core application orchestrator.

Coordinates the full pipeline:
    File validation → PDF reading → Bank detection → Parsing
    → Validation → Export → Repository storage → Response

This service contains the application's primary business logic.
It depends only on abstractions (PDFReaderAdapter, AbstractRepository)
— never on concrete implementations directly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from app.core.config import Settings
from app.core.exceptions import RecordNotFoundError, EmptyDocumentError
from app.models.statement import ParsedStatement, StatementInfo
from app.models.transaction import Transaction
from app.ocr.ocr_service import OCRService
from app.parsers.monzo_parser import MonzoBusinessParser  # triggers registration
from app.parsers.parser_registry import BankParserRegistry
from app.parsers.pdf_reader import PageText, PyMuPDFAdapter
from app.repositories.base_repository import AbstractRepository
from app.repositories.in_memory_repository import InMemoryStatementRepository
from app.services.export_service import ExportService
from app.utils.id_generator import generate_job_uuid

logger = logging.getLogger(__name__)


class StatementService:
    """
    Primary application service — orchestrates the full PDF processing pipeline.

    Responsibilities:
    1. Coordinate file reading, parsing, validation, export, and storage.
    2. Generate and return the ParsedStatement aggregate.
    3. Retrieve stored statements for download endpoints.

    All dependencies are injected, making the service fully unit-testable.
    """

    def __init__(
        self,
        settings: Settings,
        repository: AbstractRepository[ParsedStatement] | None = None,
        export_service: ExportService | None = None,
        pdf_reader: PyMuPDFAdapter | None = None,
    ) -> None:
        self._settings = settings
        self._repository: AbstractRepository[ParsedStatement] = (
            repository or InMemoryStatementRepository()
        )
        self._export_service = export_service or ExportService(settings)
        self._pdf_reader = pdf_reader or PyMuPDFAdapter()

    async def process_statement(
        self, pdf_path: Path, job_id: UUID | None = None
    ) -> ParsedStatement:
        """
        Execute the full PDF processing pipeline for a validated PDF file.

        Steps:
        1. Extract page text via PDFReaderAdapter.
        2. Auto-detect bank format via BankParserRegistry.
        3. Parse header and transactions.
        4. Build ParsedStatement aggregate.
        5. Export to CSV and Excel.
        6. Persist to repository.
        7. Return the complete ParsedStatement.

        Args:
            pdf_path: Absolute path to the validated PDF on disk.
            job_id:   Optional pre-generated UUID. If None, one is generated.

        Returns:
            A fully populated ParsedStatement with export paths populated.

        Raises:
            UnsupportedBankFormatError: If no parser matches.
            HeaderExtractionError:      If header fields are missing.
            TransactionExtractionError: If no transactions found.
            ExportError:                If file generation fails.
        """
        effective_job_id = job_id or generate_job_uuid()
        logger.info("Processing statement: job_id=%s, file=%s", effective_job_id, pdf_path.name)

        # Step 1: Extract raw page text via PyMuPDF (fast, native)
        pages: list[PageText] = self._pdf_reader.extract_pages(pdf_path)
        
        # Step 1b: Fallback to OCR if native extraction yields no usable text
        if not pages or not any(p.text.strip() for p in pages):
            logger.warning("No extractable text found via native PDF read. Switching to OCR pipeline for %s", pdf_path.name)
            pages = OCRService.extract_pages(str(pdf_path))
            
            # If still no text after OCR, then the document is truly unreadable
            if not pages or not any(p.text.strip() for p in pages):
                raise EmptyDocumentError("PDF contains no extractable text even after OCR. Ensure the document is readable.")
                
        logger.debug("Extracted %d pages from PDF", len(pages))

        # Step 2: Auto-detect bank format

        parser = BankParserRegistry.detect_and_get(pages)
        logger.info("Using parser: %s", parser.bank_name)

        # Step 3: Parse statement (template method: validate → header → transactions)
        info, transactions, warnings = parser.parse(pages)

        # Step 4: Build the aggregate
        statement = ParsedStatement(
            job_id=effective_job_id,
            info=info,
            transactions=transactions,
            page_count=len(pages),
            warnings=warnings,
        )

        # Step 5: Generate exports
        csv_path, excel_path = self._export_service.export_all(statement)
        logger.info(
            "Exports generated: csv=%s, xlsx=%s",
            csv_path.name,
            excel_path.name,
        )

        # Step 6: Persist
        await self._repository.save(statement)

        logger.info(
            "Statement processing complete: job_id=%s, transactions=%d, warnings=%d",
            effective_job_id,
            statement.transaction_count,
            len(warnings),
        )
        return statement

    async def get_statement(self, job_id: UUID) -> ParsedStatement:
        """
        Retrieve a previously processed statement by job ID.

        Args:
            job_id: UUID of the processing job.

        Returns:
            The ParsedStatement.

        Raises:
            RecordNotFoundError: If the job ID is not found.
        """
        statement = await self._repository.get_by_id(job_id)
        if statement is None:
            raise RecordNotFoundError(str(job_id))
        return statement
