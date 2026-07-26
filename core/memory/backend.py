"""
Memory Backend — abstract storage interface for Atlas OS Memory Router v2.

Every backend (dict, SQLite, Redis, Pinecone, …) implements this ABC
so the router can swap storage without touching any routing logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord


class MemoryBackend(ABC):
    """
    Abstract backend that the router talks to.

    Implementations must be stateless w.r.t. routing — they just
    store and retrieve MemoryRecord objects.
    """

    # ── lifecycle ────────────────────────────────

    @abstractmethod
    def open(self) -> None:
        """Acquire resources (DB connection, etc.)."""

    @abstractmethod
    def close(self) -> None:
        """Release resources."""

    @abstractmethod
    def health(self) -> bool:
        """Return True if the backend is operational."""

    # ── CRUD ─────────────────────────────────────

    @abstractmethod
    def put(self, record: MemoryRecord) -> None:
        """Insert or overwrite a record (upsert semantics)."""

    @abstractmethod
    def get(self, memory_type: str, key: str) -> Optional[MemoryRecord]:
        """Retrieve a single record, or None."""

    @abstractmethod
    def update(self, record: MemoryRecord) -> None:
        """Update an existing record (alias of put for most backends)."""

    @abstractmethod
    def delete(self, memory_type: str, key: str) -> bool:
        """Delete a record. Return True if it existed."""

    # ── bulk / query ─────────────────────────────

    @abstractmethod
    def list_records(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryRecord]:
        """
        List records, optionally filtered by memory_type.
        Returns at most *limit* records starting from *offset*.
        """

    @abstractmethod
    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[MemoryRecord]:
        """
        Search across stored records.

        Default implementation falls back to substring matching;
        vector backends (Pinecone, Chroma, …) override with
        semantic search.
        """

    @abstractmethod
    def count(self, memory_type: Optional[str] = None) -> int:
        """Return the total number of records, optionally per type."""

    # ── maintenance ──────────────────────────────

    @abstractmethod
    def purge_expired(self) -> int:
        """Remove all records whose TTL has elapsed. Return count removed."""

    @abstractmethod
    def clear(self, memory_type: Optional[str] = None) -> int:
        """
        Wipe records. If memory_type is given, only wipe that type.
        Return count of records removed.
        """
