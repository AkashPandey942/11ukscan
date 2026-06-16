"""
Abstract base class for all export formats.

Defines the contract that all exporters (CSV, Excel, future PDF, JSON)
must satisfy. The service layer depends on this abstraction, not on
any concrete implementation.

Extension pattern:
    class JSONExporter(AbstractExporter):
        extension = ".json"
        def export(self, statement, output_path): ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.models.statement import ParsedStatement


class AbstractExporter(ABC):
    """
    Abstract base class for all statement export formats.

    Subclasses define:
    - ``extension``: The file extension including the dot (e.g. ".csv").
    - ``export()``:  The method that writes the output file.
    """

    extension: str = ""
    """File extension produced by this exporter, including the dot."""

    @abstractmethod
    def export(self, statement: ParsedStatement, output_path: Path) -> Path:
        """
        Export the parsed statement to the given output path.

        Args:
            statement:   The fully parsed and validated statement data.
            output_path: Absolute path where the output file should be written.
                         The parent directory is guaranteed to exist.

        Returns:
            The absolute Path of the written output file.

        Raises:
            CSVExportError / ExcelExportError: If the export operation fails.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(extension={self.extension!r})"
