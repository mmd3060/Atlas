"""
Procedural Memory — Atlas's internal how-to knowledge.
"""

from typing import Any, Dict, List, Optional


class ProceduralMemory:
    """
    Atlas OS's procedural knowledge (how to fix errors, how to run tests).
    
    Usage:
        memory = ProceduralMemory()
        memory.record_procedure("fix_python_error", ["install deps", "run lint", "fix bugs"])
        steps = memory.get_steps("fix_python_error")
    """

    def __init__(self):
        self._procedures: Dict[str, List[str]] = {}

    def record_procedure(self, name: str, steps: List[str]):
        """Record a procedure."""
        self._procedures[name] = steps

    def get_steps(self, name: str) -> List[str]:
        """Get steps for a procedure."""
        return self._procedures.get(name, [])

    def list_procedures(self) -> List[str]:
        """List all procedures."""
        return list(self._procedures.keys())