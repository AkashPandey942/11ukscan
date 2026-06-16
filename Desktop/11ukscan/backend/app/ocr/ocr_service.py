"""
OCR Orchestrator Service.

Wraps the OCR Factory and adapts the raw text output into the `PageText`
dataclass format expected by the bank parsers.
"""

import logging
from app.ocr.ocr_factory import OCRFactory
from app.parsers.pdf_reader import PageText

logger = logging.getLogger(__name__)


class OCRService:
    """
    Orchestrates OCR extraction and maps the output for the parser layer.
    """

    @classmethod
    def extract_pages(cls, pdf_path: str) -> list[PageText]:
        """
        Run OCR on the given PDF and return standard PageText objects.
        
        Args:
            pdf_path: The absolute path to the PDF file.
            
        Returns:
            A list of PageText objects compatible with our parsers.
        """
        engine = OCRFactory.get_ocr_engine()
        raw_pages_text = engine.extract_text(pdf_path)
        
        page_texts = []
        for index, text in enumerate(raw_pages_text, start=1):
            # We don't have accurate width/height from OCR easily without 
            # inspecting the PIL image, but the parsers currently only rely on `text`.
            # We default to standard A4 points (595x842) as a placeholder.
            page_texts.append(
                PageText(
                    page_number=index,
                    text=text,
                    width=595.0,
                    height=842.0,
                )
            )
            
        return page_texts
