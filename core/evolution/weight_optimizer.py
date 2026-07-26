"""
Weight Optimizer — Manages decision weights for evolution.

Responsibilities:
  - Store current weights
  - Update weights with bounds
  - Apply max change limit
"""

from typing import Dict


class WeightOptimizer:
    """
    Manages task-provider weights with safety bounds.

    Usage:
        optimizer = WeightOptimizer()
        optimizer.update(task="coding", provider="github", reward=0.9)
        weight = optimizer.get_weight("coding", "github")
    """

    MAX_CHANGE = 0.05  # Max change per update

    def __init__(self):
        self._weights: Dict[str, Dict[str, float]] = {}
        self._defaults: Dict[str, Dict[str, float]] = {}

    def get_weight(self, task: str, provider: str) -> float:
        """Get current weight for task-provider pair."""
        return self._weights.get(task, {}).get(provider, 0.5)

    def update(self, task: str, provider: str, reward: float) -> float:
        """
        Update weight based on reward.

        Args:
            task:     Task type
            provider: Provider name
            reward:   Reward signal (0-1)

        Returns:
            New weight
        """
        current = self.get_weight(task, provider)

        # Calculate change based on reward
        # reward > 0.5 → increase, reward < 0.5 → decrease
        raw_change = (reward - 0.5) * 0.2

        # Apply max change limit
        change = max(-self.MAX_CHANGE, min(self.MAX_CHANGE, raw_change))
        new_weight = max(0.1, min(1.0, current + change))

        # Store
        if task not in self._weights:
            self._weights[task] = {}
        self._weights[task][provider] = round(new_weight, 4)

        return new_weight

    def set_weight(self, task: str, provider: str, weight: float):
        """Directly set a weight (for rollback)."""
        if task not in self._weights:
            self._weights[task] = {}
        self._weights[task][provider] = round(weight, 4)

    def get_all_weights(self) -> Dict[str, Dict[str, float]]:
        """Get all weights."""
        return dict(self._weights)
