"""
Memory-aware Decision Engine v1 — Uses memory to improve model selection.

Before:
    decision = engine.decide(message)

After:
    decision = engine.decide(message, memory_context=context)

Memory signals:
  - User preferences → boost matching providers
  - Project context → task-specific adjustments
  - Previous failures → penalize failed providers
"""

from typing import Any, Dict, List, Optional

from core.decision.memory_signal import MemorySignal


class MemoryAwareEngine:
    """
    Enhances decision making with memory signals.

    Usage:
        engine = MemoryAwareEngine(adapter=memory_adapter)
        decision = engine.decide(
            message="کد Python بنویس",
            base_scores={"openrouter": 0.5, "gemini": 0.6},
        )
        # {provider, confidence, reasons, final_scores}
    """

    # Penalty for previous failures
    FAILURE_PENALTY = 0.15

    # Boost for matching user preferences
    PREFERENCE_BOOST = 0.1

    def __init__(self, adapter=None):
        self._signal = MemorySignal(adapter=adapter)

    def decide(
        self,
        message: str,
        base_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Make a memory-aware decision.

        Args:
            message:     User message
            base_scores: {provider: score} from base DecisionEngine

        Returns:
            {provider, confidence, reasons, final_scores}
        """
        # ── Extract memory signals ──
        signals = self._signal.extract(message)

        # ── Apply adjustments ──
        final_scores = dict(base_scores)
        reasons = []

        # Apply failure penalties
        for failure in signals["history"].get("failures", []):
            provider = failure["provider"]
            if provider in final_scores:
                final_scores[provider] = max(0, final_scores[provider] - self.FAILURE_PENALTY)
                reasons.append(f"penalized {provider} for previous failure")

        # Apply preference boosts
        prefs = signals["user_preferences"]
        if prefs.get("detail_level") == "high":
            for p in final_scores:
                if "openrouter" in p or "github" in p:
                    final_scores[p] = min(1.0, final_scores[p] + self.PREFERENCE_BOOST)
                    reasons.append(f"boosted {p} for detail preference")

        if prefs.get("language") == "fa":
            for p in final_scores:
                final_scores[p] = min(1.0, final_scores[p] + 0.02)
                reasons.append(f"Persian language context applied")

        # ── Select best provider ──
        best_provider = max(final_scores, key=final_scores.get)
        best_score = final_scores[best_provider]

        # ── Calculate confidence ──
        scores_sorted = sorted(final_scores.values(), reverse=True)
        if len(scores_sorted) >= 2:
            gap = scores_sorted[0] - scores_sorted[1]
            confidence = min(1.0, 0.5 + gap * 2)
        else:
            confidence = best_score

        return {
            "provider": best_provider,
            "confidence": round(confidence, 4),
            "reasons": reasons,
            "final_scores": {k: round(v, 4) for k, v in final_scores.items()},
        }
