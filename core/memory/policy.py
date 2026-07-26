"""
Memory Policy — retention & routing rules for Atlas OS Memory Router v2.

Each memory type has its own policy that dictates:
  - max capacity
  - time-to-live (TTL)
  - minimum importance threshold for storage
  - whether to auto-purge expired entries
  - promotion/demotion rules
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from core.memory.types import MEMORY_TYPES


@dataclass
class TypePolicy:
    """
    Retention rules for a single memory type.

    Attributes:
        max_entries:         hard cap (0 = unlimited)
        ttl_seconds:        time-to-live in seconds (None = never expire)
        min_importance:     reject records below this importance score
        auto_purge:         whether the router should periodically purge expired
        priority:           routing priority (lower = more important)
        description:        human-readable label
        promote_to:         if set, records exceeding max_entries are promoted here
        demote_after:       seconds of inactivity before considering demotion
    """
    max_entries: int = 0
    ttl_seconds: Optional[float] = None
    min_importance: float = 0.0
    auto_purge: bool = False
    priority: int = 50
    description: str = ""
    promote_to: Optional[str] = None
    demote_after: Optional[float] = None


# ─────────────────────────────────────────────────────────────
# Default policies — sensible Atlas OS defaults
# ─────────────────────────────────────────────────────────────
DEFAULT_POLICIES: Dict[str, TypePolicy] = {
    "short": TypePolicy(
        max_entries=50,
        ttl_seconds=3600,           # 1 hour
        min_importance=0.1,
        auto_purge=True,
        priority=10,
        description="Working / scratch memory — short-lived context",
        promote_to="long",
        demote_after=1800,          # 30 min
    ),
    "long": TypePolicy(
        max_entries=0,              # unlimited
        ttl_seconds=None,           # never expires
        min_importance=0.6,
        auto_purge=False,
        priority=100,
        description="Persistent long-term memory — important facts & knowledge",
    ),
    "session": TypePolicy(
        max_entries=200,
        ttl_seconds=None,           # cleared when session ends
        min_importance=0.0,
        auto_purge=False,
        priority=1,
        description="Current session memory — lives only for this conversation",
    ),
    "project": TypePolicy(
        max_entries=0,
        ttl_seconds=None,
        min_importance=0.5,
        auto_purge=False,
        priority=80,
        description="Project-specific knowledge — code, architecture, decisions",
    ),
    "user": TypePolicy(
        max_entries=0,
        ttl_seconds=None,
        min_importance=0.7,
        auto_purge=False,
        priority=90,
        description="User profile — preferences, facts, identity",
    ),
    "task": TypePolicy(
        max_entries=100,
        ttl_seconds=86400,          # 24 hours
        min_importance=0.3,
        auto_purge=True,
        priority=60,
        description="Task / goal tracking — active and recent tasks",
        promote_to="experience",
    ),
    "experience": TypePolicy(
        max_entries=0,
        ttl_seconds=None,
        min_importance=0.4,
        auto_purge=False,
        priority=70,
        description="Learned patterns — past mistakes, solutions, lessons",
    ),
    "knowledge": TypePolicy(
        max_entries=0,
        ttl_seconds=None,
        min_importance=0.5,
        auto_purge=False,
        priority=75,
        description="Structured knowledge base — facts, procedures, references",
    ),
}


class MemoryPolicy:
    """
    Manages retention policies for all memory types.

    Usage:
        policy = MemoryPolicy()
        p = policy.get("short")
        if record.importance >= p.min_importance:
            ...
    """

    def __init__(self, custom_policies: Optional[Dict[str, TypePolicy]] = None):
        # Start with defaults, then overlay any custom overrides
        self._policies: Dict[str, TypePolicy] = {}
        for mt in MEMORY_TYPES:
            if custom_policies and mt in custom_policies:
                self._policies[mt] = custom_policies[mt]
            elif mt in DEFAULT_POLICIES:
                self._policies[mt] = DEFAULT_POLICIES[mt]
            else:
                self._policies[mt] = TypePolicy()

    # ── access ───────────────────────────────────

    def get(self, memory_type: str) -> TypePolicy:
        """Get the policy for a memory type. Returns a permissive default if unknown."""
        return self._policies.get(memory_type, TypePolicy())

    def set(self, memory_type: str, policy: TypePolicy) -> None:
        """Override or add a policy for a memory type."""
        self._policies[memory_type] = policy

    def all_policies(self) -> Dict[str, TypePolicy]:
        """Return a copy of all policies."""
        return dict(self._policies)

    # ── decision helpers ─────────────────────────

    def should_accept(self, memory_type: str, importance: float) -> bool:
        """Return True if a record with this importance qualifies for storage."""
        policy = self.get(memory_type)
        return importance >= policy.min_importance

    def choose_memory_type(self, importance: float, hints: Optional[str] = None) -> str:
        """
        Given an importance score and optional content hints,
        decide which memory type should receive the record.

        This is the importance-based routing decision.
        """
        if importance >= 0.9:
            return "long"       # very important → long-term
        if importance >= 0.7:
            return "user"       # moderately high → user memory
        if importance >= 0.5:
            return "project"    # medium → project memory
        if importance >= 0.3:
            return "task"       # low-medium → task memory
        return "short"          # low → short-term (ephemeral)

    def needs_promotion(self, memory_type: str, current_count: int) -> bool:
        """Return True if the bucket is at capacity and promotion target exists."""
        policy = self.get(memory_type)
        if policy.max_entries <= 0:
            return False
        if not policy.promote_to:
            return False
        return current_count >= policy.max_entries

    def is_overdue_demotion(self, record_updated_at: float, memory_type: str) -> bool:
        """Return True if a record has been inactive long enough to demote."""
        import time
        policy = self.get(memory_type)
        if policy.demote_after is None:
            return False
        return (time.time() - record_updated_at) > policy.demote_after
