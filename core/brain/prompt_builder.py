"""
Prompt Builder — Constructs prompts with memory context.

Usage:
    builder = PromptBuilder()
    prompt = builder.build(message, memory_context, analysis)
    # {system_prompt, user_prompt, memory_injected}
"""

from typing import Any, Dict, List, Optional


class PromptBuilder:
    """
    Builds prompts with memory context injection.
    """

    def build(
        self,
        message: str,
        memory_context: Optional[Dict] = None,
        analysis: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Build a prompt with memory context.

        Args:
            message:         User message
            memory_context:  {memories, prompt_text, count}
            analysis:        {task_type, language, complexity}

        Returns:
            {system_prompt, user_prompt, memory_injected, total_length}
        """
        # ── System prompt ──
        system_parts = [
            "You are Atlas, an AI Operating System.",
            "You are helpful, knowledgeable, and direct.",
        ]

        if analysis:
            lang = analysis.get("language", "en")
            if lang == "fa":
                system_parts.append("Respond in Persian (Farsi).")

        # ── Memory injection ──
        memory_text = ""
        memory_injected = False

        if memory_context and memory_context.get("count", 0) > 0:
            memory_text = memory_context.get("prompt_text", "")
            if memory_text:
                system_parts.append(f"\n{memory_text}")
                memory_injected = True

        # ── User prompt ──
        user_prompt = message

        system_prompt = "\n".join(system_parts)

        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "memory_injected": memory_injected,
            "total_length": len(system_prompt) + len(user_prompt),
        }
