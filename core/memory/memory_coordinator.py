"""
Memory Coordinator v2.1

The Coordinator is responsible for:
  - Managing ConversationState
  - Managing Context
  - Coordinating Pipeline + Engine
  - Preparing memory for Brain

The Coordinator does NOT:
  - Route requests (Router does that)
  - Build individual records (Pipeline does that)
  - Store directly to backend (Engine does that)
"""

import time

from core.memory.memory_engine import MemoryEngine
from core.memory.conversation_state import ConversationStateManager
from core.memory.context_manager import ContextManager
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.types import MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.policy import MemoryPolicy


class MemoryCoordinator:
    """
    Memory Coordinator v2.1

    The central coordination hub for Atlas OS memory system.
    Bridges Router ↔ Pipeline ↔ Engine ↔ Context.
    """

    def __init__(
        self,
        backend=None,
        policy=None,
    ):
        # Backend + Policy (shared across layers)
        self._backend = backend
        self._policy = policy or MemoryPolicy()

        # Core components
        if backend:
            self.memory = MemoryEngine()
        else:
            self.memory = MemoryEngine()

        self.state = ConversationStateManager()
        self.context = ContextManager()

        # Pipeline with shared backend
        self.pipeline = MemoryPipeline(
            backend=self._backend,
            policy=self._policy,
            memory_engine=self.memory,
        )

    # ═══════════════════════════════════════════════
    #  PROCESS MESSAGE — main entry point
    # ═══════════════════════════════════════════════

    def process_message(
        self,
        user_id,
        message,
    ):
        """
        Process a user message through the full memory pipeline.

        Steps:
          1. Register message in ConversationState
          2. Process through Pipeline (analyze → store)
          3. Build context for Brain
        """
        # 1. Register in conversation
        self.state.add_message("user", message)

        # 2. Process through pipeline
        memory_result = self.pipeline.process(message)

        # 3. Build context
        context = self.build_context(user_id, message)

        return {
            "status": "processed",
            "user_id": user_id,
            "message": message,
            "memory": memory_result,
            "context": context,
        }

    # ═══════════════════════════════════════════════
    #  BUILD CONTEXT
    # ═══════════════════════════════════════════════

    def build_context(
        self,
        user_id,
        message,
    ):
        """Build full context snapshot for Brain."""
        return {
            "user_id": user_id,
            "message": message,
            "conversation": self.state.snapshot(),
            "context": self.context.get_context(),
            "memory": self.memory.get_context(),
            "timestamp": time.time(),
        }

    # ═══════════════════════════════════════════════
    #  MESSAGE MANAGEMENT
    # ═══════════════════════════════════════════════

    def add_message(
        self,
        role,
        content,
        metadata=None,
    ):
        """Add a message to conversation state."""
        self.state.add_message(role, content, metadata)
        return {
            "status": "success",
            "event": "message_added",
            "role": role,
        }

    # ═══════════════════════════════════════════════
    #  CONTEXT MANAGEMENT
    # ═══════════════════════════════════════════════

    def update_context(
        self,
        category,
        data,
    ):
        """Update a context category."""
        self.context.update(category, data)
        return {
            "status": "updated",
            "category": category,
        }

    # ═══════════════════════════════════════════════
    #  DIRECT MEMORY OPERATIONS
    # ═══════════════════════════════════════════════

    def save_memory(
        self,
        category,
        key,
        value,
    ):
        """Save directly to MemoryEngine."""
        self.memory.save(category, key, value)
        return {
            "status": "saved",
            "category": category,
            "key": key,
        }

    def load_memory(
        self,
        category,
        key,
        default=None,
    ):
        """Load from MemoryEngine."""
        return self.memory.load(category, key, default)

    # ═══════════════════════════════════════════════
    #  SNAPSHOT / EXPORT
    # ═══════════════════════════════════════════════

    def snapshot(self):
        """Full state snapshot."""
        return {
            "conversation": self.state.snapshot(),
            "context": self.context.get_context(),
            "memory": self.memory.get_context(),
        }

    def export_context(self):
        """Export context for Brain prompt construction."""
        from core.memory.context_builder import ContextBuilder
        builder = ContextBuilder(backend=self._backend)
        return builder.export()
