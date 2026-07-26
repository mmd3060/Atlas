"""
Memory Record — standardized memory entry for Atlas OS Memory Router v2.

Every piece of information that flows through the memory system
is wrapped in a MemoryRecord, making it traceable, rankable,
and portable across backends.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


# ──────────────────────────────────────────────
# Valid memory types the router understands
# ──────────────────────────────────────────────
MEMORY_TYPES = (
    "short",         # working / scratch memory
    "long",          # persistent long-term memory
    "session",       # current session only
    "project",       # project-specific knowledge
    "user",          # user profile & preferences
    "task",          # task / goal tracking
    "experience",    # learned patterns, past mistakes/solutions
    "knowledge",     # structured knowledge base entries
)


@dataclass
class MemoryRecord:
    """
    A single, self-describing memory unit.

    Attributes:
        key:        unique identifier within its memory type
        value:      the payload (any JSON-serialisable object)
        memory_type: which subsystem stores this record
        importance:  0.0 – 1.0  (used for ranking & retention)
        created_at:  epoch timestamp
        updated_at:  epoch timestamp
        tags:        freeform labels for filtering
        source:      where this memory came from (e.g. "user_message", "brain_output")
        ttl:         time-to-live in seconds  (None = no expiry)
        access_count: how many times this record has been retrieved
        metadata:    arbitrary extra fields
    """

    key: str
    value: Any
    memory_type: str = "short"
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: list = field(default_factory=list)
    source: str = "unknown"
    ttl: Optional[float] = None
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ── helpers ──────────────────────────────────

    def touch(self):
        """Bump access count and update timestamp."""
        self.access_count += 1
        self.updated_at = time.time()

    def is_expired(self) -> bool:
        """Return True if the record's TTL has elapsed."""
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary (backend-agnostic)."""
        return {
            "key":          self.key,
            "value":        self.value,
            "memory_type":  self.memory_type,
            "importance":   self.importance,
            "created_at":   self.created_at,
            "updated_at":   self.updated_at,
            "tags":         self.tags,
            "source":       self.source,
            "ttl":          self.ttl,
            "access_count": self.access_count,
            "metadata":     self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        """Reconstruct a MemoryRecord from a plain dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @staticmethod
    def generate_key(text: str, memory_type: str = "short") -> str:
        """
        Deterministic key derived from text content.
        Falls back to a UUID if text is empty.
        """
        if text and text.strip():
            words = text.strip().split()
            slug = "_".join(words[:4]).lower()
            # strip non-alphanum except underscore / hyphen
            slug = "".join(c for c in slug if c.isalnum() or c in "_-")
            return f"{memory_type}::{slug}"
        return f"{memory_type}::{uuid.uuid4().hex[:12]}"
