"""
Multi-Agent System for Atlas OS.
"""

from typing import List, Dict, Any


class Agent:
    """A specialist agent."""
    def __init__(self, name: str, role: str, tools: List[str]):
        self.name = name
        self.role = role
        self.tools = tools

    def process(self, message: str) -> str:
        return f"[{self.name}]: Processing '{message[:50]}...' using tools: {', '.join(self.tools)}"


class AgentManager:
    """Orchestrates a team of agents."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {
            "coder": Agent("Atlas Coder", "writes and debugs code", ["terminal", "file_read", "file_write"]),
            "researcher": Agent("Atlas Researcher", "searches and gathers info", ["terminal", "file_read"]),
            "planner": Agent("Atlas Planner", "breaks down complex goals", ["file_read"]),
            "reviewer": Agent("Atlas Reviewer", "reviews and improves code", ["file_read"]),
        }

    def dispatch(self, task_type: str, message: str) -> str:
        agent = self.agents.get(task_type, self.agents["coder"])
        return agent.process(message)

    def list_agents(self) -> Dict[str, Dict]:
        return {
            name: {"role": a.role, "tools": a.tools}
            for name, a in self.agents.items()
        }