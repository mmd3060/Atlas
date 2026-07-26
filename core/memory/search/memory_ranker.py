"""
Memory Ranker — Multi-factor ranking for search results.

Ranking Formula:
    Final Score = 0.35 similarity + 0.25 importance + 0.20 recency
                + 0.10 access_count + 0.10 memory_type_priority

Responsibilities:
  - Calculate similarity score
  - Calculate importance score
  - Calculate recency score
  - Calculate access frequency score
  - Combine into final score
  - Sort results

Does NOT:
  - Search (KeywordSearch does that)
  - Parse queries (QueryParser does that)
"""

import math
import time
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES


# Default weights
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


class MemoryRanker:
    """
    Multi-factor ranking for memory search results.

    Usage:
        ranker = MemoryRanker()
        ranked = ranker.rank(query="Atlas", records=records)
    """

    def __init__(self, weights=None, type_priorities=None):
        """
        Args:
            weights: Custom ranking weights (optional)
            type_priorities: Custom type priorities (optional)
        """
        self._weights = weights or DEFAULT_WEIGHTS
        self._type_priorities = type_priorities or TYPE_PRIORITIES

    def rank(
        self,
        query: str,
        records: List[MemoryRecord],
    ) -> List[Dict[str, Any]]:
        """
        Rank records by multiple factors.

        Args:
            query:   Original search query
            records: List of MemoryRecord to rank

        Returns:
            List of dicts with record, score, and breakdown
        """
        now = time.time()
        results = []

        for record in records:
            score_data = self._score_one(query, record, now)
            results.append(score_data)

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _score_one(
        self,
        query: str,
        record: MemoryRecord,
        now: float,
    ) -> Dict[str, Any]:
        """Score a single record."""
        similarity = self._calc_similarity(query, record)
        importance = record.importance
        recency = self._calc_recency(record, now)
        access = self._calc_access_score(record)
        type_priority = self._type_priorities.get(record.memory_type, 0.5)

        total = (
            self._weights["similarity"] * similarity +
            self._weights["importance"] * importance +
            self._weights["recency"] * recency +
            self._weights["access_count"] * access +
            self._weights["type_priority"] * type_priority
        )

        return {
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
        }

    def _calc_similarity(self, query: str, record: MemoryRecord) -> float:
        """Calculate text similarity (Jaccard + boosts)."""
        query_words = set(query.lower().split())
        record_words = set(str(record.value).lower().split())
        record_words.update(record.key.lower().split("::")[-1].split("_"))

        if not query_words:
            return 0.0

        intersection = query_words & record_words
        union = query_words | record_words

        if not union:
            return 0.0

        jaccard = len(intersection) / len(union)

        # Boost for exact match in value
        if query.lower() in str(record.value).lower():
            jaccard = min(1.0, jaccard + 0.3)

        # Boost for tag matches
        query_lower = query.lower()
        for tag in record.tags:
            if query_lower in tag.lower():
                jaccard = min(1.0, jaccard + 0.2)

        return min(1.0, jaccard)

    def _calc_recency(self, record: MemoryRecord, now: float) -> float:
        """Calculate recency score (exponential decay)."""
        age_seconds = now - record.updated_at
        age_hours = age_seconds / 3600
        # 1-week half-life
        return math.exp(-age_hours / 168)

    def _calc_access_score(self, record: MemoryRecord) -> float:
        """Calculate access frequency score (log scale)."""
        if record.access_count <= 0:
            return 0.0
        return min(1.0, math.log1p(record.access_count) / math.log1p(100))
