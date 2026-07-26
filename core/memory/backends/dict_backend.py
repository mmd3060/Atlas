"""
Dict Backend — in-memory storage implementation for Atlas OS Memory Router v2.

The default backend. Fast, zero-dependency, perfect for development
and single-process deployments.  All data lives in a dict of dicts:

    storage[memory_type][key] -> MemoryRecord
"""

from typing import Dict, List, Optional

from core.memory.backend import MemoryBackend
from core.memory.types import MemoryRecord, MEMORY_TYPES


class DictBackend(MemoryBackend):
    """
    Pure-Python in-memory backend backed by nested dicts.

    Thread-safety note: this backend is NOT thread-safe.
    For multi-threaded deployments, wrap with a lock or use
    a different backend (SQLite, Redis, …).
    """

    def __init__(self):
        # storage[memory_type][key] = MemoryRecord
        self.storage: Dict[str, Dict[str, MemoryRecord]] = {}
        for mt in MEMORY_TYPES:
            self.storage[mt] = {}
        self._open = True

    # ── lifecycle ────────────────────────────────

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def health(self) -> bool:
        return self._open

    # ── CRUD ─────────────────────────────────────

    def put(self, record: MemoryRecord) -> None:
        self._ensure_type(record.memory_type)
        self.storage[record.memory_type][record.key] = record

    def get(self, memory_type: str, key: str) -> Optional[MemoryRecord]:
        bucket = self.storage.get(memory_type, {})
        record = bucket.get(key)
        if record is not None:
            record.touch()
        return record

    def update(self, record: MemoryRecord) -> None:
        """Update in place, or insert if missing."""
        self.put(record)

    def delete(self, memory_type: str, key: str) -> bool:
        bucket = self.storage.get(memory_type, {})
        if key in bucket:
            del bucket[key]
            return True
        return False

    # ── bulk / query ─────────────────────────────

    def list_records(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryRecord]:
        if memory_type:
            records = list(self.storage.get(memory_type, {}).values())
        else:
            records = [
                r
                for bucket in self.storage.values()
                for r in bucket.values()
            ]
        records.sort(key=lambda r: r.updated_at, reverse=True)
        return records[offset: offset + limit]

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[MemoryRecord]:
        """
        Substring search across keys, values (if str), tags, and metadata.
        Results are ranked by importance (descending).
        """
        query_lower = query.lower()
        results: List[MemoryRecord] = []

        types_to_search = memory_types or list(self.storage.keys())

        for mt in types_to_search:
            bucket = self.storage.get(mt, {})
            for record in bucket.values():
                if record.importance < min_importance:
                    continue
                if self._matches(record, query_lower):
                    results.append(record)

        results.sort(key=lambda r: (-r.importance, -r.updated_at))
        return results[:limit]

    def count(self, memory_type: Optional[str] = None) -> int:
        if memory_type:
            return len(self.storage.get(memory_type, {}))
        return sum(len(b) for b in self.storage.values())

    # ── maintenance ──────────────────────────────

    def purge_expired(self) -> int:
        removed = 0
        for mt in list(self.storage.keys()):
            bucket = self.storage[mt]
            expired_keys = [k for k, r in bucket.items() if r.is_expired()]
            for k in expired_keys:
                del bucket[k]
            removed += len(expired_keys)
        return removed

    def clear(self, memory_type: Optional[str] = None) -> int:
        if memory_type:
            count = len(self.storage.get(memory_type, {}))
            if memory_type in self.storage:
                self.storage[memory_type] = {}
            return count
        total = sum(len(b) for b in self.storage.values())
        for mt in MEMORY_TYPES:
            self.storage[mt] = {}
        return total

    # ── internal helpers ─────────────────────────

    def _ensure_type(self, memory_type: str) -> None:
        if memory_type not in self.storage:
            self.storage[memory_type] = {}

    @staticmethod
    def _matches(record: MemoryRecord, query_lower: str) -> bool:
        """Check if a record matches a lowercase query string."""
        # key match
        if query_lower in record.key.lower():
            return True
        # value match (if string)
        if isinstance(record.value, str) and query_lower in record.value.lower():
            return True
        # tag match
        for tag in record.tags:
            if query_lower in tag.lower():
                return True
        # metadata match (string values only)
        for v in record.metadata.values():
            if isinstance(v, str) and query_lower in v.lower():
                return True
        return False
