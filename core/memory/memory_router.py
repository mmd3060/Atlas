"""
Memory Router v2.2 — PURE SWITCH, nothing else.

The Router is a dumb switch. It receives a request,
looks at the source, and forwards it. That's it.

Architecture:
    Brain → Router → Pipeline → Repository → Backend

The Router does ONLY:
  1. Receive (source, message)
  2. Forward to Pipeline

The Router does NOT:
  - Build MemoryRecords
  - Calculate importance
  - Check policies
  - Build context
  - Process messages
  - Know about MemoryRecord, Policy, or Backend
"""

from typing import Any, Dict, Optional


class MemoryRouter:
    """
    Pure switch — no logic, no state, no decisions.

    Usage:
        router = MemoryRouter(pipeline=my_pipeline)
        result = router.route("hello", source="brain")
    """

    def __init__(self, pipeline=None):
        """
        Args:
            pipeline: MemoryPipeline instance (for brain/tool/agent requests)
        """
        self._pipeline = pipeline

    def route(
        self,
        message: str,
        source: str = "brain",
    ) -> Dict[str, Any]:
        """
        Pure routing — no decisions, no record building.

        Args:
            message:  The content
            source:   Who sent this (brain / agent / tool)

        Returns:
            Result dict from the Pipeline.
        """
        # All sources go to Pipeline
        if self._pipeline is None:
            return {"status": "error", "reason": "pipeline not wired"}
        return self._pipeline.process(text=message)
