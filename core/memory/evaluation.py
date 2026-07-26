"""
Memory Evaluation v1 — Analyzes memory quality and provides insights.

Responsibilities:
  - Evaluate individual memory quality
  - Detect potential duplicates
  - Generate quality distribution
  - Provide actionable recommendations
  - Calculate health statistics

Does NOT:
  - Modify memories (Consolidator does that)
  - Search (SearchEngine does that)
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend


class MemoryEvaluator:
    """
    Evaluates memory quality and provides insights.

    Usage:
        evaluator = MemoryEvaluator(backend=sqlite_backend)
        report = evaluator.evaluate()
    """

    def __init__(self, backend=None):
        self._backend = backend

    # ═══════════════════════════════════════════════
    #  SINGLE MEMORY EVALUATION
    # ═══════════════════════════════════════════════

    def evaluate_memory(self, memory_type: str, key: str) -> Dict[str, Any]:
        """
        Evaluate quality of a single memory.

        Returns:
            {score, factors, quality_level}
        """
        record = self._backend.get(memory_type, key)
        if record is None:
            return {"score": 0.0, "factors": {}, "quality_level": "none"}

        factors = self._calculate_factors(record)
        score = sum(factors.values())

        return {
            "score": round(score, 4),
            "factors": factors,
            "quality_level": self._quality_level(score),
            "record": record,
        }

    def _calculate_factors(self, record: MemoryRecord) -> Dict[str, float]:
        """Calculate quality factors for a record."""
        now = time.time()

        # Factor 1: Importance (0.3 weight)
        importance = record.importance * 0.3

        # Factor 2: Access frequency (0.25 weight)
        access = min(1.0, record.access_count / 10) * 0.25

        # Factor 3: Recency (0.25 weight)
        age_hours = (now - record.updated_at) / 3600
        recency = max(0, 1.0 - age_hours / 168) * 0.25

        # Factor 4: Content quality (0.2 weight)
        content = self._content_quality(record) * 0.2

        return {
            "importance": round(importance, 4),
            "access": round(access, 4),
            "recency": round(recency, 4),
            "content": round(content, 4),
        }

    def _content_quality(self, record: MemoryRecord) -> float:
        """Assess content quality based on heuristics."""
        value = str(record.value)
        score = 0.5

        # Length bonus (not too short, not too long)
        if 10 < len(value) < 500:
            score += 0.2
        elif len(value) <= 10:
            score -= 0.2

        # Tag bonus
        if record.tags:
            score += 0.1

        # Metadata bonus
        if record.metadata:
            score += 0.1

        # Source bonus
        if record.source and record.source not in ("unknown", "temp"):
            score += 0.1

        return min(1.0, max(0.0, score))

    def _quality_level(self, score: float) -> str:
        """Convert score to quality level."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"

    # ═══════════════════════════════════════════════
    #  FULL EVALUATION
    # ═══════════════════════════════════════════════

    def evaluate(self) -> Dict[str, Any]:
        """Full evaluation of all memories."""
        all_records = self._backend.list_records(limit=10000)
        by_type = {}
        scores = []

        for record in all_records:
            if record.is_expired():
                continue
            if record.memory_type not in by_type:
                by_type[record.memory_type] = []
            quality = self.evaluate_memory(record.memory_type, record.key)
            by_type[record.memory_type].append(quality)
            scores.append(quality["score"])

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_count": len(scores),
            "avg_quality": round(avg_score, 4),
            "by_type": {
                mt: {
                    "count": len(quals),
                    "avg_quality": round(sum(q["score"] for q in quals) / len(quals), 4) if quals else 0,
                }
                for mt, quals in by_type.items()
            },
            "quality_distribution": self.get_quality_distribution(),
            "recommendations": self.get_recommendations(),
        }

    # ═══════════════════════════════════════════════
    #  DUPLICATE DETECTION
    # ═══════════════════════════════════════════════

    def find_duplicates(self, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Find potential duplicate memories using similarity."""
        import re
        all_records = self._backend.list_records(limit=10000)
        valid = [r for r in all_records if not r.is_expired()]
        duplicates = []
        seen = set()

        for i, r1 in enumerate(valid):
            if r1.key in seen:
                continue
            words1 = self._normalize_words(r1.value)
            similar_group = [r1]

            for r2 in valid[i+1:]:
                if r2.key in seen:
                    continue
                words2 = self._normalize_words(r2.value)
                sim = self._jaccard(words1, words2)
                if sim >= threshold:
                    similar_group.append(r2)
                    seen.add(r2.key)

            if len(similar_group) > 1:
                seen.add(r1.key)
                duplicates.append({
                    "keys": [r.key for r in similar_group],
                    "types": [r.memory_type for r in similar_group],
                    "values": [str(r.value)[:50] for r in similar_group],
                })

        return duplicates

    def _normalize_words(self, text) -> set:
        """Normalize text to a set of words."""
        import re
        stop_words = {
            'یک', 'است', 'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با',
            'a', 'the', 'is', 'and', 'or', 'in', 'at', 'to', 'of',
        }
        value = str(text).lower()
        value = re.sub(r'[^\w\s]', ' ', value)
        return set(value.split()) - stop_words

    def _jaccard(self, s1: set, s2: set) -> float:
        """Jaccard similarity between two sets."""
        if not s1 or not s2:
            return 0.0
        intersection = s1 & s2
        union = s1 | s2
        return len(intersection) / len(union) if union else 0.0

    # ═══════════════════════════════════════════════
    #  QUALITY DISTRIBUTION
    # ═══════════════════════════════════════════════

    def get_quality_distribution(self) -> Dict[str, int]:
        """Get count of memories per quality level."""
        all_records = self._backend.list_records(limit=10000)
        dist = {"high": 0, "medium": 0, "low": 0}

        for record in all_records:
            if record.is_expired():
                continue
            quality = self.evaluate_memory(record.memory_type, record.key)
            level = quality["quality_level"]
            if level in dist:
                dist[level] += 1

        return dist

    # ═══════════════════════════════════════════════
    #  RECOMMENDATIONS
    # ═══════════════════════════════════════════════

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        all_records = self._backend.list_records(limit=10000)
        now = time.time()

        for record in all_records:
            if record.is_expired():
                continue

            quality = self.evaluate_memory(record.memory_type, record.key)

            # Recommendation: promote high-quality short memories
            if (record.memory_type == "short"
                    and quality["score"] >= 0.6
                    and record.importance >= 0.5):
                recommendations.append({
                    "action": "promote",
                    "key": record.key,
                    "reason": "High quality short memory",
                    "score": quality["score"],
                })

            # Recommendation: demote old low-quality long memories
            elif (record.memory_type == "long"
                  and quality["score"] < 0.3
                  and (now - record.updated_at) > 86400 * 7):
                recommendations.append({
                    "action": "demote",
                    "key": record.key,
                    "reason": "Old low-quality long memory",
                    "score": quality["score"],
                })

            # Recommendation: review memories with no access
            elif record.access_count == 0 and record.memory_type != "short":
                recommendations.append({
                    "action": "review",
                    "key": record.key,
                    "reason": "Never accessed",
                    "score": quality["score"],
                })

        return recommendations

    # ═══════════════════════════════════════════════
    #  STATS
    # ═══════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        all_records = self._backend.list_records(limit=10000)
        now = time.time()
        total = len(all_records)
        ages = []

        for record in all_records:
            if not record.is_expired():
                ages.append(now - record.updated_at)

        avg_age_hours = (sum(ages) / len(ages) / 3600) if ages else 0
        oldest_hours = (max(ages) / 3600) if ages else 0

        return {
            "total": total,
            "avg_quality": self._calc_avg_quality(all_records),
            "oldest_hours": round(oldest_hours, 2),
            "avg_age_hours": round(avg_age_hours, 2),
        }

    def _calc_avg_quality(self, records) -> float:
        """Calculate average quality across all records."""
        scores = []
        for record in records:
            if not record.is_expired():
                quality = self.evaluate_memory(record.memory_type, record.key)
                scores.append(quality["score"])
        return round(sum(scores) / len(scores), 4) if scores else 0.0
