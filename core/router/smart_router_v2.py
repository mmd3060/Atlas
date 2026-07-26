"""
Smart Router v2 — Selects the BEST MODEL for each task.

Flow:
  Input → Task Classifier → Score Models → Select Best

Scoring:
  Final Score = Task Match + Quality + Speed + Cost + Memory

Usage:
    router = SmartRouterV2(registry=registry)
    result = router.route("کد Python بنویس")
    # {model, provider, score, reasons, alternatives}
"""

from typing import Any, Dict, List, Optional

from core.router.model_registry import ModelRegistry
from core.router.task_classifier import TaskClassifier


class SmartRouterV2:
    """
    Smart Router that selects models based on task requirements.
    """

    # Scoring weights
    TASK_WEIGHT = 0.40
    QUALITY_WEIGHT = 0.25
    SPEED_WEIGHT = 0.15
    COST_WEIGHT = 0.10
    MEMORY_WEIGHT = 0.10

    def __init__(self, registry=None, adapter=None):
        self._registry = registry or ModelRegistry()
        self._classifier = TaskClassifier()
        self._adapter = adapter

    def route(
        self,
        message: str,
        exclude: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Route a message to the best model.

        Args:
            message: User message
            exclude: Model names to exclude (failover)

        Returns:
            {model, provider, score, reasons, alternatives}
        """
        exclude = exclude or []

        # ── Step 1: Classify task ──
        task = self._classifier.classify(message)
        task_type = task["type"]

        # ── Step 2: Score all models ──
        scores = self.score_models(message, exclude=exclude)

        if not scores:
            return {
                "model": "llama-3.3-70b",
                "provider": "openrouter",
                "score": 0.5,
                "reasons": ["fallback: no models available"],
                "alternatives": [],
            }

        # ── Step 3: Select best ──
        sorted_models = sorted(scores.items(), key=lambda x: x[1]["total"], reverse=True)
        best_name, best_data = sorted_models[0]

        # ── Step 4: Get alternatives ──
        alternatives = [
            {"model": name, "score": data["total"]}
            for name, data in sorted_models[1:3]
        ]

        return {
            "model": best_name,
            "provider": best_data["provider"],
            "score": round(best_data["total"], 4),
            "reasons": best_data["reasons"],
            "alternatives": alternatives,
        }

    def score_models(
        self,
        message: str,
        exclude: Optional[List[str]] = None,
    ) -> Dict[str, Dict]:
        """
        Score all models for a message.

        Returns:
            {model_name: {total, provider, reasons}}
        """
        exclude = exclude or []
        task = self._classifier.classify(message)
        task_type = task["type"]

        scores = {}
        for model in self._registry.get_all():
            if model.name in exclude:
                continue

            # ── Task match score ──
            task_attr = {
                "code": "coding",
                "coding": "coding",
                "math": "math",
                "text": "text",
                "writing": "text",
                "analysis": "reasoning",
            }.get(task_type, "reasoning")
            task_score = getattr(model, task_attr, 0.5)

            # ── Quality (average of capabilities) ──
            quality = (model.coding + model.reasoning + model.math + model.text) / 4

            # ── Speed ──
            speed = model.speed

            # ── Cost (higher = cheaper = better) ──
            cost = model.cost

            # ── Memory bonus ──
            memory_bonus = 0.0
            reasons = []

            if task["language"] == "fa" and "gemini" in model.name:
                memory_bonus = 0.05
                reasons.append("Persian language bonus")

            # ── Final score ──
            total = (
                task_score * self.TASK_WEIGHT +
                quality * self.QUALITY_WEIGHT +
                speed * self.SPEED_WEIGHT +
                cost * self.COST_WEIGHT +
                memory_bonus
            )

            reasons.append(f"task_match={task_score:.2f}")
            reasons.append(f"quality={quality:.2f}")

            scores[model.name] = {
                "total": round(total, 4),
                "provider": model.provider,
                "reasons": reasons,
            }

        return scores
