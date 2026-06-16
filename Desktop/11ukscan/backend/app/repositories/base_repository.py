"""
Abstract repository interface.

Defines the contract for all persistence backends. The service layer
depends only on this abstraction — it never imports MongoDB, Redis,
or any concrete storage directly.

To enable MongoDB persistence:
1. Create MongoRepository(AbstractRepository[ParsedStatement]).
2. Register it in main.py's DI container.
Zero changes to services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar("T")


class AbstractRepository(ABC, Generic[T]):
    """
    Generic abstract repository with standard CRUD operations.

    Type parameter T represents the domain entity being persisted.
    """

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Persist a new entity.

        Args:
            entity: The domain object to store.

        Returns:
            The stored entity (may include generated fields).
        """
        ...

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """
        Retrieve an entity by its UUID.

        Args:
            entity_id: The UUID primary key.

        Returns:
            The entity, or None if not found.
        """
        ...

    @abstractmethod
    async def list_all(self) -> List[T]:
        """
        Return all stored entities.

        Returns:
            List of all entities in the repository.
        """
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """
        Delete an entity by its UUID.

        Args:
            entity_id: The UUID of the entity to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...
