"""
CSV Exporter — generates a UTF-8 encoded CSV file from parsed statements.

Output format:
    Date,Description,Amount,Balance
    2024-01-01,Amazon Prime,-9.99,1024.55
    ...

Design notes:
- Uses pandas for consistent, tested CSV serialisation.
- UTF-8 with BOM (utf-8-sig) for Excel compatibility on Windows.
- Amounts are written as plain numbers (not currency strings) so they
  can be used in spreadsheet calculations immediately.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from app.core.exceptions import CSVExportError
from app.exporters.base_exporter import AbstractExporter
from app.models.statement import ParsedStatement

logger = logging.getLogger(__name__)


class CSVExporter(AbstractExporter):
    """
    Exports a ParsedStatement to a UTF-8 CSV file.

    Columns: Date, Description, Amount, Balance

    The file is UTF-8 with BOM so Microsoft Excel on Windows opens it
    correctly without requiring an import wizard.
    """

    extension: str = ".csv"

    def export(self, statement: ParsedStatement, output_path: Path) -> Path:
        """
        Write all transactions to a CSV file at ``output_path``.

        Args:
            statement:   Parsed statement containing transaction list.
            output_path: Absolute path for the output .csv file.

        Returns:
            The path to the written CSV file.

        Raises:
            CSVExportError: If the file cannot be written.
        """
        logger.info(
            "Exporting %d transactions to CSV: %s",
            statement.transaction_count,
            output_path,
        )

        try:
            rows = [tx.to_export_dict() for tx in statement.transactions]
            df = pd.DataFrame(
                rows,
                columns=["Date", "Description", "Amount", "Balance"],
            )

            # utf-8-sig adds a BOM byte so Excel auto-detects encoding
            df.to_csv(str(output_path), index=False, encoding="utf-8-sig")

        except Exception as exc:
            logger.exception("CSV export failed: %s", exc)
            raise CSVExportError(f"Failed to write CSV file: {exc}") from exc

        logger.info("CSV export complete: %s (%d KB)",
                    output_path.name,
                    output_path.stat().st_size // 1024)
        return output_path
