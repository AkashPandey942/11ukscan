"""
Export Service — orchestrates CSV and Excel export operations.

The service depends on ``AbstractExporter`` instances injected via DI.
Adding new export formats (JSON, PDF report) requires only:
1. Creating a new AbstractExporter subclass.
2. Injecting it here.
No changes to the API layer or statement service.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import Settings
from app.exporters.base_exporter import AbstractExporter
from app.exporters.csv_exporter import CSVExporter
from app.exporters.excel_exporter import ExcelExporter
from app.models.statement import ParsedStatement
from app.utils.sanitize import build_output_path

logger = logging.getLogger(__name__)


class ExportService:
    """
    Orchestrates generation of all export file formats for a parsed statement.

    Injects concrete exporter implementations and delegates to each.
    Returns the file paths so the API layer can serve downloads.
    """

    def __init__(
        self,
        settings: Settings,
        csv_exporter: AbstractExporter | None = None,
        excel_exporter: AbstractExporter | None = None,
    ) -> None:
        self._settings = settings
        self._csv_exporter: AbstractExporter = csv_exporter or CSVExporter()
        self._excel_exporter: AbstractExporter = excel_exporter or ExcelExporter()

    def export_all(self, statement: ParsedStatement) -> tuple[Path, Path]:
        """
        Generate both CSV and Excel exports for a parsed statement.

        Args:
            statement: The fully parsed statement.

        Returns:
            Tuple of (csv_path, excel_path).

        Raises:
            CSVExportError, ExcelExportError: If either export fails.
        """
        job_id_str = str(statement.job_id)

        csv_path = build_output_path(self._settings.OUTPUT_DIR, job_id_str, ".csv")
        excel_path = build_output_path(self._settings.OUTPUT_DIR, job_id_str, ".xlsx")

        logger.info("Starting export for job_id=%s", job_id_str)

        self._csv_exporter.export(statement, csv_path)
        self._excel_exporter.export(statement, excel_path)

        logger.info(
            "Export complete for job_id=%s: csv=%s, xlsx=%s",
            job_id_str,
            csv_path.name,
            excel_path.name,
        )
        return csv_path, excel_path
