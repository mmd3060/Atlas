"""
Response Memory — Stores responses in memory for future reference.

Usage:
    resp_mem = ResponseMemory(adapter=memory_adapter)
    result = resp_mem.remember_response(message, response, metadata)
"""

from typing import Any, Dict, Optional


class ResponseMemory:
    """
    Stores responses in memory.
    """

    def __init__(self, adapter=None):
        self._adapter = adapter

    def remember_response(
        self,
        message: str,
        response: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Store a response in memory.

        Args:
            message:  Original user message
            response: The response given
            metadata: Additional context

        Returns:
            {status, key}
        """
        if self._adapter is None:
            return {"status": "no_adapter", "key": None}

        metadata = metadata or {}
        task_type = metadata.get("task_type", "general")

        # Store the interaction
        value = f"User: {message[:100]}\nResponse: {response[:200]}"
        result = self._adapter.remember(
            value=value,
            memory_type="experience",
            importance=0.5,
            tags=["response", task_type],
        )

        return {
            "status": "stored",
            "key": result.get("key"),
        }
