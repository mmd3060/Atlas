"""
Memory Governance Package

Modules:
    memory_governance.py — Decision engine
    rules.py             — Thresholds and constants
    conflict_detector.py — Conflict detection

Usage:
    from core.memory.governance import MemoryGovernance, ConflictDetector, GovernanceRules

    gov = MemoryGovernance()
    decision = gov.evaluate(importance=0.9, quality=0.9, confidence=0.8)
"""

from core.memory.governance.memory_governance import MemoryGovernance
from core.memory.governance.rules import GovernanceRules
from core.memory.governance.conflict_detector import ConflictDetector

__all__ = [
    "MemoryGovernance",
    "GovernanceRules",
    "ConflictDetector",
]
