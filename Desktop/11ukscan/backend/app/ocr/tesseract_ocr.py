"""
Tesseract OCR integration.

Implements BaseOCR using pdf2image to convert PDF pages to images,
and pytesseract to extract text from those images.
"""

import os
import logging
import pytesseract
from pdf2image import convert_from_path

from app.ocr.base_ocr import BaseOCR

logger = logging.getLogger(__name__)


# Hardcode Windows paths if running locally (Docker has them in PATH)
_IS_WINDOWS = os.name == "nt"
_WINDOWS_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_WINDOWS_POPPLER_PATH = os.path.expandvars(
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-25.07.0\Library\bin"
)

if _IS_WINDOWS and os.path.exists(_WINDOWS_TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = _WINDOWS_TESSERACT_CMD

class TesseractOCR(BaseOCR):
    """
    OCR engine implementation using Tesseract via pytesseract.
    """

    def extract_text(self, pdf_path: str) -> list[str]:
        """
        Convert PDF to images and extract text using Tesseract.
        """
        logger.info("Starting Tesseract OCR extraction for %s", pdf_path)
        extracted_pages = []

        try:
            # Convert PDF pages to a list of PIL Image objects.
            poppler_kwargs = {}
            if _IS_WINDOWS and os.path.exists(_WINDOWS_POPPLER_PATH):
                poppler_kwargs["poppler_path"] = _WINDOWS_POPPLER_PATH

            images = convert_from_path(pdf_path, **poppler_kwargs)
            
            for i, image in enumerate(images, start=1):
                logger.debug("Running OCR on page %d", i)
                text = pytesseract.image_to_string(image)
                extracted_pages.append(text)
                
            logger.info("OCR completed. Extracted %d pages.", len(extracted_pages))
            return extracted_pages
            
        except Exception as e:
            logger.error("Tesseract OCR extraction failed: %s", e)
            # Re-raise to let the orchestrator handle the failure
            raise
