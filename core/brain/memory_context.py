"""
Brain Memory Injection v1 — Injects relevant memories into Brain's reasoning.

Flow:
  User Message → MemoryContext → Memory Adapter → Relevant Memories → Prompt

Responsibilities:
  - Extract query from user message
  - Fetch relevant memories via Adapter
  - Sort by importance
  - Limit token count
  - Format for Brain prompt

Does NOT:
  - Store memories
  - Make decisions
  - Access Backend directly
"""

from typing import Any, Dict, List, Optional


class MemoryContext:
    """
    Injects relevant memories into Brain's reasoning process.

    Usage:
        context = MemoryContext(adapter=memory_adapter)
        result = context.build("ادامه پروژه Atlas")
        # {memories, prompt_text, count, approx_tokens}
    """

    def __init__(self, adapter=None, max_items: int = 10):
        """
        Args:
            adapter:   MemoryAdapter instance
            max_items: Max memories to fetch
        """
        self._adapter = adapter
        self._max_items = max_items

    def build(
        self,
        message: str,
        max_tokens: int = 500,
        max_items: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Build memory context for Brain.

        Args:
            message:    User message to get context for
            max_tokens: Approximate token limit for prompt
            max_items:  Override max items

        Returns:
            {memories, prompt_text, count, approx_tokens}
        """
        if self._adapter is None:
            return self._empty_result()

        # ── Step 1: Recall relevant memories ──
        items = max_items or self._max_items
        memories = self._adapter.recall(query=message, limit=items)

        # ── Step 2: Sort by importance (descending) ──
        memories.sort(key=lambda m: m.get("relevance", 0), reverse=True)

        # ── Step 3: Apply token limit ──
        selected, approx_tokens = self._apply_token_limit(memories, max_tokens)

        # ── Step 4: Format prompt ──
        prompt_text = self._format_prompt(selected)

        return {
            "memories": selected,
            "prompt_text": prompt_text,
            "count": len(selected),
            "approx_tokens": approx_tokens,
        }

    def _apply_token_limit(
        self,
        memories: List[Dict],
        max_tokens: int,
    ) -> tuple:
        """Select memories within token budget."""
        selected = []
        total_chars = 0
        # Rough estimate: 1 token ≈ 4 chars
        max_chars = max_tokens * 4

        for mem in memories:
            text = str(mem.get("value", ""))
            chars = len(text)

            if total_chars + chars > max_chars:
                break

            selected.append(mem)
            total_chars += chars

        return selected, total_chars // 4

    def _format_prompt(self, memories: List[Dict]) -> str:
        """Format memories as prompt text for Brain."""
        if not memories:
            return ""

        lines = ["[Memory Context]"]
        for m in memories:
            val = m.get("value", "")
            val = val[:120] + "..." if len(val) > 120 else val
            lines.append(f"- {val}")

        return "\n".join(lines)

    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result when no adapter."""
        return {
            "memories": [],
            "prompt_text": "",
            "count": 0,
            "approx_tokens": 0,
        }
