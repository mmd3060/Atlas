"""
Memory Pipeline v2.2

Pipeline is responsible for ALL decisions:
  - Importance Analysis (via MemoryImportanceAnalyzer)
  - Category Detection
  - Building MemoryRecords
  - Validation
  - Deciding whether to store or discard
  - Storing via Repository

Pipeline does NOT:
  - Route requests (Router does that)
  - Build context (ContextBuilder does that)
  - Manage conversation state (Coordinator does that)
"""

from core.memory.memory_importance import MemoryImportanceAnalyzer
from core.memory.types import MemoryRecord
from core.memory.policy import MemoryPolicy
from core.memory.memory_repository import MemoryRepository


class MemoryPipeline:
    """
    The decision-making layer for memory storage.

    Receives text, analyzes it, builds a MemoryRecord,
    and stores it via the Repository.
    """

    def __init__(self, repository=None, policy=None):
        """
        Args:
            repository: MemoryRepository instance (for data access)
            policy:     MemoryPolicy instance (for rules)
        """
        self.analyzer = MemoryImportanceAnalyzer()
        self._repository = repository or MemoryRepository()
        self._policy = policy or MemoryPolicy()

    def process(self, text, memory_type=None, importance=None):
        """
        Full pipeline: analyze → decide → build record → store.

        Args:
            text:         The content to process
            memory_type:  Force a specific type (skip auto-detection)
            importance:   Force importance score (skip analyzer)

        Returns:
            Result dict with status, category, key, etc.
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
            return {"status": "ignored", "analysis": analysis}

        # ── Step 3: Determine memory type ──
        category = memory_type or analysis["category"]

        # ── Step 4: Check policy acceptance ──
        imp = analysis["importance"]
        if not self._policy.should_accept(category, imp):
            return {
                "status": "rejected",
                "reason": f"importance {imp} below threshold for '{category}'",
                "analysis": analysis,
            }

        # ── Step 5: Build MemoryRecord (Pipeline builds, not Router) ──
        key = MemoryRecord.generate_key(text, category)
        record = self._build_record(
            key=key,
            value=text,
            memory_type=category,
            importance=imp,
        )

        # ── Step 6: Store via Repository ──
        existing = self._repository.load(category, key)
        if existing is not None:
            self._repository.update(category, key, text)
            action = "updated"
        else:
            self._repository.save(category, key, text)
            action = "stored"

        return {
            "status": action,
            "category": category,
            "key": key,
            "importance": imp,
            "analysis": analysis,
        }

    def _build_record(self, key, value, memory_type="short",
                      importance=0.5, tags=None, source="pipeline",
                      ttl=None, metadata=None):
        """
        Build a MemoryRecord from raw data.
        Pipeline's responsibility — not Router's.
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
