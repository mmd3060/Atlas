"""
Advanced Memory — Unified interface for all 3 memory types.
"""

from typing import Any, Dict, List, Optional
from core.memory.episodic_memory import EpisodicMemory
from core.memory.semantic_memory import SemanticMemory
from core.memory.procedural_memory import ProceduralMemory


class AdvancedMemory:
    """
    Unified interface for Episodic + Semantic + Procedural memory.
    
    This is Atlas OS's full memory model.
    """

    def __init__(self, adapter=None):
        self.episodic = EpisodicMemory(adapter=adapter)
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()

    def remember_event(self, event_type: str, content: str, context: Dict[str, Any],
                       importance: float = 0.5, tags: List[str] = None):
        """Record an episodic memory."""
        return self.episodic.record_event(event_type, content, context, importance, tags or [])

    def remember_fact(self, subject: str, predicate: str, obj: str):
        """Add a semantic fact."""
        return self.semantic.add_fact(subject, predicate, obj)

    def remember_procedure(self, name: str, steps: List[str]):
        """Record a procedure."""
        return self.procedural.record_procedure(name, steps)

    def recall_full(self, query: str) -> Dict[str, Any]:
        """Recall all relevant memories."""
        return {
            "episodes": [ep.__dict__ for ep in self.episodic.recall(query)],
            "facts": self.semantic.query(query),
            "procedures": [
                {"name": name, "steps": steps}
                for name, steps in self._safe_procedures(query)
            ],
        }

    def _safe_procedures(self, query: str):
        try:
            all_procs = self.procedural.list_procedures()
            return [
                (p, self.procedural.get_steps(p))
                for p in all_procs
                if query.lower() in p.lower()
            ]
        except Exception:
            return []