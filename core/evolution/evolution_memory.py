"""
Evolution Memory — Stores evolution history for pattern analysis.

Usage:
    memory = EvolutionMemory()
    memory.record({hypothesis, verdict, confidence, change})
    history = memory.get_history()
"""

from typing import Any, Dict, List, Optional


class EvolutionMemory:
    """
    Stores evolution history.

    Usage:
        memory = EvolutionMemory()
        memory.record({...})
        history = memory.get_history()
    """

    def __init__(self):
        self._records: List[Dict] = []

    def record(self, data: Dict[str, Any]):
        """Record an evolution event."""
        import time
        self._records.append({**data, "timestamp": time.time()})

    def get_history(self, task: Optional[str] = None) -> List[Dict]:
        """Get evolution history."""
        if task:
            return [r for r in self._records if task in str(r)]
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def get_stats(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        total = len(self._records)
        adopts = sum(1 for r in self._records if r.get("verdict") == "adopt")
        rejects = sum(1 for r in self._records if r.get("verdict") == "reject")
        return {
            "total": total,
            "adopts": adopts,
            "rejects": rejects,
            "adoption_rate": round(adopts / total, 4) if total > 0 else 0,
        }
