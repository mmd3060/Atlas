"""
Memory Coordinator v2.2 — THE ONLY entry point for Atlas OS memory.

Architecture:
    Brain → Coordinator → Router → Pipeline → Repository → Backend

The Coordinator is responsible for:
  - Being the ONLY interface Brain/Agent/Tool talk to
  - Managing ConversationState
  - Managing Context
  - Coordinating Router → Pipeline → Repository
  - Preparing memory for Brain

The Coordinator does NOT:
  - Build individual records (Pipeline does that)
  - Store directly to backend (Repository does that)
  - Route requests (Router does that)
"""

import time

from core.memory.memory_repository import MemoryRepository
from core.memory.conversation_state import ConversationStateManager
from core.memory.context_manager import ContextManager
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.memory_router import MemoryRouter
from core.memory.context_builder import ContextBuilder


class MemoryCoordinator:
    """
    The ONLY entry point for all memory operations in Atlas OS.

    Brain, Agent, and Tool all talk to Coordinator.
    Coordinator delegates to Router → Pipeline → Repository → Backend.
    """

    def __init__(self, backend=None):
        """
        Args:
            backend: MemoryBackend instance (shared across all layers)
        """
        # ── Data layer ──
        self.repository = MemoryRepository(backend=backend)

        # ── Business logic ──
        self.pipeline = MemoryPipeline(repository=self.repository)

        # ── State management ──
        self.state = ConversationStateManager()
        self.context = ContextManager()

        # ── Routing (pure switch) ──
        self.router = MemoryRouter(
            pipeline=self.pipeline,
            coordinator=self,  # circular but intentional — Router delegates back
        )

        # ── Context export ──
        self._context_builder = ContextBuilder(backend=backend)

    # ═══════════════════════════════════════════════
    #  THE ONLY ENTRY POINT — Brain talks here
    # ═══════════════════════════════════════════════

    def process_message(self, user_id, message):
        """
        Process a user message through the full memory pipeline.

        This is the ONLY way external code should interact with memory.
        """
        # 1. Register in conversation
        self.state.add_message("user", message)

        # 2. Process through pipeline (analyze → build record → store)
        memory_result = self.pipeline.process(text=message)

        # 3. Build context for Brain
        context = self._build_context(user_id, message)

        return {
            "status": "processed",
            "user_id": user_id,
            "message": message,
            "memory": memory_result,
            "context": context,
        }

    def process_brain_request(self, message):
        """
        Brain requests go through Pipeline for analysis + storage.
        """
        return self.pipeline.process(text=message)

    def process_tool_output(self, message):
        """
        Tool outputs go through Pipeline with default handling.
        """
        return self.pipeline.process(text=message)

    # ═══════════════════════════════════════════════
    #  ROUTING — delegate to Router
    # ═══════════════════════════════════════════════

    def route(self, message, source="brain", user_id=None):
        """
        Route a request — pure delegation to Router.
        """
        return self.router.route(message, source, user_id)

    # ═══════════════════════════════════════════════
    #  CONTEXT
    # ═══════════════════════════════════════════════

    def _build_context(self, user_id, message):
        """Build full context snapshot for Brain."""
        return {
            "user_id": user_id,
            "message": message,
            "conversation": self.state.snapshot(),
            "context": self.context.get_context(),
            "memory": self.repository.get_context(),
            "timestamp": time.time(),
        }

    def export_context(self, **kwargs):
        """Export context for Brain prompt construction."""
        return self._context_builder.export(**kwargs)

    def export_context_for_brain(self, **kwargs):
        """Export context as formatted string for Brain prompt."""
        return self._context_builder.export_for_brain(**kwargs)

    # ═══════════════════════════════════════════════
    #  MESSAGE MANAGEMENT
    # ═══════════════════════════════════════════════

    def add_message(self, role, content, metadata=None):
        """Add a message to conversation state."""
        self.state.add_message(role, content, metadata)
        return {"status": "success", "event": "message_added", "role": role}

    # ═══════════════════════════════════════════════
    #  CONTEXT MANAGEMENT
    # ═══════════════════════════════════════════════

    def update_context(self, category, data):
        """Update a context category."""
        self.context.update(category, data)
        return {"status": "updated", "category": category}

    # ═══════════════════════════════════════════════
    #  DIRECT REPOSITORY ACCESS
    # ═══════════════════════════════════════════════

    def save_memory(self, category, key, value):
        """Save directly to Repository."""
        self.repository.save(category, key, value)
        return {"status": "saved", "category": category, "key": key}

    def load_memory(self, category, key, default=None):
        """Load from Repository."""
        return self.repository.load(category, key, default)

    # ═══════════════════════════════════════════════
    #  SNAPSHOT
    # ═══════════════════════════════════════════════

    def snapshot(self):
        """Full state snapshot."""
        return {
            "conversation": self.state.snapshot(),
            "context": self.context.get_context(),
            "memory": self.repository.get_context(),
        }

    # ═══════════════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════════════

    def open(self):
        self.repository.open()

    def close(self):
        self.repository.close()

    def health(self):
        return self.repository.health()
