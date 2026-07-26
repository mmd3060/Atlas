"""
Memory Signal — Extracts decision-relevant signals from Memory.

Responsibilities:
  - Extract user preferences
  - Extract project context
  - Extract failure history
  - Extract successful models

Does NOT:
  - Make decisions (MemoryAwareEngine does that)
  - Store memories
"""

from typing import Any, Dict, List


class MemorySignal:
    """
    Extracts signals from Memory for Decision Engine.

    Usage:
        signal = MemorySignal(adapter=memory_adapter)
        signals = signal.extract("کد Python بنویس")
        # {user_preferences, project_context, history}
    """

    def __init__(self, adapter=None):
        self._adapter = adapter

    def extract(self, query: str) -> Dict[str, Any]:
        """
        Extract decision signals from memory.

        Args:
            query: User message

        Returns:
            {user_preferences, project_context, history}
        """
        if self._adapter is None:
            return self._empty()

        # ── User preferences ──
        pref_results = self._adapter.recall(query="user preference", limit=5)
        preferences = {}
        for r in pref_results:
            val = r.get("value", "").lower()
            if "فارسی" in val or "persian" in val:
                preferences["language"] = "fa"
            if "مفصل" in val or "detail" in val:
                preferences["detail_level"] = "high"
            if "کوتاه" in val or "short" in val:
                preferences["detail_level"] = "low"
            if "مثال" in val or "example" in val:
                preferences["style"] = "with_examples"

        # ── Project context ──
        proj_results = self._adapter.recall(query="project atlas", limit=3)
        project = {}
        for r in proj_results:
            val = r.get("value", "")
            if "atlas" in val.lower():
                project["active_project"] = "Atlas"
            if "stage" in val.lower() or "مرحله" in val:
                project["current_stage"] = val[:50]

        # ── Failure history ──
        fail_results = self._adapter.recall(query="failure error failed خطا", limit=5)
        failures = []
        for r in fail_results:
            val = r.get("value", "").lower()
            if "خطا" in val or "error" in val or "fail" in val:
                # Extract provider name
                for provider in ["gemini", "openrouter", "github", "nvidia"]:
                    if provider in val:
                        failures.append({"provider": provider, "reason": r.get("value", "")[:50]})

        return {
            "user_preferences": preferences,
            "project_context": project,
            "history": {"failures": failures},
        }

    def _empty(self):
        return {
            "user_preferences": {},
            "project_context": {},
            "history": {"failures": []},
        }
