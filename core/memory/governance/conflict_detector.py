"""
Conflict Detector — Finds contradictory memories.
"""


from typing import Any, Dict, List


class ConflictDetector:
    """
    Detects conflicts between memories.

    A conflict exists when:
      - Same key, different values
      - Same topic, contradictory information
    """

    def has_conflict(self, mem1: Dict, mem2: Dict) -> bool:
        """
        Check if two memories conflict.

        Conflict = same key but different value.
        """
        if mem1.get("key") != mem2.get("key"):
            return False

        return str(mem1.get("value", "")).strip() != str(mem2.get("value", "")).strip()

    def find_conflicts(self, memories: List[Dict]) -> List[Dict]:
        """
        Find all conflicts in a list of memories.

        Returns:
            List of {memory1, memory2, key, conflict_type}
        """
        conflicts = []
        seen = set()

        for i, m1 in enumerate(memories):
            for m2 in memories[i+1:]:
                if self.has_conflict(m1, m2):
                    pair_key = tuple(sorted([
                        (m1.get("key", ""), m1.get("value", "")),
                        (m2.get("key", ""), m2.get("value", "")),
                    ]))
                    if pair_key not in seen:
                        seen.add(pair_key)
                        conflicts.append({
                            "memory1": m1,
                            "memory2": m2,
                            "key": m1.get("key"),
                            "conflict_type": "value_changed",
                        })

        return conflicts

    def resolve_conflict(self, mem1: Dict, mem2: Dict, strategy: str = "newest") -> Dict:
        """
        Resolve a conflict between two memories.

        Strategies:
          - newest: keep the more recent one
          - highest_importance: keep the one with higher importance
          - merged: combine values
        """
        if strategy == "highest_importance":
            if mem1.get("importance", 0) >= mem2.get("importance", 0):
                return mem1
            return mem2
        elif strategy == "merged":
            return {
                "key": mem1.get("key"),
                "value": f"{mem1.get('value', '')} → {mem2.get('value', '')}",
                "importance": max(mem1.get("importance", 0), mem2.get("importance", 0)),
            }
        else:  # newest
            if mem1.get("updated_at", 0) >= mem2.get("updated_at", 0):
                return mem1
            return mem2
