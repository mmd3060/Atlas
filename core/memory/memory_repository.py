"""
Memory Repository — the ONLY direct data access layer in Atlas OS.

Repository is responsible for:
  - CRUD operations on memory data
  - Data access abstraction
  - No business logic, no routing, no analysis

Repository does NOT:
  - Route requests (Router does that)
  - Analyze importance (Pipeline does that)
  - Build context (ContextBuilder does that)
  - Decide what to store (Pipeline does that)

Naming:
  MemoryRepository (not MemoryEngine) because this is a data access layer,
  not an "engine" that processes things.
"""

from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend


class MemoryRepository:
    """
    Direct data access layer for Atlas OS memory.

    Wraps a MemoryBackend and provides simple CRUD operations.
    No business logic — just data in, data out.
    """

    def __init__(self, backend=None):
        """
        Args:
            backend: MemoryBackend instance (default: DictBackend)
        """
        self._backend = backend or DictBackend()

    # ═══════════════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════════════

    def open(self):
        self._backend.open()

    def close(self):
        self._backend.close()

    def health(self):
        return self._backend.health()

    # ═══════════════════════════════════════════════
    #  CRUD
    # ═══════════════════════════════════════════════

    def save(self, category, key, value):
        """Save a key-value pair to a category."""
        from core.memory.types import MemoryRecord
        record = MemoryRecord(
            key=key,
            value=value,
            memory_type=category,
        )
        existing = self._backend.get(category, key)
        if existing:
            self._backend.update(record)
        else:
            self._backend.put(record)

    def load(self, category, key, default=None):
        """Load a value by category and key."""
        record = self._backend.get(category, key)
        if record is None:
            return default
        if record.is_expired():
            self._backend.delete(category, key)
            return default
        return record.value

    def update(self, category, key, value):
        """Update an existing record."""
        self.save(category, key, value)

    def delete(self, category, key):
        """Delete a record by category and key."""
        return self._backend.delete(category, key)

    # ═══════════════════════════════════════════════
    #  QUERY
    # ═══════════════════════════════════════════════

    def exists(self, category, key):
        """Check if a record exists."""
        record = self._backend.get(category, key)
        return record is not None and not record.is_expired()

    def count(self, category=None):
        """Count records, optionally per category."""
        return self._backend.count(category)

    def list_keys(self, category=None, limit=100):
        """List all keys in a category."""
        records = self._backend.list_records(memory_type=category, limit=limit)
        return [r.key for r in records if not r.is_expired()]

    # ═══════════════════════════════════════════════
    #  CONTEXT EXPORT (for backward compat)
    # ═══════════════════════════════════════════════

    def get_context(self):
        """Return all data grouped by category."""
        from core.memory.types import MEMORY_TYPES
        context = {}
        for cat in MEMORY_TYPES:
            records = self._backend.list_records(memory_type=cat, limit=1000)
            context[cat] = {
                r.key: r.value for r in records if not r.is_expired()
            }
        return context

    # ═══════════════════════════════════════════════
    #  MAINTENANCE
    # ═══════════════════════════════════════════════

    def purge_expired(self):
        """Remove all expired records."""
        return self._backend.purge_expired()

    def clear(self, category=None):
        """Clear records, optionally per category."""
        return self._backend.clear(category)

    def clear_session(self):
        """Clear all session memory."""
        return self.clear("session")
