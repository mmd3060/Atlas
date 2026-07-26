"""
Evolution Package

Modules:
    weight_optimizer.py       — Manages decision weights
    change_manager.py         — Records changes for audit
    rollback_manager.py       — Save/restore snapshots
    self_improvement_engine.py — The evolution loop (v1)
    hypothesis_engine.py      — Generates hypotheses
    experiment_planner.py     — Designs experiments
    experiment_runner.py      — Runs experiments
    evaluator.py              — Evaluates results
    evolution_memory.py       — Evolution history
    evolution_controller.py   — Orchestrates full cycle
"""

from core.evolution.weight_optimizer import WeightOptimizer
from core.evolution.change_manager import ChangeManager
from core.evolution.rollback_manager import RollbackManager
from core.evolution.self_improvement_engine import SelfImprovementEngine, EvolutionRules
from core.evolution.hypothesis_engine import HypothesisEngine
from core.evolution.experiment_planner import ExperimentPlanner
from core.evolution.experiment_runner import ExperimentRunner
from core.evolution.evaluator import ExperimentEvaluator
from core.evolution.evolution_memory import EvolutionMemory
from core.evolution.evolution_controller import EvolutionController

__all__ = [
    "WeightOptimizer",
    "ChangeManager",
    "RollbackManager",
    "SelfImprovementEngine",
    "EvolutionRules",
    "HypothesisEngine",
    "ExperimentPlanner",
    "ExperimentRunner",
    "ExperimentEvaluator",
    "EvolutionMemory",
    "EvolutionController",
]
