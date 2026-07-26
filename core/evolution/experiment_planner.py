"""
Experiment Planner — Designs experiments to test hypotheses.

Usage:
    planner = ExperimentPlanner()
    plan = planner.plan(hypothesis)
    # {sample_size, control, variant, duration}
"""

from typing import Any, Dict


class ExperimentPlanner:
    """
    Designs experiments to test hypotheses.

    Usage:
        planner = ExperimentPlanner()
        plan = planner.plan(hypothesis)
    """

    MIN_SAMPLE = 10
    MAX_SAMPLE = 100

    def plan(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an experiment plan from a hypothesis.

        Args:
            hypothesis: {statement, confidence, target, evidence}

        Returns:
            {sample_size, control, variant, duration}
        """
        confidence = hypothesis.get("confidence", 0.5)
        target = hypothesis.get("target", {})

        # Sample size based on confidence
        # Higher confidence → smaller sample needed
        if confidence >= 0.8:
            sample_size = 15
        elif confidence >= 0.6:
            sample_size = 25
        else:
            sample_size = 40

        sample_size = max(self.MIN_SAMPLE, min(self.MAX_SAMPLE, sample_size))

        # Control = current best provider
        # Variant = proposed better provider
        evidence = hypothesis.get("evidence", [])
        if len(evidence) >= 2:
            control_provider = evidence[0]["provider"]
            variant_provider = evidence[1]["provider"]
        else:
            control_provider = "current"
            variant_provider = target.get("provider", "alternative")

        return {
            "sample_size": sample_size,
            "control": {"provider": control_provider, "ratio": 0.5},
            "variant": {"provider": variant_provider, "ratio": 0.5},
            "duration": "until_sample_complete",
            "task": target.get("task", "unknown"),
        }
