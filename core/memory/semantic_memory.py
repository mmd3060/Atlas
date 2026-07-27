"""
Semantic Memory — Knowledge graph concepts and relationships.
"""

from typing import Any, Dict, List, Optional


class SemanticMemory:
    """
    Stores and retrieves knowledge (concepts, definitions, relationships).
    
    Usage:
        memory = SemanticMemory()
        memory.add_fact("Python", "is", "a programming language")
        facts = memory.query("Python")
    """

    def __init__(self):
        # A simple graph representation: {subject: {predicate: object}}
        self._graph: Dict[str, Dict[str, List[str]]] = {}

    def add_fact(self, subject: str, predicate: str, obj: str):
        """Add a fact to semantic memory."""
        subj = subject.lower()
        if subj not in self._graph:
            self._graph[subj] = {}
        if predicate not in self._graph[subj]:
            self._graph[subj][predicate] = []
        
        if obj not in self._graph[subj][predicate]:
            self._graph[subj][predicate].append(obj)

    def query(self, subject: str) -> Dict[str, List[str]]:
        """Query semantic memory for a subject."""
        return self._graph.get(subject.lower(), {})

    def find_related(self, predicate: str, obj: str) -> List[str]:
        """Find subjects by relation/object."""
        results = []
        for subj, predicates in self._graph.items():
            if predicate in predicates and obj in predicates[predicate]:
                results.append(subj)
        return results