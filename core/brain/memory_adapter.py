"""
Brain Memory Adapter v1 — Bridge between Brain and Memory.

Brain uses:
  adapter.recall(query)          → relevant memories for reasoning
  adapter.remember(value, ...)   → store new memory
  adapter.get_context(query)     → full context for prompt
  adapter.get_user_profile()     → user preferences/history
  adapter.auto_remember(message) → automatic memory capture

Brain does NOT see Memory internals.

Usage:
    adapter = MemoryAdapter(backend=sqlite_backend)
    memories = adapter.recall("Atlas router")
    adapter.remember("user prefers Python", memory_type="user")
"""

import time
from typing import Any, Dict, List, Optional


class MemoryAdapter:
    """
    Clean bridge between Brain and Memory.

    Converts Memory Interface API to Brain-friendly format.
    """

    def __init__(self, backend=None):
        self._backend = backend
        self._memory = None
        self._initialized = False

    def _ensure_init(self):
        """Lazy init — hides Memory internals from Brain."""
        if self._initialized:
            return
        from core.memory.memory_interface import MemoryInterface
        self._memory = MemoryInterface(backend=self._backend)
        self._initialized = True

    # ═══════════════════════════════════════════════
    #  RECALL — Brain calls this before reasoning
    # ═══════════════════════════════════════════════

    def recall(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories for a query.

        Args:
            query:    What Brain is looking for
            limit:    Max memories to return
            min_score: Minimum relevance score

        Returns:
            List of {key, value, type, relevance}
        """
        self._ensure_init()
        results = self._memory.search(query=query, limit=limit)
        return [
            {
                "key": r["key"],
                "value": r["value"],
                "type": r["type"],
                "relevance": round(r["score"], 3),
            }
            for r in results
            if r["score"] >= min_score
        ]

    # ═══════════════════════════════════════════════
    #  REMEMBER — Brain calls this after learning
    # ═══════════════════════════════════════════════

    def remember(
        self,
        value: str,
        memory_type: str = "short",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Store a new memory.

        Args:
            value:        What to remember
            memory_type:  user/project/experience/knowledge/short/long
            importance:   How important (0-1)
            tags:         Optional tags

        Returns:
            {status, key, memory_type}
        """
        self._ensure_init()
        return self._memory.remember(
            value=value,
            memory_type=memory_type,
            importance=importance,
            tags=tags,
        )

    # ═══════════════════════════════════════════════
    #  GET_CONTEXT — Brain uses this for prompt
    # ═══════════════════════════════════════════════

    def get_context(self, query: str, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Get context for Brain prompt construction.

        Args:
            query:      What Brain needs context for
            max_tokens: Approximate token limit

        Returns:
            {memories, prompt_text, count}
        """
        self._ensure_init()
        ctx = self._memory.get_context(query=query, max_tokens=max_tokens)
        return {
            "memories": ctx["memories"],
            "prompt_text": self._format_prompt(ctx),
            "count": ctx["count"],
        }

    def _format_prompt(self, ctx: Dict) -> str:
        """Format memories as prompt text for Brain."""
        if not ctx["memories"]:
            return ""
        lines = ["[Memory Context]"]
        for m in ctx["memories"]:
            val = m["value"][:100] + "..." if len(m["value"]) > 100 else m["value"]
            lines.append(f"- {val}")
        return "\n".join(lines)

    # ═══════════════════════════════════════════════
    #  GET_USER_PROFILE — Brain uses for personalization
    # ═══════════════════════════════════════════════

    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile from memory."""
        self._ensure_init()
        results = self._memory.search(query="user preference", memory_types=["user"], limit=10)
        preferences = [r["value"] for r in results]

        name_results = self._memory.search(query="user name", memory_types=["user"], limit=3)
        name = name_results[0]["value"] if name_results else "Unknown"

        return {
            "name": name,
            "preferences": preferences,
        }

    # ═══════════════════════════════════════════════
    #  AUTO_REMEMBER — Automatic memory capture
    # ═══════════════════════════════════════════════

    def auto_remember(self, message: str) -> Dict[str, Any]:
        """
        Automatically decide what to remember from a message.

        Classifies the message and stores if important enough.
        """
        self._ensure_init()

        # Simple classification
        classification = self._classify(message)

        if classification["importance"] >= 0.5:
            result = self._memory.remember(
                value=message,
                memory_type=classification["type"],
                importance=classification["importance"],
                tags=classification["tags"],
            )
            return {
                "status": "stored",
                "memory_type": classification["type"],
                "importance": classification["importance"],
                "key": result.get("key"),
            }

        return {
            "status": "ignored",
            "reason": "importance too low",
            "importance": classification["importance"],
        }

    def _classify(self, message: str) -> Dict[str, Any]:
        """Simple rule-based classification."""
        msg_lower = message.lower()

        # User preference
        if any(w in msg_lower for w in ["دوست دارم", "ترجیح می", "می‌خواهم", "prefer", "like", "want"]):
            return {"type": "user", "importance": 0.8, "tags": ["preference"]}

        # Identity
        if any(w in msg_lower for w in ["اسم من", "من هستم", "my name", "i am"]):
            return {"type": "user", "importance": 0.9, "tags": ["identity"]}

        # Error
        if any(w in msg_lower for w in ["خطا", "error", "bug", "مشکل"]):
            return {"type": "experience", "importance": 0.7, "tags": ["error"]}

        # Project
        if any(w in msg_lower for w in ["پروژه", "project", "ساخت", "build"]):
            return {"type": "project", "importance": 0.6, "tags": ["project"]}

        # Default: short term
        return {"type": "short", "importance": 0.3, "tags": []}
