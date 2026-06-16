"""
Bank Parser Registry — factory and auto-detection engine.

The registry uses a class-level dictionary to map bank name strings
to parser classes. This enables:
1. Auto-detection: Scan page 1 text to find the correct parser.
2. Named lookup: Get a specific parser by bank name.
3. Open/Closed extension: Register new parsers without touching this file.

Registration happens at import time via the ``@BankParserRegistry.register``
decorator — or explicitly via ``BankParserRegistry.register()``.

Usage:
    # Auto-detect from PDF content:
    parser = BankParserRegistry.detect_and_get(pages)

    # Or register a new parser from an external module:
    BankParserRegistry.register(HSBCParser)
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Type

from app.core.exceptions import UnsupportedBankFormatError
from app.parsers.base_parser import AbstractBankStatementParser
from app.parsers.pdf_reader import PageText

logger = logging.getLogger(__name__)


class BankParserRegistry:
    """
    Singleton registry of all available bank statement parsers.

    Parsers are registered at module import time. The registry then
    exposes a ``detect_and_get()`` factory method used by the service
    layer to obtain the correct parser for any given PDF.

    Thread-safety: The ``_parsers`` dict is only mutated at import time
    (during parser class registration), so no locking is required for
    the read-only ``detect_and_get`` path.
    """

    _parsers: Dict[str, Type[AbstractBankStatementParser]] = {}

    @classmethod
    def register(cls, parser_class: Type[AbstractBankStatementParser]) -> Type[AbstractBankStatementParser]:
        """
        Register a parser class in the registry.

        Can be used as a class decorator:
            @BankParserRegistry.register
            class MonzoBusinessParser(AbstractBankStatementParser): ...

        Or called explicitly:
            BankParserRegistry.register(HSBCParser)

        Args:
            parser_class: A concrete subclass of AbstractBankStatementParser.

        Returns:
            The parser_class unchanged (for decorator compatibility).

        Raises:
            ValueError: If bank_name is empty or already registered.
        """
        bank_name = parser_class.bank_name
        if not bank_name:
            raise ValueError(
                f"Parser class {parser_class.__name__} must define a "
                f"non-empty ``bank_name`` class attribute."
            )
        if bank_name in cls._parsers:
            logger.warning(
                "Overwriting existing parser registration for bank '%s'",
                bank_name,
            )
        cls._parsers[bank_name] = parser_class
        logger.debug("Registered parser '%s' -> %s", bank_name, parser_class.__name__)
        return parser_class

    @classmethod
    def detect_and_get(cls, pages: List[PageText]) -> AbstractBankStatementParser:
        """
        Auto-detect the bank format and return the appropriate parser instance.

        Iterates all registered parsers in registration order and returns
        the first one whose ``can_parse()`` method returns True.

        Args:
            pages: All extracted page text objects from the PDF.

        Returns:
            An instantiated parser ready to call ``.parse(pages)``.

        Raises:
            UnsupportedBankFormatError: If no registered parser matches.
        """
        logger.info(
            "Auto-detecting bank format from %d registered parsers...",
            len(cls._parsers),
        )

        for bank_name, parser_class in cls._parsers.items():
            instance = parser_class()
            if instance.can_parse(pages):
                logger.info("Detected bank format: %s", bank_name)
                return instance

        logger.warning(
            "No parser matched. Registered parsers: %s",
            list(cls._parsers.keys()),
        )
        raise UnsupportedBankFormatError()

    @classmethod
    def get_by_name(cls, bank_name: str) -> AbstractBankStatementParser:
        """
        Retrieve a parser by its exact bank name string.

        Args:
            bank_name: The ``bank_name`` string of the desired parser.

        Returns:
            An instantiated parser.

        Raises:
            UnsupportedBankFormatError: If the bank name is not registered.
        """
        parser_class = cls._parsers.get(bank_name)
        if parser_class is None:
            raise UnsupportedBankFormatError(
                f"No parser registered for bank '{bank_name}'. "
                f"Available: {list(cls._parsers.keys())}"
            )
        return parser_class()

    @classmethod
    def list_registered_banks(cls) -> List[str]:
        """
        Return a sorted list of all registered bank names.

        Returns:
            Sorted list of bank name strings.
        """
        return sorted(cls._parsers.keys())
