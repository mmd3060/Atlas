"""
Atlas OS Memory System v2

Components:
    MemoryRouter      — single entry point for ALL memory operations
    MemoryRecord      — standardised memory entry dataclass
    MemoryBackend     — abstract storage interface
    DictBackend       — default in-memory backend
    MemoryPolicy      — retention rules per memory type

Quick start:
    from core.memory import MemoryRouter
    router = MemoryRouter()
    router.store("my_key", "my_value", importance=0.8)
    print(router.search("my_value"))
"""

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy, DEFAULT_POLICIES
from core.memory.memory_router import MemoryRouter

__all__ = [
    "MemoryRouter",
    "MemoryRecord",
    "MemoryBackend",
    "DictBackend",
    "MemoryPolicy",
    "TypePolicy",
    "DEFAULT_POLICIES",
    "MEMORY_TYPES",
]
