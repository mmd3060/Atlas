"""
Change Manager — Records all changes for audit trail.
"""

import time
import uuid
from typing import Any, Dict, List, Optional


class ChangeManager:
    """
    Records all weight changes for audit and rollback.

    Usage:
        manager = ChangeManager()
        change_id = manager.record_change(
            target="github", task="coding",
            old_value=0.5, new_value=0.55,
            reason="high success rate", confidence=0.85,
        )
    """

    def __init__(self):
        self._changes: List[Dict[str, Any]] = []

    def record_change(
        self,
        target: str,
        task: str,
        old_value: float,
        new_value: float,
        reason: str,
        confidence: float,
    ) -> str:
        """Record a change and return change_id."""
        change_id = str(uuid.uuid4())[:8]
        self._changes.append({
            "id": change_id,
            "target": target,
            "task": task,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
            "confidence": confidence,
            "timestamp": time.time(),
        })
        return change_id

    def get_changes(self, task: Optional[str] = None) -> List[Dict]:
        """Get recorded changes."""
        if task:
            return [c for c in self._changes if c["task"] == task]
        return list(self._changes)

    def get_change(self, change_id: str) -> Optional[Dict]:
        """Get a specific change by id."""
        for c in self._changes:
            if c["id"] == change_id:
                return c
        return None

    def count(self) -> int:
        return len(self._changes)
