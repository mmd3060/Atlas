"""
Atlas OS Memory System v2.1

Architecture:
    User → Memory Router → Memory Pipeline → Memory Coordinator → Memory Engine → Backend

Modules:
    types.py           — MemoryRecord dataclass
    backend.py         — MemoryBackend ABC
    backends/          — Backend implementations (Dict, SQLite, Redis, ...)
    policy.py          — MemoryPolicy (retention rules per type)
    memory_router.py   — Slim router (ONLY routing)
    memory_pipeline.py — Analysis + record building + storage
    memory_coordinator.py — Coordination hub
    context_builder.py — Context snapshots for Brain
    memory_engine.py   — Core storage (legacy)
    memory_importance.py — Importance analyzer
    conversation_state.py — Conversation tracking
    context_manager.py — Context management
"""

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy
from core.memory.memory_router import MemoryRouter
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.memory_coordinator import MemoryCoordinator
from core.memory.context_builder import ContextBuilder

__all__ = [
    "MemoryRecord",
    "MEMORY_TYPES",
    "MemoryBackend",
    "DictBackend",
    "MemoryPolicy",
    "TypePolicy",
    "MemoryRouter",
    "MemoryPipeline",
    "MemoryCoordinator",
    "ContextBuilder",
]
