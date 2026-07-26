"""
Memory Router v2.1 — SLIM gateway for all memory operations in Atlas OS.

Architecture:
    User → Memory Router → Memory Pipeline → Memory Coordinator → Memory Engine → Backend

The Router does ONLY:
  1. Receive request
  2. Detect source (Brain / Agent / Tool)
  3. Delegate to Pipeline
  4. Return result

It does NOT:
  - Build MemoryRecords (Pipeline does that)
  - Calculate importance (Pipeline + ImportanceAnalyzer)
  - Build context (ContextBuilder does that)
  - Process messages (Coordinator does that)
  - Promote/demote records (MaintenanceService does that)
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy


class MemoryRouter:
    """
    Slim router between external callers and the memory subsystem.

    Instantiation:
        router = MemoryRouter()                    # defaults
        router = MemoryRouter(backend=MyBackend()) # custom backend
        router = MemoryRouter(policy=MemoryPolicy(...))

    The router owns the backend lifecycle — call open() before use
    and close() when done.
    """

    def __init__(
        self,
        backend: Optional[MemoryBackend] = None,
        policy: Optional[MemoryPolicy] = None,
        auto_open: bool = True,
    ):
        self._backend: MemoryBackend = backend or DictBackend()
        self._policy: MemoryPolicy = policy or MemoryPolicy()
        self._pipeline = None  # lazy init
        self._coordinator = None  # lazy init

        if auto_open:
            self._backend.open()

    # ═══════════════════════════════════════════════
    #  LAZY WIRING — import here to avoid circular deps
    # ═══════════════════════════════════════════════

    def _get_pipeline(self):
        if self._pipeline is None:
            from core.memory.memory_pipeline import MemoryPipeline
            self._pipeline = MemoryPipeline(
                backend=self._backend,
                policy=self._policy,
            )
        return self._pipeline

    def _get_coordinator(self):
        if self._coordinator is None:
            from core.memory.memory_coordinator import MemoryCoordinator
            self._coordinator = MemoryCoordinator(
                backend=self._backend,
                policy=self._policy,
            )
        return self._coordinator

    # ═══════════════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════════════

    def open(self) -> None:
        """Open the underlying backend."""
        self._backend.open()

    def close(self) -> None:
        """Close the underlying backend."""
        self._backend.close()

    def health(self) -> Dict[str, Any]:
        """Return router health status."""
        return {
            "router": "ok",
            "backend": "ok" if self._backend.health() else "degraded",
            "backend_type": type(self._backend).__name__,
            "total_records": self._backend.count(),
            "records_per_type": {
                mt: self._backend.count(mt) for mt in MEMORY_TYPES
            },
        }

    # ═══════════════════════════════════════════════
    #  CORE ROUTING — the ONLY job of this class
    # ═══════════════════════════════════════════════

    def route(
        self,
        message: str,
        source: str = "brain",
        user_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Route a memory request to the appropriate handler.

        Args:
            message:     The content to process
            source:      Who sent this (brain / agent / tool / user)
            user_id:     Optional user identifier
            memory_type: Force a specific memory type (skip Pipeline analysis)
            importance:  Force importance score (skip ImportanceAnalyzer)

        Returns:
            Result dict from the Pipeline or Coordinator.
        """
        # ── detect source and route accordingly ──
        if source == "user":
            return self._route_user_message(message, user_id)
        elif source == "brain":
            return self._route_brain_request(message, memory_type, importance)
        elif source == "tool":
            return self._route_tool_output(message, memory_type, importance)
        else:
            # default: treat as brain request
            return self._route_brain_request(message, memory_type, importance)

    def _route_user_message(
        self,
        message: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """User messages go through the full Coordinator pipeline."""
        coordinator = self._get_coordinator()
        return coordinator.process_message(
            user_id=user_id or "anonymous",
            message=message,
        )

    def _route_brain_request(
        self,
        message: str,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Brain requests go through Pipeline for analysis + storage."""
        pipeline = self._get_pipeline()
        return pipeline.process(
            text=message,
            memory_type=memory_type,
            importance=importance,
        )

    def _route_tool_output(
        self,
        message: str,
        memory_type: Optional[str] = None,
        importance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Tool outputs go through Pipeline with default importance."""
        pipeline = self._get_pipeline()
        return pipeline.process(
            text=message,
            memory_type=memory_type,
            importance=importance or 0.5,
        )

    # ═══════════════════════════════════════════════
    #  DIRECT ACCESS — for when you know exactly what you need
    # ═══════════════════════════════════════════════

    def store(
        self,
        key: str,
        value: Any,
        memory_type: Optional[str] = None,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        source: str = "unknown",
        ttl: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Direct store — bypasses Pipeline analysis.
        Use when you already know the type and importance.
        """
        if memory_type is None:
            memory_type = self._policy.choose_memory_type(importance)

        if not self._policy.should_accept(memory_type, importance):
            return {
                "status": "rejected",
                "reason": f"importance {importance} below threshold "
                          f"({self._policy.get(memory_type).min_importance}) "
                          f"for type '{memory_type}'",
                "key": key,
                "memory_type": memory_type,
            }

        record = MemoryRecord(
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            source=source,
            ttl=ttl or self._policy.get(memory_type).ttl_seconds,
            metadata=metadata or {},
        )

        existing = self._backend.get(memory_type, key)
        if existing is not None:
            merged_meta = {**existing.metadata, **record.metadata}
            record.metadata = merged_meta
            record.created_at = existing.created_at
            record.access_count = existing.access_count
            self._backend.update(record)
            action = "updated"
        else:
            self._backend.put(record)
            action = "stored"

        return {
            "status": action,
            "key": key,
            "memory_type": memory_type,
            "importance": importance,
        }

    def retrieve(
        self,
        key: str,
        memory_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Direct retrieve by key."""
        if memory_type:
            record = self._backend.get(memory_type, key)
            if record and record.is_expired():
                self._backend.delete(memory_type, key)
                return None
            if record:
                return record.to_dict()
            return None

        for mt in MEMORY_TYPES:
            record = self._backend.get(mt, key)
            if record:
                if record.is_expired():
                    self._backend.delete(mt, key)
                    continue
                return record.to_dict()
        return None

    def delete(
        self,
        key: str,
        memory_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Direct delete by key."""
        if memory_type:
            found = self._backend.delete(memory_type, key)
            return {"status": "deleted" if found else "not_found", "key": key}

        for mt in MEMORY_TYPES:
            if self._backend.delete(mt, key):
                return {"status": "deleted", "key": key, "memory_type": mt}

        return {"status": "not_found", "key": key}

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search across memory types."""
        results = self._backend.search(
            query=query,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance,
        )
        live = [r.to_dict() for r in results if not r.is_expired()]
        return live

    # ═══════════════════════════════════════════════
    #  DELEGATION — Pipeline/Coordinator handle these
    # ═══════════════════════════════════════════════

    def export_context(self, **kwargs) -> Dict[str, Any]:
        """Delegate to ContextBuilder via Coordinator."""
        from core.memory.context_builder import ContextBuilder
        builder = ContextBuilder(backend=self._backend)
        return builder.export(**kwargs)

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Delegate to Coordinator."""
        coordinator = self._get_coordinator()
        return coordinator.process_message(user_id, message)

    def purge_expired(self) -> int:
        """Remove all expired records."""
        return self._backend.purge_expired()

    def clear(self, memory_type: Optional[str] = None) -> int:
        """Clear records."""
        return self._backend.clear(memory_type)

    def clear_session(self) -> int:
        """Clear all session memory."""
        return self.clear("session")

    def list_records(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List records."""
        records = self._backend.list_records(memory_type, limit, offset)
        return [r.to_dict() for r in records if not r.is_expired()]

    def count(self, memory_type: Optional[str] = None) -> int:
        """Count records."""
        return self._backend.count(memory_type)
