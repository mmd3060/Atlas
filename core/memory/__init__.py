"""
Atlas OS Memory System v2.2

Architecture:
    Brain → Coordinator → Router → Pipeline → Repository → Backend

Modules:
    types.py            — MemoryRecord dataclass
    backend.py          — MemoryBackend ABC
    backends/           — Backend implementations (Dict, SQLite, Redis, ...)
    policy.py           — MemoryPolicy (retention rules per type)
    memory_repository.py — Direct data access (CRUD)
    memory_pipeline.py  — Analysis + record building + storage decisions
    memory_router.py    — Pure switch (no logic)
    memory_coordinator.py — THE ONLY entry point
    context_builder.py  — Context snapshots for Brain
    memory_importance.py — Importance analyzer
    conversation_state.py — Conversation tracking
    context_manager.py  — Context management
"""

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy
from core.memory.memory_repository import MemoryRepository
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.memory_router import MemoryRouter
from core.memory.memory_coordinator import MemoryCoordinator
from core.memory.context_builder import ContextBuilder


def get_memory_prompt():
    """Get memory context for Brain prompt (simplified)."""
    try:
        from core.memory.backends.sqlite_backend import SQLiteBackend
        backend = SQLiteBackend()
        backend.open()
        repo = MemoryRepository(backend=backend)
        memories = repo.list_all(limit=5)
        backend.close()
        if memories:
            lines = ["[Memory]"]
            for m in memories:
                lines.append(f"- {m.value[:80]}")
            return "\n".join(lines)
    except Exception:
        pass
    return ""

__all__ = [
    "MemoryRecord",
    "MEMORY_TYPES",
    "MemoryBackend",
    "DictBackend",
    "MemoryPolicy",
    "TypePolicy",
    "MemoryRepository",
    "MemoryPipeline",
    "MemoryRouter",
    "MemoryCoordinator",
    "ContextBuilder",
    "get_memory_prompt",
]
