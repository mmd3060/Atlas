"""
Memory Governance v1 — Decision layer for memory actions.

Architecture:
    Memory Evaluation → Governance → Action
                              ├── KEEP
                              ├── PROMOTE
                              ├── ARCHIVE
                              ├── DELETE
                              └── CONFLICT

Usage:
    gov = MemoryGovernance()
    decision = gov.evaluate(importance=0.9, quality=0.9, confidence=0.8)
    # {action: "keep", confidence: 0.92, reason: "high quality memory"}
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.governance.rules import GovernanceRules
from core.memory.governance.conflict_detector import ConflictDetector


class MemoryGovernance:
    """
    Decides what to do with each memory based on quality metrics.
    """

    def __init__(self, rules=None):
        self._rules = rules or GovernanceRules()
        self._conflict_detector = ConflictDetector()

    def evaluate(
        self,
        importance: float = 0.5,
        quality: float = 0.5,
        confidence: float = 0.5,
        access_count: int = 0,
        age_days: int = 0,
        is_duplicate: bool = False,
        is_corrupted: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluate a memory and decide an action.

        Returns:
            {action, confidence, reason, factors}
        """
        # ── Priority 1: Delete corrupted/duplicate ──
        if is_corrupted:
            return self._decision("delete", confidence=1.0, reason="corrupted memory")
        if is_duplicate:
            return self._decision("delete", confidence=0.9, reason="duplicate memory")

        # ── Calculate composite score ──
        composite = self._composite_score(importance, quality, confidence, access_count)

        # ── Priority 2: Promote high-value memories ──
        if (importance >= self._rules.promote_threshold
                and quality >= self._rules.promote_threshold
                and confidence >= self._rules.confidence_threshold
                and access_count >= 5):
            return self._decision(
                "promote",
                confidence=composite,
                reason="high importance + high quality + frequently accessed",
            )

        # ── Priority 3: Archive low-value old memories ──
        if (quality <= self._rules.archive_max_quality
                and confidence <= self._rules.archive_max_confidence
                and age_days >= self._rules.archive_min_age_days):
            return self._decision(
                "archive",
                confidence=composite,
                reason="low quality + low confidence + old memory",
            )

        # ── Priority 4: Keep everything else ──
        if quality >= self._rules.quality_threshold and confidence >= self._rules.confidence_threshold:
            return self._decision(
                "keep",
                confidence=composite,
                reason="meets quality and confidence thresholds",
            )

        # ── Default: archive borderline memories ──
        return self._decision(
            "archive",
            confidence=composite,
            reason="below quality/confidence thresholds",
        )

    def evaluate_batch(self, memories: List[Dict]) -> List[Dict]:
        """Evaluate a batch of memories."""
        return [
            self.evaluate(
                importance=m.get("importance", 0.5),
                quality=m.get("quality", 0.5),
                confidence=m.get("confidence", 0.5),
                access_count=m.get("access_count", 0),
                age_days=m.get("age_days", 0),
                is_duplicate=m.get("is_duplicate", False),
                is_corrupted=m.get("is_corrupted", False),
            )
            for m in memories
        ]

    def get_stats(self, decisions: List[Dict]) -> Dict[str, int]:
        """Get statistics from a list of decisions."""
        stats = {"keep": 0, "promote": 0, "archive": 0, "delete": 0, "conflict": 0}
        for d in decisions:
            action = d.get("action", "unknown")
            if action in stats:
                stats[action] += 1
        return stats

    @property
    def conflicts(self):
        return self._conflict_detector

    def _composite_score(self, importance, quality, confidence, access_count):
        """Calculate composite governance score."""
        access_score = min(1.0, access_count / 10)
        return round(
            0.30 * importance
            + 0.30 * quality
            + 0.25 * confidence
            + 0.15 * access_score,
            4,
        )

    def _decision(self, action, confidence, reason):
        return {
            "action": action,
            "confidence": round(confidence, 4),
            "reason": reason,
        }
