"""
Agent Orchestrator — Breaks complex goals into sub-tasks and dispatches to agents.

Flow:
    User Goal → Decompose → Assign Agents → Execute → Synthesize → Result

Example:
    Goal: "Build a REST API for user management"
    → Planner: breaks into 4 sub-tasks
    → Coder: writes code for each
    → Reviewer: reviews code
    → Researcher: finds best practices
    → Synthesized result
"""

from typing import Any, Dict, List, Optional
from core.agents.agent_manager import AgentManager


class AgentOrchestrator:
    """
    Orchestrates multiple agents to solve complex goals.
    """

    def __init__(self):
        self._agent_manager = AgentManager()
        self._max_sub_tasks = 5

    def solve(self, goal: str) -> Dict[str, Any]:
        """
        Break a complex goal into sub-tasks and dispatch to agents.
        """
        # Step 1: Decompose goal into sub-tasks
        sub_tasks = self._decompose(goal)

        # Step 2: Assign each sub-task to the best agent
        results = []
        for task in sub_tasks:
            agent_name = self._pick_agent(task)
            result = self._agent_manager.dispatch(agent_name, task)
            results.append({
                "task": task,
                "agent": agent_name,
                "result": result,
            })

        # Step 3: Synthesize final result
        final = self._synthesize(results)

        return {
            "goal": goal,
            "sub_tasks": sub_tasks,
            "results": results,
            "final": final,
            "status": "completed",
        }

    def _decompose(self, goal: str) -> List[str]:
        """
        Break a complex goal into smaller sub-tasks.
        
        Uses simple heuristics for v1. In v2, this will use an LLM.
        """
        tasks = []
        goal_lower = goal.lower()

        # Coding tasks
        if any(w in goal_lower for w in ["build", "create", "make", "بنویس", "بساز"]):
            tasks.append("Plan the architecture and file structure")
            tasks.append("Write the core implementation code")
            tasks.append("Research best practices and patterns")
            tasks.append("Review the code for bugs and improvements")

        # Analysis tasks
        elif any(w in goal_lower for w in ["analyze", "تحلیل", "بررسی", "study"]):
            tasks.append("Research the topic and gather information")
            tasks.append("Analyze findings and identify patterns")
            tasks.append("Plan recommendations based on analysis")

        # Debug tasks
        elif any(w in goal_lower for w in ["fix", "debug", "اصلاح", "باگ"]):
            tasks.append("Read and understand the problematic code")
            tasks.append("Identify the root cause of the issue")
            tasks.append("Write the fix and verify it")

        # Default: single task
        else:
            tasks.append(f"Process: {goal}")

        return tasks[:self._max_sub_tasks]

    def _pick_agent(self, task: str) -> str:
        """Pick the best agent for a sub-task."""
        task_lower = task.lower()

        if any(w in task_lower for w in ["plan", "architecture", "طرح", "معماری"]):
            return "planner"
        elif any(w in task_lower for w in ["write", "code", "implement", "بنویس", "کد"]):
            return "coder"
        elif any(w in task_lower for w in ["research", "find", "جستجو", "تحقیق"]):
            return "researcher"
        elif any(w in task_lower for w in ["review", "check", "بررسی", "بازبینی"]):
            return "reviewer"
        return "coder"  # default

    def _synthesize(self, results: List[Dict]) -> str:
        """Combine agent results into a final answer."""
        lines = ["🎯 Orchestrated Solution:\n"]
        for r in results:
            lines.append(f"  [{r['agent'].upper()}] {r['task']}")
            lines.append(f"    → {r['result']}")
        return "\n".join(lines)
