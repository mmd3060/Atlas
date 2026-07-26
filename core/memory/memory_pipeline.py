"""
Memory Pipeline v2.1

Pipeline is responsible for:
  - Importance Analysis (via MemoryImportanceAnalyzer)
  - Category Detection
  - Building MemoryRecords
  - Validation
  - Deciding whether to store or discard
  - Storing via Backend

Pipeline does NOT:
  - Route requests (Router does that)
  - Build context (ContextBuilder does that)
  - Manage conversation state (Coordinator does that)
"""

from core.memory.memory_importance import MemoryImportanceAnalyzer
from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy
from core.memory.memory_engine import MemoryEngine


class MemoryPipeline:
    """
    Memory Pipeline v2.1

    The decision-making layer for memory storage.
    Receives text from Router, analyzes it, builds a MemoryRecord,
    and stores it via the Backend.
    """

    def __init__(
        self,
        backend=None,
        policy=None,
        memory_engine=None,
    ):
        self.analyzer = MemoryImportanceAnalyzer()
        self._backend = backend or DictBackend()
        self._policy = policy or MemoryPolicy()

        # Legacy compatibility
        self._memory_engine = memory_engine

    def process(
        self,
        text,
        memory_type=None,
        importance=None,
    ):
        """
        Full pipeline: analyze → decide → build record → store.

        Args:
            text:         The content to process
            memory_type:  Force a specific type (skip auto-detection)
            importance:   Force importance score (skip analyzer)
        """
        # ── Step 1: Analyze importance ──
        if importance is not None:
            analysis = {
                "text": text,
                "importance": importance,
                "category": memory_type or "short",
                "save": self._policy.should_accept(
                    memory_type or "short", importance
                ),
            }
        else:
            analysis = self.analyzer.analyze(text)

        # ── Step 2: Should we save? ──
        if not analysis["save"]:
            return {
                "status": "ignored",
                "analysis": analysis,
            }

        # ── Step 3: Determine memory type ──
        if memory_type:
            category = memory_type
        else:
            category = analysis["category"]

        # ── Step 4: Check policy acceptance ──
        imp = analysis["importance"]
        if not self._policy.should_accept(category, imp):
            return {
                "status": "rejected",
                "reason": f"importance {imp} below threshold for '{category}'",
                "analysis": analysis,
            }

        # ── Step 5: Build MemoryRecord ──
        key = MemoryRecord.generate_key(text, category)
        record = self.build_record(
            key=key,
            value=text,
            memory_type=category,
            importance=imp,
            source="pipeline",
        )

        # ── Step 6: Store ──
        existing = self._backend.get(category, key)
        if existing is not None:
            # merge and update
            merged_meta = {**existing.metadata, **record.metadata}
            record.metadata = merged_meta
            record.created_at = existing.created_at
            record.access_count = existing.access_count
            self._backend.update(record)
            action = "updated"
        else:
            self._backend.put(record)
            action = "stored"

        # Legacy compatibility
        if self._memory_engine:
            self._memory_engine.save(category, key, text)

        return {
            "status": action,
            "category": category,
            "key": key,
            "importance": imp,
            "analysis": analysis,
        }

    def build_record(
        self,
        key,
        value,
        memory_type="short",
        importance=0.5,
        tags=None,
        source="pipeline",
        ttl=None,
        metadata=None,
    ):
        """
        Build a MemoryRecord from raw data.
        This is Pipeline's responsibility — not the Router's.
        """
        return MemoryRecord(
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            source=source,
            ttl=ttl or self._policy.get(memory_type).ttl_seconds,
            metadata=metadata or {},
        )

    def get_memory_context(self):
        """Legacy: return context from MemoryEngine."""
        if self._memory_engine:
            return self._memory_engine.get_context()
        return {}

    # ── backward compatibility ──
    @property
    def memory(self):
        """Legacy: access to MemoryEngine for old code."""
        return self._memory_engine or MemoryEngine()
