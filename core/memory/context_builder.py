"""
Memory Context Builder

Responsible for:
  - Building context snapshots for Brain prompt construction
  - Exporting memory state across all types
  - Filtering and ranking context

ContextBuilder does NOT:
  - Store memories (Engine does that)
  - Route requests (Router does that)
  - Analyze importance (Pipeline does that)
"""

import time
from typing import Any, Dict, List, Optional

from core.memory.types import MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend


class ContextBuilder:
    """
    Builds context snapshots for Brain.

    Usage:
        builder = ContextBuilder(backend=my_backend)
        context = builder.export()
        context = builder.export(memory_types=["user", "project"])
    """

    def __init__(self, backend=None):
        self._backend = backend or DictBackend()

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
        types_to_export = memory_types or list(MEMORY_TYPES)
        memories = {}
        total = 0

        for mt in types_to_export:
            records = self._backend.list_records(
                memory_type=mt, limit=limit_per_type
            )
            # filter expired
            live = [r.to_dict() for r in records if not r.is_expired()]
            if not include_metadata:
                for rec in live:
                    rec.pop("metadata", None)
            memories[mt] = live
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
        counts = {}
        for mt in MEMORY_TYPES:
            records = self._backend.list_records(memory_type=mt, limit=1000)
            live = [r for r in records if not r.is_expired()]
            counts[mt] = len(live)

        return {
            "timestamp": time.time(),
            "total_records": sum(counts.values()),
            "counts": counts,
        }
