"""
Rollback Manager — Save and restore weight snapshots.
"""

import time
import uuid
from typing import Any, Dict, Optional


class RollbackManager:
    """
    Save and restore weight snapshots for rollback.

    Usage:
        rollback = RollbackManager(optimizer=optimizer)
        snapshot_id = rollback.save_snapshot()
        # ... make changes ...
        rollback.restore_snapshot(snapshot_id)
    """

    def __init__(self, optimizer=None):
        self._optimizer = optimizer
        self._snapshots: Dict[str, Dict] = {}
        self._rollback_count = 0

    def save_snapshot(self) -> str:
        """Save current weights and return snapshot_id."""
        snapshot_id = str(uuid.uuid4())[:8]
        import copy
        self._snapshots[snapshot_id] = {
            "weights": copy.deepcopy(self._optimizer.get_all_weights()),
            "timestamp": time.time(),
        }
        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore weights from snapshot."""
        if snapshot_id not in self._snapshots:
            return False

        snapshot = self._snapshots[snapshot_id]
        for task, providers in snapshot["weights"].items():
            for provider, weight in providers.items():
                self._optimizer.set_weight(task, provider, weight)

        self._rollback_count += 1
        return True

    def get_rollback_count(self) -> int:
        return self._rollback_count

    def list_snapshots(self) -> Dict[str, Dict]:
        return dict(self._snapshots)
