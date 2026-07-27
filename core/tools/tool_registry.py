"""
Tool Registry — Manages registered tools.
"""

from typing import Dict, List, Optional
from core.tools.tool_executor import ToolExecutor

class ToolRegistry:
    """Registry for available tools."""
    
    def __init__(self):
        self._tools = ["terminal", "file_read"]
        self._executor = ToolExecutor()

    def get_available_tools(self) -> List[str]:
        return self._tools

    def execute_tool(self, tool_name: str, args: Dict) -> Any:
        if tool_name not in self._tools:
            return {"error": "Tool not allowed"}
        return self._executor.execute(tool_name, args)
