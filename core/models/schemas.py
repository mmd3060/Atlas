from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ModelCapabilities:
    """
    توانایی‌های یک مدل هوش مصنوعی
    """

    coding: float = 0.0
    math: float = 0.0
    text: float = 0.0
    vision: float = 0.0
    reasoning: float = 0.0
    multilingual: float = 0.0


@dataclass
class ModelProfile:
    """
    پروفایل کامل یک مدل برای Atlas OS

    Atlas فقط این را می‌شناسد،
    نه Provider را.
    """

    name: str

    capabilities: ModelCapabilities

    context_window: int = 0

    speed: float = 0.5

    cost: float = 0.5

    providers: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)


    def capability_score(self, task: str) -> float:
        """
        امتیاز مدل برای یک وظیفه
        """

        mapping = {
            "code": self.capabilities.coding,
            "coding": self.capabilities.coding,

            "math": self.capabilities.math,

            "text": self.capabilities.text,
            "writing": self.capabilities.text,

            "vision": self.capabilities.vision,

            "reasoning": self.capabilities.reasoning,
        }


        return mapping.get(
            task,
            self.capabilities.reasoning
        )


    def to_dict(self):
        return {

            "name": self.name,

            "capabilities": {

                "coding": self.capabilities.coding,
                "math": self.capabilities.math,
                "text": self.capabilities.text,
                "vision": self.capabilities.vision,
                "reasoning": self.capabilities.reasoning,
                "multilingual": self.capabilities.multilingual,

            },

            "context_window": self.context_window,

            "speed": self.speed,

            "cost": self.cost,

            "providers": self.providers,

            "tags": self.tags,

        }
