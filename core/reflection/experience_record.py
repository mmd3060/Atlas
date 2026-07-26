"""
Experience Record — A single experience for reflection.
"""

import time
from typing import Any, Dict, Optional


class ExperienceRecord:
    """
    Represents a single experience (decision + outcome).

    Usage:
        exp = ExperienceRecord(
            task="coding",
            decision={"provider": "github"},
            outcome="success",
            feedback="answer was helpful",
        )
    """

    def __init__(
        self,
        task: str,
        decision: Dict[str, Any],
        outcome: str,
        feedback: str = "",
        metadata: Optional[Dict] = None,
    ):
        self.task = task
        self.decision = decision
        self.outcome = outcome
        self.feedback = feedback
        self.metadata = metadata or {}
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "decision": self.decision,
            "outcome": self.outcome,
            "feedback": self.feedback,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExperienceRecord":
        return cls(
            task=data.get("task", ""),
            decision=data.get("decision", {}),
            outcome=data.get("outcome", ""),
            feedback=data.get("feedback", ""),
            metadata=data.get("metadata", {}),
        )
