"""
PDF Reader Adapter — abstraction layer over PDF extraction engines.

Design:
    The ``PDFReaderAdapter`` Protocol defines the interface that all PDF
    reading backends must satisfy. The ``PyMuPDFAdapter`` is the default
    production implementation using PyMuPDF (fitz).

    To add pdfplumber, Tesseract OCR, or Google Document AI later:
    1. Create a new class implementing the ``PDFReaderAdapter`` protocol.
    2. Inject it into ``FileService`` instead of ``PyMuPDFAdapter``.
    Zero changes to parsers or business logic.

PageText is a dataclass carrying the page number and raw extracted text,
making it easy to pass page-specific context through the pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PageText:
    """
    Represents text content extracted from a single PDF page.

    Attributes:
        page_number: 1-indexed page number within the document.
        text:        Raw text extracted from the page, preserving whitespace.
        width:       Page width in points (useful for column detection).
        height:      Page height in points.
    """

    page_number: int
    text: str
    width: float = 0.0
    height: float = 0.0

    @property
    def is_empty(self) -> bool:
        """Return True if the page contains no meaningful text content."""
        return not self.text.strip()

    @property
    def lines(self) -> List[str]:
        """Split page text into individual lines."""
        return self.text.splitlines()


@runtime_checkable
class PDFReaderAdapter(Protocol):
    """
    Protocol (structural interface) for PDF text extraction backends.

    Any class that implements ``extract_pages`` satisfies this protocol.
    No inheritance required — duck-typed compatibility.
    """

    def extract_pages(self, path: Path) -> List[PageText]:
        """
        Extract text from all pages of a PDF file.

        Args:
            path: Absolute path to the PDF file on disk.

        Returns:
            A list of ``PageText`` objects, one per page, in order.

        Raises:
            FileNotFoundError: If the PDF does not exist at ``path``.
            RuntimeError:      If the PDF is corrupted or unreadable.
        """
        ...


class PyMuPDFAdapter:
    """
    PDF text extractor using PyMuPDF (fitz) — the primary production engine.

    PyMuPDF is chosen because it:
    - Is significantly faster than pdfplumber for text-heavy documents.
    - Preserves relative text positioning (crucial for column parsing).
    - Handles password-protected PDFs gracefully.
    - Has minimal memory overhead on large documents.

    The ``extract_text`` call uses the "text" mode which preserves
    whitespace layout, critical for right-aligned amount column detection.
    """

    def extract_pages(self, path: Path) -> List[PageText]:
        """
        Extract text from all pages using PyMuPDF.

        Args:
            path: Absolute path to the validated PDF file.

        Returns:
            List of ``PageText`` objects, one per page (1-indexed).

        Raises:
            RuntimeError: If PyMuPDF cannot open or read the file.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError as e:
            raise RuntimeError(
                "PyMuPDF (fitz) is not installed. "
                "Install it with: pip install pymupdf"
            ) from e

        pages: List[PageText] = []

        try:
            doc = fitz.open(str(path))
        except Exception as exc:
            raise RuntimeError(f"Cannot open PDF at {path}: {exc}") from exc

        try:
            for page_index in range(len(doc)):
                page = doc[page_index]
                # "text" mode: preserves layout whitespace for column parsing
                text = page.get_text("text")
                rect = page.rect
                pages.append(
                    PageText(
                        page_number=page_index + 1,
                        text=text,
                        width=rect.width,
                        height=rect.height,
                    )
                )
                logger.debug(
                    "Extracted page %d: %d chars",
                    page_index + 1,
                    len(text),
                )
        finally:
            doc.close()

        logger.info("Extracted %d pages from %s", len(pages), path.name)
        return pages
