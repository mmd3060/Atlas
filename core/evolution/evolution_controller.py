"""
Evolution Controller v2 — Orchestrates the full evolution cycle.

Flow:
  Observations → Hypothesis → Experiment → Evaluation → Adopt/Reject → Memory

Usage:
    controller = EvolutionController(adapter, optimizer, ...)
    result = controller.evolve(observations)
"""

from typing import Any, Dict, List, Optional

from core.evolution.hypothesis_engine import HypothesisEngine
from core.evolution.experiment_planner import ExperimentPlanner
from core.evolution.experiment_runner import ExperimentRunner
from core.evolution.evaluator import ExperimentEvaluator
from core.evolution.evolution_memory import EvolutionMemory


class EvolutionController:
    """
    Orchestrates the full evolution cycle.

    Usage:
        controller = EvolutionController(
            adapter=adapter,
            optimizer=optimizer,
        )
        result = controller.evolve(observations)
    """

    def __init__(
        self,
        adapter=None,
        optimizer=None,
        hypothesis_engine=None,
        planner=None,
        runner=None,
        evaluator=None,
        evolution_memory=None,
    ):
        self._adapter = adapter
        self._optimizer = optimizer
        self._hypothesis_engine = hypothesis_engine or HypothesisEngine()
        self._planner = planner or ExperimentPlanner()
        self._runner = runner or ExperimentRunner()
        self._evaluator = evaluator or ExperimentEvaluator()
        self._memory = evolution_memory or EvolutionMemory()

    def evolve(self, observations: List[Dict]) -> Dict[str, Any]:
        """
        Run a full evolution cycle.

        Args:
            observations: list of {task, provider, success}

        Returns:
            {hypothesis, plan, results, decision, change}
        """
        # ── Step 1: Generate hypothesis ──
        hypothesis = self._hypothesis_engine.generate(observations)

        if hypothesis["confidence"] < 0.3:
            return {
                "hypothesis": hypothesis,
                "plan": None,
                "results": None,
                "decision": {"verdict": "skip", "reason": "insufficient data"},
                "change": None,
            }

        # ── Step 2: Plan experiment ──
        plan = self._planner.plan(hypothesis)

        # ── Step 3: Run experiment ──
        results = self._runner.simulate(plan)

        # ── Step 4: Evaluate ──
        decision = self._evaluator.evaluate(results)

        # ── Step 5: Apply if adopted ──
        change = None
        if decision["verdict"] == "adopt" and self._optimizer and hypothesis.get("target"):
            target = hypothesis["target"]
            old_weight = self._optimizer.get_weight(target["task"], target["provider"])

            # Apply safe change
            improvement = decision.get("improvement", 0.05)
            new_weight = min(1.0, old_weight + min(0.05, improvement * 0.5))
            self._optimizer.set_weight(target["task"], target["provider"], new_weight)

            change = {
                "task": target["task"],
                "provider": target["provider"],
                "old": old_weight,
                "new": new_weight,
            }

            # Store in memory
            if self._adapter:
                self._adapter.remember(
                    value=f"Evolution: {hypothesis['statement']}",
                    memory_type="experience",
                    importance=hypothesis["confidence"],
                    tags=["evolution", "experiment"],
                )

        # ── Step 6: Record in evolution memory ──
        self._memory.record({
            "hypothesis": hypothesis.get("statement", ""),
            "verdict": decision.get("verdict", "unknown"),
            "confidence": hypothesis.get("confidence", 0),
            "change": change,
        })

        return {
            "hypothesis": hypothesis,
            "plan": plan,
            "results": results,
            "decision": decision,
            "change": change,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        return self._memory.get_stats()
