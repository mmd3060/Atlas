"""
Model Registry — Models with capabilities for Smart Router v2.

Each model has:
  - name, provider
  - coding, reasoning, math, text scores (0-1)
  - speed, cost scores (0-1)
  - max_tokens, supports_vision
"""

from typing import Any, Dict, List, Optional


class ModelProfile:
    """A single model's capabilities."""

    def __init__(
        self,
        name: str,
        provider: str,
        coding: float = 0.5,
        reasoning: float = 0.5,
        math: float = 0.5,
        text: float = 0.5,
        speed: float = 0.5,
        cost: float = 0.5,
        max_tokens: int = 4096,
        supports_vision: bool = False,
    ):
        self.name = name
        self.provider = provider
        self.coding = coding
        self.reasoning = reasoning
        self.math = math
        self.text = text
        self.speed = speed
        self.cost = cost
        self.max_tokens = max_tokens
        self.supports_vision = supports_vision

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "coding": self.coding,
            "reasoning": self.reasoning,
            "math": self.math,
            "text": self.text,
            "speed": self.speed,
            "cost": self.cost,
            "max_tokens": self.max_tokens,
            "supports_vision": self.supports_vision,
        }


class ModelRegistry:
    """
    Registry of all available models with capabilities.

    Usage:
        registry = ModelRegistry()
        models = registry.get_for_task("coding")
    """

    def __init__(self):
        self._models: List[ModelProfile] = []
        self._load_defaults()

    def _load_defaults(self):
        """Load default model profiles."""
        self._models = [
            ModelProfile(
                name="llama-3.3-70b", provider="openrouter",
                coding=0.85, reasoning=0.80, math=0.75, text=0.80,
                speed=0.70, cost=0.95, max_tokens=8192,
            ),
            ModelProfile(
                name="claude-3.5-sonnet", provider="openrouter",
                coding=0.92, reasoning=0.90, math=0.85, text=0.88,
                speed=0.65, cost=0.60, max_tokens=8192,
            ),
            ModelProfile(
                name="gpt-4o", provider="openrouter",
                coding=0.90, reasoning=0.88, math=0.88, text=0.85,
                speed=0.60, cost=0.50, max_tokens=128000,
            ),
            ModelProfile(
                name="gemini-2.0-flash", provider="gemini",
                coding=0.70, reasoning=0.72, math=0.70, text=0.75,
                speed=0.95, cost=0.90, max_tokens=32000,
            ),
            ModelProfile(
                name="deepseek-coder", provider="openrouter",
                coding=0.88, reasoning=0.75, math=0.70, text=0.72,
                speed=0.75, cost=0.85, max_tokens=16000,
            ),
            ModelProfile(
                name="gemini-pro", provider="gemini",
                coding=0.75, reasoning=0.78, math=0.75, text=0.80,
                speed=0.80, cost=0.70, max_tokens=32000,
                supports_vision=True,
            ),
        ]

    def get_all(self) -> List[ModelProfile]:
        return list(self._models)

    def get_model(self, name: str) -> Optional[ModelProfile]:
        for m in self._models:
            if m.name == name:
                return m
        return None

    def get_for_task(self, task_type: str) -> List[ModelProfile]:
        """Get models sorted by relevance for a task type."""
        attr_map = {
            "code": "coding",
            "coding": "coding",
            "math": "math",
            "text": "text",
            "writing": "text",
            "reasoning": "reasoning",
        }
        attr = attr_map.get(task_type, "reasoning")
        return sorted(self._models, key=lambda m: getattr(m, attr, 0.5), reverse=True)

    def register(self, model: ModelProfile):
        """Register a new model."""
        self._models.append(model)
