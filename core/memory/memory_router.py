"""
Memory Router v2.2 — PURE SWITCH, nothing else.

The Router is a dumb switch. It receives a request,
looks at the source, and forwards it. That's it.

Architecture:
    Brain → Coordinator → Router → Pipeline → Repository → Backend

The Router does ONLY:
  1. Receive (source, message)
  2. Forward to the right handler

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

    def __init__(self, pipeline=None, coordinator=None):
        """
        Args:
            pipeline:    MemoryPipeline instance (for brain/tool requests)
            coordinator: MemoryCoordinator instance (for user messages)
        """
        self._pipeline = pipeline
        self._coordinator = coordinator

    def route(
        self,
        message: str,
        source: str = "brain",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Pure routing — no decisions, no record building.

        Args:
            message:  The content
            source:   Who sent this (brain / agent / tool / user)
            user_id:  Optional user identifier (only for source="user")

        Returns:
            Result dict from the handler.
        """
        if source == "user":
            return self._route_to_coordinator(message, user_id)
        else:
            # brain, tool, agent → all go to pipeline
            return self._route_to_pipeline(message)

    def _route_to_coordinator(self, message, user_id=None):
        """User messages → Coordinator."""
        if self._coordinator is None:
            return {"status": "error", "reason": "coordinator not wired"}
        return self._coordinator.process_message(
            user_id=user_id or "anonymous",
            message=message,
        )

    def _route_to_pipeline(self, message):
        """Brain/tool/agent → Pipeline."""
        if self._pipeline is None:
            return {"status": "error", "reason": "pipeline not wired"}
        return self._pipeline.process(text=message)
