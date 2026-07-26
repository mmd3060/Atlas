"""
Brain Reasoning Pipeline v1 — The heart of Atlas.

Flow:
  User Message → Input Analyzer → Memory Recall → Decision Engine
  → Prompt Builder → Response → Auto Remember

Usage:
    pipeline = ReasoningPipeline(adapter=memory_adapter)
    result = pipeline.process("ادامه پروژه Atlas")
    # {analysis, memory_context, prompt, decision, response}
"""

from typing import Any, Dict, Optional

from core.brain.input_analyzer import InputAnalyzer
from core.brain.prompt_builder import PromptBuilder
from core.brain.response_memory import ResponseMemory
from core.brain.memory_context import MemoryContext


class ReasoningPipeline:
    """
    The full reasoning flow for Atlas.
    """

    def __init__(self, adapter=None):
        self._adapter = adapter
        self._analyzer = InputAnalyzer()
        self._memory_context = MemoryContext(adapter=adapter) if adapter else None
        self._prompt_builder = PromptBuilder()
        self._response_memory = ResponseMemory(adapter=adapter) if adapter else None

    def process(
        self,
        message: str,
        skip_llm: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a user message through the full reasoning pipeline.

        Args:
            message:  User message
            skip_llm: Skip actual LLM call (for testing)

        Returns:
            {analysis, memory_context, prompt, decision, response}
        """
        # ── Step 1: Analyze input ──
        analysis = self._analyzer.analyze(message)

        # ── Step 2: Recall relevant memories ──
        memory_ctx = {}
        if self._memory_context:
            memory_ctx = self._memory_context.build(message)

        # ── Step 3: Build prompt with memory ──
        prompt = self._prompt_builder.build(
            message=message,
            memory_context=memory_ctx,
            analysis=analysis,
        )

        # ── Step 4: Make decision (simplified) ──
        decision = self._make_decision(analysis)

        # ── Step 5: Get response (skip LLM for testing) ──
        response = None
        if not skip_llm:
            response = self._get_response(prompt)

        # ── Step 6: Remember the interaction ──
        if self._response_memory and response:
            self._response_memory.remember_response(
                message=message,
                response=str(response),
                metadata={"task_type": analysis.get("task_type")},
            )

        return {
            "analysis": analysis,
            "memory_context": memory_ctx,
            "prompt": prompt,
            "decision": decision,
            "response": response,
        }

    def _make_decision(self, analysis: Dict) -> Dict[str, Any]:
        """Make a routing decision based on analysis."""
        task_type = analysis.get("task_type", "general")
        complexity = analysis.get("complexity", "medium")

        # Simple decision rules
        if task_type == "coding":
            provider = "github"
            model = "llama-3.3-70b"
        elif task_type == "math":
            provider = "openrouter"
            model = "claude-3.5-sonnet"
        elif complexity == "high":
            provider = "openrouter"
            model = "gpt-4o"
        else:
            provider = "openrouter"
            model = "llama-3.3-70b"

        return {
            "provider": provider,
            "model": model,
            "task_type": task_type,
        }

    def _get_response(self, prompt: Dict) -> str:
        """Get response from LLM (placeholder)."""
        return f"[Response to: {prompt.get('user_prompt', '')[:50]}]"
