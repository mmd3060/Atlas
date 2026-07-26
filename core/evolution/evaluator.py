"""
Experiment Evaluator — Compares experiment results and decides adopt/reject.

Usage:
    evaluator = ExperimentEvaluator()
    decision = evaluator.evaluate(results)
    # {verdict, confidence, reason}
"""

from typing import Any, Dict


class ExperimentEvaluator:
    """
    Evaluates experiment results.

    Usage:
        evaluator = ExperimentEvaluator()
        decision = evaluator.evaluate(results)
    """

    MIN_IMPROVEMENT = 0.05  # 5% minimum improvement to adopt

    def evaluate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate experiment results.

        Args:
            results: {control: {success_rate}, variant: {success_rate}}

        Returns:
            {verdict, confidence, reason, improvement}
        """
        control_rate = results.get("control", {}).get("success_rate", 0)
        variant_rate = results.get("variant", {}).get("success_rate", 0)

        improvement = variant_rate - control_rate

        if improvement >= self.MIN_IMPROVEMENT:
            confidence = min(0.95, 0.5 + improvement * 2)
            return {
                "verdict": "adopt",
                "confidence": round(confidence, 4),
                "reason": f"variant improved by {improvement:.1%}",
                "improvement": round(improvement, 4),
            }
        elif improvement <= -self.MIN_IMPROVEMENT:
            return {
                "verdict": "reject",
                "confidence": 0.7,
                "reason": f"variant performed worse by {abs(improvement):.1%}",
                "improvement": round(improvement, 4),
            }
        else:
            return {
                "verdict": "reject",
                "confidence": 0.5,
                "reason": f"no significant improvement ({improvement:.1%})",
                "improvement": round(improvement, 4),
            }
