"""
Tool Integration — Connects ReasoningPipeline to ToolExecutor.

Flow:
    User Message -> Brain Reasoning -> Tool Detection -> Tool Execution -> Result -> Response
"""

from typing import Any, Dict, List, Optional
from core.tools.tool_registry import ToolRegistry


class ToolIntegration:
    """Connects Reasoning Pipeline to Tools."""
    
    def __init__(self):
        self._registry = ToolRegistry()

    def process(self, reasoning_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if reasoning requires a tool, execute it if so.
        """
        # ساده‌سازی: اگر مدل خواست از ابزار استفاده کنه (بر اساس تحلیل)
        # در اینجا ما یک لایه چک‌کننده داریم
        
        # شناسایی نیاز به ابزار از تصمیم (اینجا باید با مدل هماهنگ بشه)
        task_type = reasoning_output.get("analysis", {}).get("task_type")
        
        # فعلاً برای تست، اگر task_type ابزار بخواد
        if task_type == "coding" and "tools" in reasoning_output:
            tool_name = reasoning_output["tools"].get("name")
            args = reasoning_output["tools"].get("args")
            return self._registry.execute_tool(tool_name, args)
            
        return {"status": "no_tool_needed"}
