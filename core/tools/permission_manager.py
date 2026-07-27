"""
Permission Manager — Safety layer for tool execution.

Categories:
  - SAFE: read-only operations (file_read, ls, cat)
  - MODERATE: write operations (file_write, mkdir)
  - DANGEROUS: destructive operations (rm, kill, sudo)

Usage:
    manager = PermissionManager()
    if manager.is_allowed("terminal", {"command": "ls"}):
        # execute
"""

from typing import Any, Dict, List, Optional


class PermissionManager:
    """
    Safety layer for Atlas OS Tool System.
    """

    SAFE_TOOLS = ["file_read", "list_files", "status"]
    
    MODERATE_TOOLS = ["file_write", "mkdir", "touch"]
    
    DANGEROUS_PATTERNS = [
        "rm -rf", "sudo", "chmod 777", "kill -9",
        "shutdown", "reboot", "dd if=", "mkfs",
        "> /dev/", "curl | bash", "wget | bash",
    ]

    def __init__(self, auto_approve_safe: bool = True):
        self._auto_approve_safe = auto_approve_safe
        self._pending_approvals: List[Dict] = []

    def check_permission(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a tool execution is allowed.
        
        Returns:
            {allowed, level, reason}
        """
        # Safe tools - auto-approve
        if tool_name in self.SAFE_TOOLS:
            return {
                "allowed": self._auto_approve_safe,
                "level": "safe",
                "reason": "read-only operation",
            }

        # Check dangerous patterns in terminal commands
        if tool_name == "terminal":
            command = args.get("command", "")
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern in command.lower():
                    return {
                        "allowed": False,
                        "level": "dangerous",
                        "reason": f"blocked pattern: {pattern}",
                    }
            
            # Moderate: write commands
            if any(w in command for w in ["write", "create", "mkdir", "touch", "echo"]):
                return {
                    "allowed": True,
                    "level": "moderate",
                    "reason": "write operation (auto-approved in dev mode)",
                }
            
            # Default terminal = moderate
            return {
                "allowed": True,
                "level": "moderate",
                "reason": "terminal command",
            }

        # Moderate tools
        if tool_name in self.MODERATE_TOOLS:
            return {
                "allowed": True,
                "level": "moderate",
                "reason": "write operation",
            }

        # Unknown tool
        return {
            "allowed": False,
            "level": "unknown",
            "reason": f"unknown tool: {tool_name}",
        }

    def request_approval(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Request user approval for dangerous operations."""
        approval_id = f"approval_{len(self._pending_approvals)}"
        self._pending_approvals.append({
            "id": approval_id,
            "tool": tool_name,
            "args": args,
        })
        return approval_id

    def get_pending(self) -> List[Dict]:
        """Get pending approval requests."""
        return list(self._pending_approvals)

    def approve(self, approval_id: str) -> bool:
        """Approve a pending request."""
        for i, req in enumerate(self._pending_approvals):
            if req["id"] == approval_id:
                self._pending_approvals.pop(i)
                return True
        return False
