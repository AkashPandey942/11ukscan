"""
In-Memory Repository — MVP implementation for ParsedStatement storage.

Stores statements in a process-level dictionary keyed by job UUID.
This is production-appropriate for MVP single-instance deployments.

To replace with MongoDB:
1. Create MongoStatementRepository(AbstractRepository[ParsedStatement]).
2. Swap the injection in main.py.
3. Delete this file (or keep for testing).

Thread safety: Python's GIL makes dict operations thread-safe for
simple get/set, which is sufficient for the async FastAPI context.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from uuid import UUID

from app.models.statement import ParsedStatement
from app.repositories.base_repository import AbstractRepository

logger = logging.getLogger(__name__)


class InMemoryStatementRepository(AbstractRepository[ParsedStatement]):
    """
    In-process dictionary-backed repository for ParsedStatement objects.

    Suitable for MVP and testing. Does not survive process restarts.
    Maximum memory usage: ~60 pages × ~100 transactions × ~512 bytes ≈ 3 MB
    per statement — perfectly acceptable for typical concurrent load.
    """

    def __init__(self) -> None:
        self._store: Dict[UUID, ParsedStatement] = {}
        logger.debug("InMemoryStatementRepository initialised")

    async def save(self, entity: ParsedStatement) -> ParsedStatement:
        """
        Store a ParsedStatement by its job_id UUID.

        Args:
            entity: The parsed statement to store.

        Returns:
            The stored entity unchanged.
        """
        self._store[entity.job_id] = entity
        logger.debug("Saved statement job_id=%s", entity.job_id)
        return entity

    async def get_by_id(self, entity_id: UUID) -> Optional[ParsedStatement]:
        """
        Retrieve a ParsedStatement by job UUID.

        Args:
            entity_id: The job UUID to look up.

        Returns:
            The ParsedStatement, or None if not found.
        """
        result = self._store.get(entity_id)
        if result is None:
            logger.debug("Statement not found for job_id=%s", entity_id)
        return result

    async def list_all(self) -> List[ParsedStatement]:
        """Return all stored statements."""
        return list(self._store.values())

    async def delete(self, entity_id: UUID) -> bool:
        """
        Remove a statement from the store.

        Args:
            entity_id: The job UUID to delete.

        Returns:
            True if deleted, False if not found.
        """
        if entity_id in self._store:
            del self._store[entity_id]
            logger.debug("Deleted statement job_id=%s", entity_id)
            return True
        return False

    @property
    def count(self) -> int:
        """Return the number of statements currently in the store."""
        return len(self._store)
