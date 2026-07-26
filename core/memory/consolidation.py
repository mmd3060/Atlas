"""
Memory Consolidation v1 — Like the human brain during sleep.

Consolidation converts short-term memories to long-term:
  1. Find short memories with high importance → promote
  2. Find duplicate memories → merge
  3. Find old/unimportant long memories → demote

Architecture:
    Short Memory → Consolidator → Long Memory
    Duplicates → Merge → Single Memory
    Old Long → Demote → Archive

Usage:
    consolidator = MemoryConsolidator(backend=sqlite_backend)
    result = consolidator.consolidate()
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend


# Default thresholds
DEFAULT_CONFIG = {
    "promotion_min_importance": 0.5,
    "demotion_max_importance": 0.4,
    "demotion_min_age_days": 7,
    "merge_similarity_threshold": 0.6,
    "max_short_memories": 100,
}


class MemoryConsolidator:
    """
    Consolidates memories like the human brain.

    Short-term → Long-term (promotion)
    Duplicates → Merged (merge)
    Old long → Archive (demotion)
    """

    def __init__(self, backend=None, config=None):
        """
        Args:
            backend: MemoryBackend instance
            config:  Custom thresholds (optional)
        """
        self._backend = backend
        self._config = config or DEFAULT_CONFIG

    # ═══════════════════════════════════════════════
    #  FULL CONSOLIDATION
    # ═══════════════════════════════════════════════

    def consolidate(self) -> Dict[str, Any]:
        """
        Run full consolidation cycle.

        Returns:
            {promoted: N, merged: N, demoted: N}
        """
        promoted = self._promote_eligible()
        merged = self._merge_duplicates()
        demoted = self._demote_old()

        return {
            "promoted": promoted,
            "merged": merged,
            "demoted": demoted,
            "timestamp": time.time(),
        }

    # ═══════════════════════════════════════════════
    #  PROMOTION
    # ═══════════════════════════════════════════════

    def find_promotion_candidates(
        self,
        min_importance: Optional[float] = None,
    ) -> List[MemoryRecord]:
        """
        Find short memories eligible for promotion to long-term.

        Criteria:
          - memory_type == "short"
          - importance >= threshold
        """
        threshold = min_importance or self._config["promotion_min_importance"]
        short_records = self._backend.list_records(memory_type="short", limit=1000)

        return [
            r for r in short_records
            if r.importance >= threshold and not r.is_expired()
        ]

    def promote(self, key: str, target_type: str = "long") -> Dict[str, Any]:
        """
        Promote a short memory to long-term.

        Args:
            key:          The memory key
            target_type:  Target memory type (default: long)

        Returns:
            {status, key, source_type, target_type}
        """
        record = self._backend.get("short", key)
        if record is None:
            return {"status": "not_found", "key": key}

        # Create new record in target type
        new_record = MemoryRecord(
            key=key,
            value=record.value,
            memory_type=target_type,
            importance=record.importance,
            tags=record.tags,
            source="consolidation_promote",
            metadata={**record.metadata, "promoted_from": "short", "promoted_at": time.time()},
        )
        self._backend.put(new_record)

        # Remove from short
        self._backend.delete("short", key)

        return {
            "status": "promoted",
            "key": key,
            "source_type": "short",
            "target_type": target_type,
        }

    def _promote_eligible(self) -> int:
        """Promote all eligible short memories."""
        candidates = self.find_promotion_candidates()
        count = 0
        for record in candidates:
            result = self.promote(record.key)
            if result["status"] == "promoted":
                count += 1
        return count

    # ═══════════════════════════════════════════════
    #  MERGE
    # ═══════════════════════════════════════════════

    def find_duplicates(self) -> List[List[str]]:
        """
        Find potential duplicate memories.

        Simple heuristic: same memory_type + similar value words.
        """
        all_records = self._backend.list_records(limit=1000)
        groups = {}

        for record in all_records:
            if record.is_expired():
                continue
            # Normalize value for comparison
            words = set(str(record.value).lower().split())
            # Create a simple fingerprint
            fingerprint = frozenset(words) if words else frozenset()

            if fingerprint not in groups:
                groups[fingerprint] = []
            groups[fingerprint].append(record.key)

        # Return groups with more than one member
        return [keys for keys in groups.values() if len(keys) > 1]

    def merge(
        self,
        key1: str,
        key2: str,
        target_type: str = "long",
    ) -> Dict[str, Any]:
        """
        Merge two memories into one.

        Keeps the one with higher importance, adds the other's value.
        """
        # Find records in any type
        rec1 = self._find_record(key1)
        rec2 = self._find_record(key2)

        if rec1 is None or rec2 is None:
            return {"status": "not_found", "key1": key1, "key2": key2}

        # Keep higher importance
        if rec1.importance >= rec2.importance:
            kept, removed = rec1, rec2
        else:
            kept, removed = rec2, rec1

        # Merge values
        merged_value = f"{kept.value} | {removed.value}"
        merged_tags = list(set(kept.tags + removed.tags))
        merged_metadata = {**kept.metadata, **removed.metadata, "merged_from": [key1, key2]}

        # Create merged record
        merged_record = MemoryRecord(
            key=kept.key,
            value=merged_value,
            memory_type=target_type,
            importance=max(kept.importance, removed.importance),
            tags=merged_tags,
            source="consolidation_merge",
            metadata=merged_metadata,
        )
        self._backend.put(merged_record)

        # Remove originals
        self._backend.delete(kept.memory_type, kept.key)
        self._backend.delete(removed.memory_type, removed.key)

        return {
            "status": "merged",
            "key": kept.key,
            "kept_importance": kept.importance,
            "removed_importance": removed.importance,
            "target_type": target_type,
        }

    def _find_record(self, key: str) -> Optional[MemoryRecord]:
        """Find a record by key across all types."""
        for mt in MEMORY_TYPES:
            record = self._backend.get(mt, key)
            if record is not None:
                return record
        return None

    def _merge_duplicates(self) -> int:
        """Merge all duplicate groups."""
        groups = self.find_duplicates()
        count = 0
        for keys in groups:
            if len(keys) >= 2:
                result = self.merge(keys[0], keys[1])
                if result["status"] == "merged":
                    count += 1
        return count

    # ═══════════════════════════════════════════════
    #  DEMOTION
    # ═══════════════════════════════════════════════

    def find_demotion_candidates(
        self,
        max_importance: Optional[float] = None,
        min_age_days: Optional[int] = None,
    ) -> List[MemoryRecord]:
        """
        Find long memories eligible for demotion.

        Criteria:
          - memory_type == "long"
          - importance <= threshold
          - age >= min_age_days
        """
        threshold = max_importance or self._config["demotion_max_importance"]
        min_age = min_age_days or self._config["demotion_min_age_days"]
        min_age_seconds = min_age * 86400

        long_records = self._backend.list_records(memory_type="long", limit=1000)
        now = time.time()

        return [
            r for r in long_records
            if r.importance <= threshold
            and (now - r.updated_at) >= min_age_seconds
            and not r.is_expired()
        ]

    def demote(self, key: str, target_type: str = "short") -> Dict[str, Any]:
        """
        Demote a long memory to short-term or archive.

        Args:
            key:          The memory key
            target_type:  Target type (default: short)

        Returns:
            {status, key, source_type, target_type}
        """
        record = self._backend.get("long", key)
        if record is None:
            return {"status": "not_found", "key": key}

        # Create new record in target type
        new_record = MemoryRecord(
            key=key,
            value=record.value,
            memory_type=target_type,
            importance=record.importance,
            tags=record.tags,
            source="consolidation_demote",
            metadata={**record.metadata, "demoted_from": "long", "demoted_at": time.time()},
        )
        self._backend.put(new_record)

        # Remove from long
        self._backend.delete("long", key)

        return {
            "status": "demoted",
            "key": key,
            "source_type": "long",
            "target_type": target_type,
        }

    def _demote_old(self) -> int:
        """Demote all eligible long memories."""
        candidates = self.find_demotion_candidates()
        count = 0
        for record in candidates:
            result = self.demote(record.key)
            if result["status"] == "demoted":
                count += 1
        return count

    # ═══════════════════════════════════════════════
    #  STATS
    # ═══════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics."""
        counts = {}
        for mt in MEMORY_TYPES:
            counts[mt] = self._backend.count(mt)

        return {
            "short_count": counts.get("short", 0),
            "long_count": counts.get("long", 0),
            "session_count": counts.get("session", 0),
            "total_count": sum(counts.values()),
            "by_type": counts,
        }
