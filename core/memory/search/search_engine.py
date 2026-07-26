"""
Memory Search Engine v2 — Modular entry point.

Architecture:
    Query → QueryParser → KeywordSearch → MemoryRanker → Top Memories

Modules:
    query_parser.py   — Parse + expand queries
    keyword_search.py — FTS5 search
    memory_ranker.py  — Multi-factor ranking
    search_engine.py  — This file (orchestrator)

Usage:
    engine = MemorySearchEngine(backend=sqlite_backend)
    results = engine.search("پروژه Atlas")
    context = engine.get_relevant_context("Atlas OS")
"""

from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.search.query_parser import QueryParser
from core.memory.search.keyword_search import KeywordSearch
from core.memory.search.memory_ranker import MemoryRanker


class MemorySearchEngine:
    """
    Modular search engine for Atlas OS memory.

    Orchestrates: QueryParser → KeywordSearch → MemoryRanker
    """

    def __init__(self, backend=None, weights=None):
        """
        Args:
            backend: MemoryBackend instance
            weights: Custom ranking weights (optional)
        """
        self._parser = QueryParser()
        self._search = KeywordSearch(backend=backend)
        self._ranker = MemoryRanker(weights=weights)

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search memory with intelligent ranking.

        Flow:
            1. Parse & expand query
            2. Search with FTS5
            3. Rank results
            4. Return top results

        Args:
            query:          Search query
            memory_types:   Filter by types
            limit:          Max results
            min_importance: Min importance threshold

        Returns:
            List of {record, score, breakdown}
        """
        # ── Step 1: Parse & expand ──
        parsed = self._parser.parse(query)

        # ── Step 2: Keyword search ──
        records = self._search.search(
            terms=parsed["expanded"],
            memory_types=memory_types,
            limit=limit * 2,
            min_importance=min_importance,
        )

        # ── Step 3: Rank ──
        ranked = self._ranker.rank(query=query, records=records)

        # ── Step 4: Return top results ──
        return ranked[:limit]

    def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 1000,
        memory_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get relevant context for Brain prompt construction.

        Returns:
            {query, memories, total_count, approx_tokens}
        """
        results = self.search(query, memory_types=memory_types, limit=20)

        memories = []
        total_chars = 0

        for r in results:
            record = r["record"]
            text = str(record.value)
            chars = len(text)

            if total_chars + chars > max_tokens * 4:
                break

            memories.append({
                "key": record.key,
                "value": text,
                "type": record.memory_type,
                "importance": record.importance,
                "score": r["score"],
            })
            total_chars += chars

        return {
            "query": query,
            "memories": memories,
            "total_count": len(memories),
            "approx_tokens": total_chars // 4,
        }
