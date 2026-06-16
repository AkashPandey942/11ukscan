"""
OCR Factory for instantiating the correct OCR engine.
"""

import logging
from app.ocr.base_ocr import BaseOCR
from app.ocr.tesseract_ocr import TesseractOCR

logger = logging.getLogger(__name__)


class OCRFactory:
    """
    Factory to retrieve the configured OCR engine.
    This allows easy swapping to Google Document AI or AWS Textract later.
    """

    @classmethod
    def get_ocr_engine(cls) -> BaseOCR:
        """
        Return the default OCR engine instance.
        Currently hardcoded to TesseractOCR, but can be driven by config later.
        """
        logger.debug("Instantiating TesseractOCR from OCRFactory")
        return TesseractOCR()
