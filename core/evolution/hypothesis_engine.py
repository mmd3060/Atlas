"""
Hypothesis Engine — Generates hypotheses from observations.

Usage:
    engine = HypothesisEngine()
    hypothesis = engine.generate(observations)
    # {statement, confidence, target, evidence}
"""

from typing import Any, Dict, List


class HypothesisEngine:
    """
    Generates hypotheses from observations.

    Usage:
        engine = HypothesisEngine()
        hypothesis = engine.generate(observations)
    """

    def generate(self, observations: List[Dict]) -> Dict[str, Any]:
        """
        Generate a hypothesis from observations.

        Args:
            observations: list of {task, provider, success}

        Returns:
            {statement, confidence, target, evidence}
        """
        if not observations:
            return {"statement": "no data", "confidence": 0, "target": None, "evidence": []}

        # Group by task and provider
        stats = {}
        for obs in observations:
            task = obs.get("task", "unknown")
            provider = obs.get("provider", "unknown")
            success = obs.get("success", False)

            key = (task, provider)
            if key not in stats:
                stats[key] = {"total": 0, "successes": 0}
            stats[key]["total"] += 1
            if success:
                stats[key]["successes"] += 1

        # Find best provider per task
        tasks = {}
        for (task, provider), s in stats.items():
            if task not in tasks:
                tasks[task] = {}
            rate = s["successes"] / s["total"] if s["total"] > 0 else 0
            tasks[task][provider] = {"rate": rate, "count": s["total"]}

        # Generate hypothesis for first task
        for task, providers in tasks.items():
            if len(providers) < 2:
                continue

            sorted_providers = sorted(providers.items(), key=lambda x: x[1]["rate"], reverse=True)
            best = sorted_providers[0]
            worst = sorted_providers[-1]

            if best[1]["rate"] > worst[1]["rate"]:
                confidence = min(0.95, 0.5 + (best[1]["rate"] - worst[1]["rate"]) * 0.5)
                return {
                    "statement": f"{best[0]} performs better than {worst[0]} for {task}",
                    "confidence": round(confidence, 4),
                    "target": {"task": task, "provider": best[0]},
                    "evidence": [
                        {"provider": best[0], "rate": round(best[1]["rate"], 4)},
                        {"provider": worst[0], "rate": round(worst[1]["rate"], 4)},
                    ],
                }

        return {"statement": "insufficient data", "confidence": 0, "target": None, "evidence": []}
