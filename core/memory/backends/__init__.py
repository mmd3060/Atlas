"""Atlas OS Memory System — backends package."""

from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend

__all__ = ["MemoryBackend", "DictBackend"]
