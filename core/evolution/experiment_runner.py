"""
Experiment Runner — Simulates or runs experiments.

Usage:
    runner = ExperimentRunner()
    results = runner.simulate(plan)
    # {control: {success_rate}, variant: {success_rate}}
"""

import random
from typing import Any, Dict


class ExperimentRunner:
    """
    Simulates experiments for testing.

    Usage:
        runner = ExperimentRunner()
        results = runner.simulate(plan)
    """

    def simulate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an experiment.

        Args:
            plan: {sample_size, control, variant}

        Returns:
            {control: {success_rate, total, successes}, variant: {...}}
        """
        sample_size = plan.get("sample_size", 20)
        half = sample_size // 2

        # Simulate control (current best)
        control_successes = random.randint(half // 2, half)
        control_rate = control_successes / half if half > 0 else 0

        # Simulate variant (proposed better)
        # Variant should be slightly better if hypothesis is correct
        variant_successes = random.randint(half // 2, half)
        variant_rate = variant_successes / half if half > 0 else 0

        return {
            "control": {
                "provider": plan.get("control", {}).get("provider", "unknown"),
                "success_rate": round(control_rate, 4),
                "total": half,
                "successes": control_successes,
            },
            "variant": {
                "provider": plan.get("variant", {}).get("provider", "unknown"),
                "success_rate": round(variant_rate, 4),
                "total": half,
                "successes": variant_successes,
            },
        }

    def run(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for simulate (for real experiments later)."""
        return self.simulate(plan)
