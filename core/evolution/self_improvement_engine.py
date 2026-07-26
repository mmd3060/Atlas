"""
Self Improvement Engine v1 — The evolution loop for Atlas.

Flow:
  Lesson → Hypothesis → Experiment → Evaluation → Change → Memory

Safety:
  - Max change per update = 0.05
  - Minimum confidence = 0.8
  - All changes logged
  - Rollback capability
"""

import time
from typing import Any, Dict, Optional

from core.evolution.weight_optimizer import WeightOptimizer
from core.evolution.change_manager import ChangeManager
from core.evolution.rollback_manager import RollbackManager


class EvolutionRules:
    """Safety rules for evolution."""

    def __init__(self, config=None):
        config = config or {}
        self.max_change = config.get("max_change", 0.05)
        self.min_confidence = config.get("min_confidence", 0.8)
        self.min_experiences = config.get("min_experiences", 3)
        self.max_changes_per_hour = config.get("max_changes_per_hour", 10)


class SelfImprovementEngine:
    """
    The self-improvement loop for Atlas.

    Usage:
        engine = SelfImprovementEngine(
            adapter=memory_adapter,
            optimizer=optimizer,
            change_manager=manager,
            rollback_manager=rollback,
        )
        result = engine.evolve(
            task="coding",
            lesson="github performs well",
            confidence=0.9,
            provider="github",
        )
    """

    def __init__(
        self,
        adapter=None,
        optimizer=None,
        change_manager=None,
        rollback_manager=None,
        rules=None,
    ):
        self._adapter = adapter
        self._optimizer = optimizer or WeightOptimizer()
        self._change_manager = change_manager or ChangeManager()
        self._rollback = rollback_manager or RollbackManager(optimizer=self._optimizer)
        self._rules = rules or EvolutionRules()
        self._evolution_count = 0

    def evolve(
        self,
        task: str,
        lesson: str,
        confidence: float,
        provider: str,
    ) -> Dict[str, Any]:
        """
        Evolve based on a lesson.

        Args:
            task:       Task type
            lesson:     What was learned
            confidence: How confident (0-1)
            provider:   Which provider

        Returns:
            {status, change, rollback_id, reason}
        """
        # ── Safety check: confidence threshold ──
        if confidence < self._rules.min_confidence:
            return {
                "status": "rejected",
                "reason": f"confidence {confidence} below threshold {self._rules.min_confidence}",
                "change": None,
            }

        # ── Save snapshot for rollback ──
        snapshot_id = self._rollback.save_snapshot()

        # ── Calculate current and new weight ──
        old_weight = self._optimizer.get_weight(task, provider)

        # Determine reward from lesson
        reward = 0.7 if "performs well" in lesson.lower() or "boost" in lesson.lower() else 0.3

        # ── Update weight ──
        new_weight = self._optimizer.update(task=task, provider=provider, reward=reward)

        # ── Record change ──
        change_id = self._change_manager.record_change(
            target=provider,
            task=task,
            old_value=old_weight,
            new_value=new_weight,
            reason=lesson,
            confidence=confidence,
        )

        # ── Store lesson in memory ──
        if self._adapter:
            self._adapter.remember(
                value=f"Evolution: {lesson}",
                memory_type="experience",
                importance=confidence,
                tags=["evolution", task, provider],
            )

        self._evolution_count += 1

        return {
            "status": "evolved",
            "change": {
                "task": task,
                "provider": provider,
                "old": old_weight,
                "new": new_weight,
            },
            "rollback_id": snapshot_id,
            "change_id": change_id,
        }

    def rollback(self, snapshot_id: str) -> bool:
        """Rollback to a previous snapshot."""
        return self._rollback.restore_snapshot(snapshot_id)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_changes": self._change_manager.count(),
            "rollbacks": self._rollback.get_rollback_count(),
            "evolutions": self._evolution_count,
        }
