"""
Memory Router v2 — the ONLY entry point for all memory operations in Atlas OS.

Design principles
─────────────────
1. SINGLE GATEWAY  – The Brain, BrainPipeline, and every other component
   call into *this* class for any memory read / write / search.
2. BACKEND AGNOSTIC – Storage is delegated to a pluggable MemoryBackend
   (DictBackend by default; swap in SQLite, Redis, Pinecone, etc.).
3. POLICY-DRIVEN   – A MemoryPolicy defines per-type retention, TTL,
   importance thresholds, and promotion/demotion rules.
4. IMPORTANCE ROUTING – When you don't know *where* to store something,
   call `store()` with importance and the router picks the right type.
5. UNIFIED SEARCH   – `search()` queries across ALL memory types (or a
   subset) and returns ranked results.
6. CONTEXT EXPORT   – `export_context()` produces the snapshot the Brain
   needs for prompt construction.
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy


class MemoryRouter:
    """
    Central router between the Brain and all memory subsystems.

    Instantiation:
        router = MemoryRouter()                    # defaults
        router = MemoryRouter(backend=MyBackend()) # custom backend
        router = MemoryRouter(policy=MemoryPolicy(custom_policies={...}))

    The router owns the backend lifecycle — call open() before use
    and close() when done (optional for DictBackend, mandatory for DB).
    """

    def __init__(
        self,
        backend: Optional[MemoryBackend] = None,
        policy: Optional[MemoryPolicy] = None,
        auto_open: bool = True,
    ):
        self._backend: MemoryBackend = backend or DictBackend()
        self._policy: MemoryPolicy = policy or MemoryPolicy()
        self._operation_log: List[Dict[str, Any]] = []

        if auto_open:
            self._backend.open()

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
    #  STORE  (save / update)
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
        Store a piece of information.

        If memory_type is None, the router uses importance + policy
        to decide where it belongs (importance-based routing).

        Returns a result dict with status, the final memory_type, and key.
        """
        # ── route by importance if no type specified ──
        if memory_type is None:
            memory_type = self._policy.choose_memory_type(importance)

        # ── policy gate: should we accept this record? ──
        if not self._policy.should_accept(memory_type, importance):
            return {
                "status": "rejected",
                "reason": f"importance {importance} below threshold "
                          f"({self._policy.get(memory_type).min_importance}) "
                          f"for type '{memory_type}'",
                "key": key,
                "memory_type": memory_type,
            }

        # ── build record ──
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

        # ── check for promotion (capacity overflow) ──
        current_count = self._backend.count(memory_type)
        if self._policy.needs_promotion(memory_type, current_count):
            self._promote(memory_type)

        # ── persist ──
        existing = self._backend.get(memory_type, key)
        if existing is not None:
            # merge metadata
            merged_meta = {**existing.metadata, **record.metadata}
            record.metadata = merged_meta
            record.created_at = existing.created_at
            record.access_count = existing.access_count
            self._backend.update(record)
            action = "updated"
        else:
            self._backend.put(record)
            action = "stored"

        self._log("store", {"key": key, "memory_type": memory_type, "action": action})

        return {
            "status": action,
            "key": key,
            "memory_type": memory_type,
            "importance": importance,
        }

    # ═══════════════════════════════════════════════
    #  RETRIEVE  (load)
    # ═══════════════════════════════════════════════

    def retrieve(
        self,
        key: str,
        memory_type: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single record by key.

        If memory_type is omitted, searches all types (slower).
        Returns a dict representation or None.
        """
        if memory_type:
            record = self._backend.get(memory_type, key)
            if record and record.is_expired():
                self._backend.delete(memory_type, key)
                return None
            if record:
                self._log("retrieve", {"key": key, "memory_type": memory_type, "found": True})
                return record.to_dict()
            return None

        # search all types
        for mt in MEMORY_TYPES:
            record = self._backend.get(mt, key)
            if record:
                if record.is_expired():
                    self._backend.delete(mt, key)
                    continue
                self._log("retrieve", {"key": key, "memory_type": mt, "found": True})
                return record.to_dict()
        return None

    # ═══════════════════════════════════════════════
    #  UPDATE
    # ═══════════════════════════════════════════════

    def update(
        self,
        key: str,
        value: Any,
        memory_type: Optional[str] = None,
        merge_metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        bump_importance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing record.  If the record doesn't exist,
        it is created (same as store).

        merge_metadata is merged into existing metadata dict.
        tags replaces the tag list entirely (pass None to keep existing).
        bump_importance overwrites the importance score.
        """
        if memory_type:
            record = self._backend.get(memory_type, key)
        else:
            record = None
            for mt in MEMORY_TYPES:
                record = self._backend.get(mt, key)
                if record:
                    memory_type = mt
                    break

        if record is None:
            # fall back to store
            return self.store(key, value, memory_type=memory_type)

        record.value = value
        record.updated_at = time.time()
        if merge_metadata:
            record.metadata.update(merge_metadata)
        if tags is not None:
            record.tags = tags
        if bump_importance is not None:
            record.importance = bump_importance

        self._backend.update(record)
        self._log("update", {"key": key, "memory_type": memory_type})

        return {
            "status": "updated",
            "key": key,
            "memory_type": memory_type,
        }

    # ═══════════════════════════════════════════════
    #  DELETE
    # ═══════════════════════════════════════════════

    def delete(
        self,
        key: str,
        memory_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Delete a record by key.

        If memory_type is omitted, searches all types.
        """
        if memory_type:
            found = self._backend.delete(memory_type, key)
            self._log("delete", {"key": key, "memory_type": memory_type, "found": found})
            return {"status": "deleted" if found else "not_found", "key": key, "memory_type": memory_type}

        for mt in MEMORY_TYPES:
            if self._backend.delete(mt, key):
                self._log("delete", {"key": key, "memory_type": mt, "found": True})
                return {"status": "deleted", "key": key, "memory_type": mt}

        return {"status": "not_found", "key": key}

    # ═══════════════════════════════════════════════
    #  SEARCH  (cross-type)
    # ═══════════════════════════════════════════════

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search across memory types.

        Returns a list of record dicts, ranked by importance.
        """
        results = self._backend.search(
            query=query,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance,
        )
        # filter expired
        live = []
        for r in results:
            if not r.is_expired():
                live.append(r.to_dict())

        self._log("search", {"query": query, "results": len(live)})
        return live

    # ═══════════════════════════════════════════════
    #  CONTEXT EXPORT  (for Brain / prompt building)
    # ═══════════════════════════════════════════════

    def export_context(
        self,
        memory_types: Optional[List[str]] = None,
        limit_per_type: int = 20,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Export a snapshot of memory for prompt construction.

        Returns:
            {
                "timestamp": ...,
                "total_records": N,
                "memories": {
                    "short": [record, ...],
                    "long":  [record, ...],
                    ...
                }
            }
        """
        types_to_export = memory_types or list(MEMORY_TYPES)
        memories = {}
        total = 0

        for mt in types_to_export:
            records = self._backend.list_records(memory_type=mt, limit=limit_per_type)
            # filter expired
            live = [r.to_dict() for r in records if not r.is_expired()]
            if not include_metadata:
                for rec in live:
                    rec.pop("metadata", None)
            memories[mt] = live
            total += len(live)

        self._log("export_context", {"total_records": total})

        return {
            "timestamp": time.time(),
            "total_records": total,
            "memories": memories,
        }

    # ═══════════════════════════════════════════════
    #  BULK / PIPELINE  operations
    # ═══════════════════════════════════════════════

    def store_batch(
        self,
        entries: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Store multiple records in one call.

        Each entry dict should have at minimum:
            { "key": ..., "value": ... }
        Optional: memory_type, importance, tags, source, ttl, metadata
        """
        results = []
        for entry in entries:
            results.append(self.store(
                key=entry["key"],
                value=entry["value"],
                memory_type=entry.get("memory_type"),
                importance=entry.get("importance", 0.5),
                tags=entry.get("tags"),
                source=entry.get("source", "batch"),
                ttl=entry.get("ttl"),
                metadata=entry.get("metadata"),
            ))
        return results

    def retrieve_batch(
        self,
        keys: List[Dict[str, str]],
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Retrieve multiple records.

        Each key dict: { "key": ..., "memory_type": ... }
        """
        return [
            self.retrieve(entry["key"], entry.get("memory_type"))
            for entry in keys
        ]

    # ═══════════════════════════════════════════════
    #  MAINTENANCE
    # ═══════════════════════════════════════════════

    def purge_expired(self) -> int:
        """Remove all expired records across all types."""
        count = self._backend.purge_expired()
        self._log("purge_expired", {"count": count})
        return count

    def clear(
        self,
        memory_type: Optional[str] = None,
    ) -> int:
        """Clear records. If memory_type given, only clear that type."""
        count = self._backend.clear(memory_type)
        self._log("clear", {"memory_type": memory_type, "count": count})
        return count

    def clear_session(self) -> int:
        """Convenience: clear all session memory."""
        return self.clear("session")

    # ═══════════════════════════════════════════════
    #  LIST / INSPECT
    # ═══════════════════════════════════════════════

    def list_records(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List records with optional type filter and pagination."""
        records = self._backend.list_records(memory_type, limit, offset)
        return [r.to_dict() for r in records if not r.is_expired()]

    def count(self, memory_type: Optional[str] = None) -> int:
        """Count records, optionally per type."""
        return self._backend.count(memory_type)

    # ═══════════════════════════════════════════════
    #  POLICY ACCESS
    # ═══════════════════════════════════════════════

    def get_policy(self, memory_type: str) -> TypePolicy:
        """Get the retention policy for a specific memory type."""
        return self._policy.get(memory_type)

    def set_policy(self, memory_type: str, policy: TypePolicy) -> None:
        """Override the policy for a memory type."""
        self._policy.set(memory_type, policy)

    # ═══════════════════════════════════════════════
    #  OPERATIONS LOG  (audit trail)
    # ═══════════════════════════════════════════════

    def get_operation_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent operation log entries."""
        return self._operation_log[-limit:]

    # ═══════════════════════════════════════════════
    #  SNAPSHOT  (full state export for serialization)
    # ═══════════════════════════════════════════════

    def snapshot(self) -> Dict[str, Any]:
        """
        Full state snapshot — compatible with the old MemoryCoordinator
        interface so the Brain can seamlessly adopt the router.
        """
        return {
            "memory": self.export_context(),
            "health": self.health(),
        }

    # ═══════════════════════════════════════════════
    #  COMPATIBILITY  (bridges from old MemoryCoordinator API)
    # ═══════════════════════════════════════════════

    def process_message(
        self,
        user_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Drop-in replacement for MemoryCoordinator.process_message().

        Stores the user message in session memory and returns
        a context dict the Brain can consume.
        """
        # store in session
        result = self.store(
            key=MemoryRecord.generate_key(message, "session"),
            value=message,
            memory_type="session",
            importance=0.3,
            source="user_message",
            metadata={"user_id": user_id},
        )

        # export context for the brain
        context = self.export_context()

        return {
            "status": "processed",
            "user_id": user_id,
            "message": message,
            "memory": result,
            "context": context,
        }

    def save_memory(
        self,
        category: str,
        key: str,
        value: Any,
    ) -> Dict[str, Any]:
        """Legacy compatibility: MemoryCoordinator.save_memory()."""
        return self.store(key=key, value=value, memory_type=category)

    def load_memory(
        self,
        category: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Legacy compatibility: MemoryCoordinator.load_memory()."""
        result = self.retrieve(key, memory_type=category)
        if result is None:
            return default
        return result.get("value", default)

    # ═══════════════════════════════════════════════
    #  INTERNALS
    # ═══════════════════════════════════════════════

    def _promote(self, memory_type: str) -> None:
        """
        Promote least-recently-used records to the promotion target.

        Called when a bucket reaches its capacity limit.
        """
        policy = self._policy.get(memory_type)
        if not policy.promote_to:
            return

        records = self._backend.list_records(memory_type=memory_type, limit=10)
        # sort by importance ascending — promote the least important
        records.sort(key=lambda r: r.importance)

        for record in records[:3]:  # promote up to 3 at a time
            record.memory_type = policy.promote_to
            self._backend.delete(memory_type, record.key)
            self._backend.put(record)
            self._log("promote", {
                "key": record.key,
                "from": memory_type,
                "to": policy.promote_to,
            })

    def _log(self, operation: str, details: Dict[str, Any]) -> None:
        """Append to the in-memory operation log (capped at 1000 entries)."""
        self._operation_log.append({
            "op": operation,
            "time": time.time(),
            **details,
        })
        if len(self._operation_log) > 1000:
            self._operation_log = self._operation_log[-1000:]
