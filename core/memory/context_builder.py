"""
Memory Context Builder

Responsible for:
  - Building context snapshots for Brain prompt construction
  - Exporting memory state across all types
  - Filtering and ranking context

ContextBuilder does NOT:
  - Store memories (Repository does that)
  - Route requests (Router does that)
  - Analyze importance (Pipeline does that)
  - Know about Backend (uses Repository)
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MEMORY_TYPES


class ContextBuilder:
    """
    Builds context snapshots for Brain.

    Uses Repository (not Backend) for data access.
    This keeps the abstraction clean:
        ContextBuilder → Repository → Backend

    Usage:
        builder = ContextBuilder(repository=my_repository)
        context = builder.export()
        context = builder.export(memory_types=["user", "project"])
    """

    def __init__(self, repository=None):
        """
        Args:
            repository: MemoryRepository instance
        """
        self._repository = repository

    def export(
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
        if self._repository is None:
            return {"timestamp": time.time(), "total_records": 0, "memories": {}}

        types_to_export = memory_types or list(MEMORY_TYPES)
        memories = {}
        total = 0

        for mt in types_to_export:
            # Use Repository's get_context for backward compat
            ctx = self._repository.get_context()
            records = ctx.get(mt, {})
            # Convert to list format
            live = [{"key": k, "value": v} for k, v in records.items()]
            if not include_metadata:
                for rec in live:
                    rec.pop("metadata", None)
            memories[mt] = live[:limit_per_type]
            total += len(live)

        return {
            "timestamp": time.time(),
            "total_records": total,
            "memories": memories,
        }

    def export_for_brain(
        self,
        limit_per_type: int = 10,
    ) -> str:
        """
        Export context as a formatted string for Brain prompt injection.
        """
        snapshot = self.export(
            limit_per_type=limit_per_type,
            include_metadata=False,
        )

        lines = ["=== Memory Context ==="]
        for mt, records in snapshot["memories"].items():
            if records:
                lines.append(f"\n[{mt}]")
                for rec in records:
                    val = rec.get("value", "")
                    if isinstance(val, str) and len(val) > 100:
                        val = val[:100] + "..."
                    lines.append(f"  - {val}")

        lines.append(f"\nTotal: {snapshot['total_records']} records")
        return "\n".join(lines)

    def export_summary(self) -> Dict[str, Any]:
        """Export a summary with counts per type."""
        if self._repository is None:
            return {"timestamp": time.time(), "total_records": 0, "counts": {}}

        ctx = self._repository.get_context()
        counts = {mt: len(records) for mt, records in ctx.items()}

        return {
            "timestamp": time.time(),
            "total_records": sum(counts.values()),
            "counts": counts,
        }
