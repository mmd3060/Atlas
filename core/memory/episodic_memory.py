"""
Episodic Memory — Events and experiences with temporal context.

Memory of "what happened when" — like a diary.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Episode:
    """A single episodic memory."""
    timestamp: str
    event_type: str          # conversation, action, observation, decision
    content: str             # what happened
    context: Dict[str, Any]  # who, where, why
    importance: float = 0.5  # 0-1
    tags: List[str] = field(default_factory=list)
    outcome: str = ""        # what resulted
    episode_id: str = ""


class EpisodicMemory:
    """
    Stores and retrieves episodic memories.
    
    Usage:
        memory = EpisodicMemory()
        memory.record_event("conversation", "User asked about Python", {"user": "MMD"})
        episodes = memory.recall("Python")
    """

    def __init__(self, adapter=None):
        self._adapter = adapter
        self._episodes: List[Episode] = []

    def record_event(
        self,
        event_type: str,
        content: str,
        context: Dict[str, Any],
        importance: float = 0.5,
        tags: List[str] = None,
        outcome: str = ""
    ) -> Episode:
        """Record a new episodic memory."""
        episode = Episode(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            content=content,
            context=context,
            importance=importance,
            tags=tags or [],
            outcome=outcome,
        )
        self._episodes.append(episode)
        
        # Store in persistent backend if available
        if self._adapter:
            self._persist(episode)
        
        return episode

    def recall(self, query: str, limit: int = 10) -> List[Episode]:
        """Recall episodes matching query."""
        query_lower = query.lower()
        matches = []
        
        for ep in self._episodes:
            score = 0
            if query_lower in ep.content.lower():
                score += 10
            if any(query_lower in tag.lower() for tag in ep.tags):
                score += 5
            if any(query_lower in str(v).lower() for v in ep.context.values()):
                score += 3
            
            if score > 0:
                matches.append((ep, score))
        
        # Sort by relevance and recency
        matches.sort(key=lambda x: (x[1], x[0].timestamp), reverse=True)
        return [ep for ep, _ in matches[:limit]]

    def get_recent(self, hours: int = 24) -> List[Episode]:
        """Get recent episodes."""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            ep for ep in self._episodes
            if datetime.fromisoformat(ep.timestamp) > cutoff
        ]

    def _persist(self, episode: Episode):
        """Persist to memory backend."""
        if self._adapter:
            self._adapter.remember(
                value=f"[{episode.event_type}] {episode.content} | Outcome: {episode.outcome}",
                memory_type="episodic",
                importance=episode.importance,
                tags=["episodic", episode.event_type] + episode.tags,
            )