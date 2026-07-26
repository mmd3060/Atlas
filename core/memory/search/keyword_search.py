"""
Keyword Search — FTS5-based search module.

Responsibilities:
  - Search backend using FTS5
  - Support memory type filtering
  - Support importance filtering

Does NOT:
  - Parse queries (QueryParser does that)
  - Rank results (MemoryRanker does that)
"""

from typing import List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend


class KeywordSearch:
    """
    FTS5-based keyword search.

    Usage:
        search = KeywordSearch(backend=sqlite_backend)
        records = search.search("Atlas", memory_types=["project"])
    """

    def __init__(self, backend=None):
        """
        Args:
            backend: MemoryBackend instance
        """
        self._backend = backend

    def search(
        self,
        terms: List[str],
        memory_types: Optional[List[str]] = None,
        limit: int = 20,
        min_importance: float = 0.0,
    ) -> List[MemoryRecord]:
        """
        Search using multiple terms.

        Args:
            terms:          Search terms (from QueryParser)
            memory_types:   Filter by memory types
            limit:          Max results per term
            min_importance: Minimum importance threshold

        Returns:
            List of unique MemoryRecord objects
        """
        if self._backend is None:
            return []

        seen_keys = set()
        results = []

        for term in terms:
            matches = self._backend.search(
                query=term,
                memory_types=memory_types,
                limit=limit,
                min_importance=min_importance,
            )
            for record in matches:
                if record.key not in seen_keys:
                    seen_keys.add(record.key)
                    results.append(record)

        return results

    def search_single(
        self,
        term: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 20,
        min_importance: float = 0.0,
    ) -> List[MemoryRecord]:
        """Search with a single term."""
        if self._backend is None:
            return []

        return self._backend.search(
            query=term,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance,
        )
