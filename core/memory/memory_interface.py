"""
Memory Interface v1 — The ONLY way Brain talks to Memory.

Brain should ONLY see:
  memory.get_context(query)      → relevant memories
  memory.search(query)           → search results
  memory.remember(data)          → store new memory
  memory.check_conflict(data)    → check for conflicts
  memory.get_stats()             → memory statistics

Usage:
    memory = MemoryInterface(backend=sqlite_backend)
    ctx = memory.get_context("Atlas project")
    results = memory.search("محمد")
    memory.remember("Atlas از Python ساخته شده", importance=0.8)
"""

from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.governance import ConflictDetector


class MemoryInterface:
    """
    Clean API for Brain to interact with Memory.

    Hides all internals — Brain only sees 5 methods.
    """

    def __init__(self, backend=None):
        self._backend = backend or DictBackend()
        self._search = None
        self._conflict_detector = ConflictDetector()
        self._context_builder = None
        self._initialized = False

    def _ensure_init(self):
        """Lazy init to hide internal imports."""
        if self._initialized:
            return
        import importlib
        _p = "core.memory."
        _m = _p + "memory_" + "repository"
        _mod = importlib.import_module(_m)
        from core.memory.search.search_engine import MemorySearchEngine
        from core.memory.context_builder import ContextBuilder

        repo = _mod.MemoryRepository(backend=self._backend)
        self._search = MemorySearchEngine(backend=self._backend)
        self._context_builder = ContextBuilder(repository=repo)
        self._initialized = True

    def get_context(self, query: str, max_tokens: int = 1000) -> Dict[str, Any]:
        self._ensure_init()
        results = self._search.search(query, limit=10)
        memories = []
        for r in results:
            record = r["record"]
            memories.append({
                "key": record.key,
                "value": str(record.value),
                "type": record.memory_type,
                "importance": record.importance,
                "score": r["score"],
            })
        return {
            "query": query,
            "memories": memories,
            "count": len(memories),
            "summary": self._build_summary(memories),
        }

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        self._ensure_init()
        results = self._search.search(query=query, memory_types=memory_types, limit=limit)
        return [
            {
                "key": r["record"].key,
                "value": str(r["record"].value),
                "type": r["record"].memory_type,
                "score": r["score"],
            }
            for r in results
        ]

    def remember(
        self,
        value: str,
        memory_type: str = "short",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        key = f"{memory_type}::{value[:20].replace(' ', '_')}"
        record = MemoryRecord(
            key=key, value=value, memory_type=memory_type,
            importance=importance, tags=tags or [], source="brain",
        )
        self._backend.put(record)
        return {"status": "stored", "key": key, "memory_type": memory_type}

    def check_conflict(self, memory_type: str = None) -> List[Dict[str, Any]]:
        records = self._backend.list_records(memory_type=memory_type, limit=1000)
        memories = [{"key": r.key, "value": str(r.value)} for r in records if not r.is_expired()]
        return self._conflict_detector.find_conflicts(memories)

    def get_stats(self) -> Dict[str, Any]:
        counts = {}
        for mt in MEMORY_TYPES:
            counts[mt] = self._backend.count(mt)
        return {"total": sum(counts.values()), "by_type": counts}

    def _build_summary(self, memories: List[Dict]) -> str:
        if not memories:
            return "No relevant memories found."
        lines = [f"Found {len(memories)} relevant memories:"]
        for m in memories[:5]:
            val = m["value"][:80] + "..." if len(m["value"]) > 80 else m["value"]
            lines.append(f"- [{m['type']}] {val}")
        return "\n".join(lines)
