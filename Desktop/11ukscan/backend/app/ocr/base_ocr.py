"""
Base OCR interface.

Defines the contract for all OCR engine integrations.
This ensures the business logic is decoupled from any specific OCR library
(e.g., Tesseract, Google Document AI, AWS Textract).
"""

from abc import ABC, abstractmethod


class BaseOCR(ABC):
    """
    Abstract base class for OCR engines.
    """

    @abstractmethod
    def extract_text(self, pdf_path: str) -> list[str]:
        """
        Extract text from an image-based PDF document.

        Args:
            pdf_path: Absolute path to the PDF file on disk.

        Returns:
            A list of strings, where each string represents the full
            extracted text of a single page in order.
        """
        pass
