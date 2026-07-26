"""
Memory Search Engine v1 — Intelligent search layer for Atlas OS.

Architecture:
    User Query → SearchEngine → QueryAnalyzer
                                ├── Keyword Search (FTS5)
                                ├── Synonym Expansion
                                └── Memory Ranker
                                    ├── similarity
                                    ├── importance
                                    ├── recency
                                    ├── access_count
                                    └── memory_type_priority

Ranking Formula:
    Final Score = 0.35 similarity + 0.25 importance + 0.20 recency
                + 0.10 access_count + 0.10 memory_type_priority

Usage:
    engine = MemorySearchEngine(backend=my_backend)
    results = engine.search("محمد کیه؟")
    context = engine.get_relevant_context("Atlas OS")
"""

import time
import math
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend


# ═══════════════════════════════════════════════
#  WEIGHTS
# ═══════════════════════════════════════════════

DEFAULT_WEIGHTS = {
    "similarity": 0.35,
    "importance": 0.25,
    "recency": 0.20,
    "access_count": 0.10,
    "type_priority": 0.10,
}

# Memory type priorities (higher = more relevant)
TYPE_PRIORITIES = {
    "user": 1.0,
    "project": 0.9,
    "experience": 0.8,
    "knowledge": 0.7,
    "long": 0.9,
    "task": 0.6,
    "session": 0.4,
    "short": 0.2,
}

# Persian ↔ English synonym map (basic)
SYNONYMS = {
    "پروژه": ["project", "atlas"],
    "حافظه": ["memory", "remember"],
    "خطا": ["error", "bug", "issue"],
    "کاربر": ["user", "person"],
    "جستجو": ["search", "find"],
    "برنامه": ["code", "program", "python"],
    "سیستم": ["system", "os"],
    "هوش مصنوعی": ["ai", "artificial intelligence", "model"],
}


class MemorySearchEngine:
    """
    Intelligent search layer for Atlas OS memory.

    Goes beyond simple FTS by:
    1. Expanding queries with synonyms
    2. Ranking results by multiple factors
    3. Providing score breakdowns
    """

    def __init__(self, backend=None, weights=None):
        """
        Args:
            backend: MemoryBackend instance (for data access)
            weights: Custom ranking weights (optional)
        """
        self._backend = backend
        self._weights = weights or DEFAULT_WEIGHTS

    # ═══════════════════════════════════════════════
    #  MAIN SEARCH
    # ═══════════════════════════════════════════════

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search memory with intelligent ranking.

        Args:
            query:          Search query (Persian or English)
            memory_types:   Filter by memory types (optional)
            limit:          Max results
            min_importance: Minimum importance threshold

        Returns:
            List of dicts with:
                - record: MemoryRecord
                - score: float (0-1)
                - breakdown: dict of score components
        """
        # ── Step 1: Expand query with synonyms ──
        expanded_terms = self._expand_query(query)

        # ── Step 2: Search using FTS5 ──
        all_results = set()
        for term in expanded_terms:
            results = self._backend.search(
                query=term,
                memory_types=memory_types,
                limit=limit * 2,  # get more for ranking
                min_importance=min_importance,
            )
            for r in results:
                all_results.add(r.key)

        # Also search original query
        results = self._backend.search(
            query=query,
            memory_types=memory_types,
            limit=limit * 2,
            min_importance=min_importance,
        )
        for r in results:
            all_results.add(r.key)

        # ── Step 3: Fetch full records ──
        records = []
        for key in all_results:
            # Try to find in any memory type
            for mt in (memory_types or MEMORY_TYPES):
                rec = self._backend.get(mt, key)
                if rec is not None and not rec.is_expired():
                    records.append(rec)
                    break

        # ── Step 4: Rank results ──
        ranked = self._rank(query, records)

        # ── Step 5: Apply limit ──
        return ranked[:limit]

    # ═══════════════════════════════════════════════
    #  QUERY EXPANSION
    # ═══════════════════════════════════════════════

    def _expand_query(self, query: str) -> List[str]:
        """Expand query with synonyms."""
        terms = [query]
        query_lower = query.lower()

        for persian, english_list in SYNONYMS.items():
            if persian in query:
                terms.extend(english_list)
            for eng in english_list:
                if eng in query_lower:
                    terms.append(persian)
                    terms.extend([e for e in english_list if e != eng])
                    break

        return list(set(terms))

    # ═══════════════════════════════════════════════
    #  RANKING
    # ═══════════════════════════════════════════════

    def _rank(self, query: str, records: List[MemoryRecord]) -> List[Dict[str, Any]]:
        """Rank records by multiple factors."""
        now = time.time()
        results = []

        for record in records:
            # Calculate each component
            similarity = self._calc_similarity(query, record)
            importance = record.importance
            recency = self._calc_recency(record, now)
            access = self._calc_access_score(record)
            type_priority = TYPE_PRIORITIES.get(record.memory_type, 0.5)

            # Weighted sum
            total = (
                self._weights["similarity"] * similarity +
                self._weights["importance"] * importance +
                self._weights["recency"] * recency +
                self._weights["access_count"] * access +
                self._weights["type_priority"] * type_priority
            )

            results.append({
                "record": record,
                "score": round(total, 4),
                "breakdown": {
                    "similarity": round(similarity, 4),
                    "importance": round(importance, 4),
                    "recency": round(recency, 4),
                    "access_count": round(access, 4),
                    "type_priority": round(type_priority, 4),
                    "total": round(total, 4),
                },
            })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _calc_similarity(self, query: str, record: MemoryRecord) -> float:
        """Calculate text similarity between query and record."""
        query_words = set(query.lower().split())
        record_words = set(str(record.value).lower().split())
        record_words.update(record.key.lower().split("::")[-1].split("_"))

        if not query_words:
            return 0.0

        # Jaccard similarity
        intersection = query_words & record_words
        union = query_words | record_words

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # Boost for exact matches in value
        if query.lower() in str(record.value).lower():
            jaccard = min(1.0, jaccard + 0.3)

        # Boost for tag matches
        query_lower = query.lower()
        for tag in record.tags:
            if query_lower in tag.lower():
                jaccard = min(1.0, jaccard + 0.2)

        return min(1.0, jaccard)

    def _calc_recency(self, record: MemoryRecord, now: float) -> float:
        """Calculate recency score (more recent = higher)."""
        age_seconds = now - record.updated_at
        age_hours = age_seconds / 3600

        # Decay function: score = e^(-age_hours / 168)
        # 168 hours = 1 week half-life
        return math.exp(-age_hours / 168)

    def _calc_access_score(self, record: MemoryRecord) -> float:
        """Calculate access frequency score."""
        # Log scale: more access = higher score, but diminishing returns
        if record.access_count <= 0:
            return 0.0
        return min(1.0, math.log1p(record.access_count) / math.log1p(100))

    # ═══════════════════════════════════════════════
    #  CONTEXT EXPORT
    # ═══════════════════════════════════════════════

    def get_relevant_context(
        self,
        query: str,
        max_tokens: int = 1000,
        memory_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get relevant context for Brain prompt construction.

        Args:
            query:        What the Brain needs context for
            max_tokens:   Approximate token limit
            memory_types: Filter by types

        Returns:
            Dict with memories, total_count, query
        """
        results = self.search(query, memory_types=memory_types, limit=20)

        # Approximate token count (rough: 1 token ≈ 4 chars)
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
