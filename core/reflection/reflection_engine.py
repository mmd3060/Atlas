"""
Reflection Engine v1 — Analyzes outcomes and extracts lessons.

Flow:
  Decision → Action → Result → Reflection → Lesson → Memory

Usage:
    engine = ReflectionEngine(adapter=memory_adapter)
    result = engine.analyze(
        task="coding",
        decision={"provider": "github"},
        outcome="success",
        feedback="answer was helpful",
    )
    # {lesson, confidence, action}
"""

import time
from typing import Any, Dict, List, Optional

from core.reflection.experience_record import ExperienceRecord


class ReflectionEngine:
    """
    Analyzes outcomes and learns from experience.
    """

    def __init__(self, adapter=None):
        self._adapter = adapter
        self._experiences: List[ExperienceRecord] = []
        self._lessons: List[Dict] = []

    def analyze(
        self,
        task: str,
        decision: Dict[str, Any],
        outcome: str,
        feedback: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze an outcome and extract a lesson.

        Args:
            task:      What was the task
            decision:  What decision was made
            outcome:   success / failure / partial
            feedback:  User feedback

        Returns:
            {lesson, confidence, action, experience}
        """
        # ── Create experience record ──
        exp = ExperienceRecord(
            task=task,
            decision=decision,
            outcome=outcome,
            feedback=feedback,
        )
        self._experiences.append(exp)

        # ── Extract lesson ──
        lesson = self._extract_lesson(exp)

        # ── Store lesson ──
        self._lessons.append(lesson)

        # ── Store in memory if adapter available ──
        if self._adapter:
            self._store_lesson(lesson)

        return {
            "lesson": lesson["text"],
            "confidence": lesson["confidence"],
            "action": lesson["action"],
            "experience": exp.to_dict(),
        }

    def _extract_lesson(self, exp: ExperienceRecord) -> Dict[str, Any]:
        """Extract a lesson from an experience."""
        provider = exp.decision.get("provider", "unknown")
        is_success = exp.outcome == "success"

        if is_success:
            text = f"{provider} performs well for {exp.task}"
            confidence = 0.7
            action = f"boost {provider} for {exp.task}"
        else:
            text = f"{provider} failed for {exp.task}: {exp.feedback[:50]}"
            confidence = 0.6
            action = f"penalize {provider} for {exp.task}"

        # Boost confidence if we have multiple successes
        same_task = [e for e in self._experiences if e.task == exp.task and e.outcome == "success"]
        if len(same_task) >= 3:
            confidence = min(0.95, confidence + 0.15)

        return {
            "text": text,
            "confidence": round(confidence, 4),
            "action": action,
            "task": exp.task,
            "provider": provider,
            "outcome": exp.outcome,
            "timestamp": exp.timestamp,
        }

    def _store_lesson(self, lesson: Dict):
        """Store lesson in memory."""
        if self._adapter:
            self._adapter.remember(
                value=lesson["text"],
                memory_type="experience",
                importance=lesson["confidence"],
                tags=["reflection", lesson["task"]],
            )

    def get_lessons(self, task: Optional[str] = None) -> List[Dict]:
        """Get extracted lessons."""
        if task:
            return [l for l in self._lessons if l.get("task") == task]
        return list(self._lessons)

    def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect patterns across experiences."""
        patterns = []

        # Group by task
        by_task = {}
        for exp in self._experiences:
            if exp.task not in by_task:
                by_task[exp.task] = []
            by_task[exp.task].append(exp)

        for task, exps in by_task.items():
            successes = [e for e in exps if e.outcome == "success"]
            failures = [e for e in exps if e.outcome == "failure"]

            if len(successes) >= 2:
                # Find best provider
                providers = {}
                for e in successes:
                    p = e.decision.get("provider", "unknown")
                    providers[p] = providers.get(p, 0) + 1
                best = max(providers, key=providers.get) if providers else "unknown"
                patterns.append({
                    "task": task,
                    "pattern": f"best provider for {task} is {best}",
                    "confidence": min(0.9, 0.5 + len(successes) * 0.1),
                })

            if len(failures) >= 2:
                providers = {}
                for e in failures:
                    p = e.decision.get("provider", "unknown")
                    providers[p] = providers.get(p, 0) + 1
                worst = max(providers, key=providers.get) if providers else "unknown"
                patterns.append({
                    "task": task,
                    "pattern": f"avoid {worst} for {task}",
                    "confidence": min(0.9, 0.5 + len(failures) * 0.1),
                })

        return patterns

    def get_stats(self) -> Dict[str, Any]:
        """Get reflection statistics."""
        total = len(self._experiences)
        success_count = sum(1 for e in self._experiences if e.outcome == "success")
        failure_count = sum(1 for e in self._experiences if e.outcome == "failure")

        return {
            "total": total,
            "success_count": success_count,
            "failure_count": failure_count,
            "lessons_count": len(self._lessons),
            "success_rate": round(success_count / total, 4) if total > 0 else 0,
        }
