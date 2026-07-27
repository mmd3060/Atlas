"""
Tool System — Atlas OS Tools Layer v1.

A complete tool system with:
  - Tool Registration
  - Permission Manager (Safety)
  - Tool Executor (Execution)
"""

from typing import Any, Dict, List
from core.tools.tool_executor import ToolExecutor
from core.tools.permission_manager import PermissionManager
from core.tools.image_editor import ImageEditor


class ToolSystem:
    """
    Central tool system for Atlas OS.
    Bridges Brain and Tools safely.
    """
    
    def __init__(self):
        self._executor = ToolExecutor()
        self._permission = PermissionManager()
        self._image_editor = ImageEditor()
        
        # Register available tools
        self._tools: Dict[str, Dict] = {
            "terminal": {
                "description": "Execute terminal commands safely",
                "level": "moderate",
                "category": "system",
            },
            "file_read": {
                "description": "Read file contents",
                "level": "safe",
                "category": "files",
            },
            "file_write": {
                "description": "Write content to files",
                "level": "moderate",
                "category": "files",
            },
            "list_files": {
                "description": "List files in a directory",
                "level": "safe",
                "category": "files",
            },
            "memory_status": {
                "description": "Check Atlas memory system status",
                "level": "safe",
                "category": "system",
            },
            "remove_background": {
                "description": "Remove background from an image",
                "level": "moderate",
                "category": "vision",
            },
        }

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Safe tool execution with permission check."""
        
        # Check permissions
        perm = self._permission.check_permission(tool_name, args)
        
        if not perm["allowed"]:
            return {
                "status": "blocked",
                "reason": perm["reason"],
                "level": perm["level"],
            }
        
        # Execute
        if tool_name == "remove_background":
            result = self._image_editor.remove_background(
                image_path=args.get("path", ""),
                output_path=args.get("output_path")
            )
        else:
            result = self._executor.execute(tool_name, args)
        
        return {
            "status": "success" if "error" not in result else "error",
            "tool": tool_name,
            "result": result,
            "permission_level": perm["level"],
        }

    def list_tools(self) -> Dict[str, Dict]:
        """List all registered tools."""
        return dict(self._tools)

    def get_tool(self, tool_name: str) -> Dict[str, Any]:
        """Get tool info."""
        return self._tools.get(tool_name, {})
