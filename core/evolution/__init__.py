"""
Evolution Package

Modules:
    weight_optimizer.py       — Manages decision weights
    change_manager.py         — Records changes for audit
    rollback_manager.py       — Save/restore snapshots
    self_improvement_engine.py — The evolution loop
"""

from core.evolution.weight_optimizer import WeightOptimizer
from core.evolution.change_manager import ChangeManager
from core.evolution.rollback_manager import RollbackManager
from core.evolution.self_improvement_engine import SelfImprovementEngine, EvolutionRules

__all__ = [
    "WeightOptimizer",
    "ChangeManager",
    "RollbackManager",
    "SelfImprovementEngine",
    "EvolutionRules",
]
