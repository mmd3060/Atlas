"""
Self-Improvement Loop v2 — Autonomous evolution controller.

Replaces passive learning with active experimentation.

Flow:
  Observe → Reflect → Hypothesize → Experiment → Evaluate → Adopt/Reject
"""

import time
from typing import Any, Dict, List, Optional
from core.evolution.weight_optimizer import WeightOptimizer
from core.evolution.hypothesis_engine import HypothesisEngine
from core.evolution.evaluator import ExperimentEvaluator
from core.evolution.evolution_memory import EvolutionMemory


class SelfImprovementLoop:
    """
    Closed-loop self-improvement for Atlas OS.
    
    Runs in background, continuously watching and learning.
    """

    CHECK_INTERVAL = 300  # 5 minutes between checks (configurable)
    MIN_DATA_POINTS = 5   # Need 5 interactions before optimizing
    MAX_CHANGES_PER_CYCLE = 3

    def __init__(self, adapter=None, optimizer=None):
        self._adapter = adapter
        self._optimizer = optimizer or WeightOptimizer()
        self._hypothesis_engine = HypothesisEngine()
        self._evaluator = ExperimentEvaluator()
        self._memory = EvolutionMemory()
        self._observations: List[Dict] = []
        self._last_check = time.time()
        self._running = False

    def observe(self, task: str, provider: str, success: bool, feedback: str = ""):
        """Log an observation for the loop."""
        self._observations.append({
            "task": task,
            "provider": provider,
            "success": success,
            "feedback": feedback,
            "timestamp": time.time(),
        })

    def should_run(self) -> bool:
        """Check if loop should run (enough data, enough time)."""
        elapsed = time.time() - self._last_check
        return (
            len(self._observations) >= self.MIN_DATA_POINTS
            and elapsed >= self.CHECK_INTERVAL
        )

    def run_cycle(self) -> Dict[str, Any]:
        """Run one full self-improvement cycle."""
        if len(self._observations) < self.MIN_DATA_POINTS:
            return {"status": "insufficient_data", "observations": len(self._observations)}

        # Step 1: Generate hypothesis from observations
        hypothesis = self._hypothesis_engine.generate(self._observations)
        
        if hypothesis.get("confidence", 0) < 0.3:
            return {"status": "no_hypothesis", "reason": "confidence too low"}

        # Step 2: Evaluate
        # Simulate comparison of best vs worst provider
        target = hypothesis.get("target", {})
        task = target.get("task", "general")
        best_provider = target.get("provider", "unknown")
        
        # Get current weight
        current_weight = self._optimizer.get_weight(task, best_provider)
        
        # Apply improvement if confidence is high
        if hypothesis.get("confidence", 0) > 0.7:
            # Update weight (safe: max 0.05 change)
            reward = 0.8 if "better" in hypothesis.get("statement", "").lower() else 0.4
            new_weight = self._optimizer.update(task, best_provider, reward)
            
            change = {
                "task": task,
                "provider": best_provider,
                "old_weight": current_weight,
                "new_weight": new_weight,
                "hypothesis": hypothesis.get("statement", ""),
                "confidence": hypothesis.get("confidence", 0),
            }
            
            self._memory.record({
                "hypothesis": change["hypothesis"],
                "verdict": "adopt",
                "confidence": change["confidence"],
                "change": change,
            })
            
            # Clear old observations after learning
            self._observations = self._observations[-5:]  # Keep last 5
            self._last_check = time.time()
            
            return {
                "status": "improved",
                "change": change,
                "hypothesis": hypothesis,
            }
        
        return {
            "status": "no_action",
            "hypothesis": hypothesis,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        stats = self._memory.get_stats()
        stats["observations"] = len(self._observations)
        stats["weights"] = self._optimizer.get_all_weights()
        return stats