"""
Tool Executor — Safe execution of system operations.
"""

import os
import subprocess
import json
from typing import Any, Dict, List, Optional


class ToolExecutor:
    """Executes tools safely with proper error handling."""

    def execute(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments."""
        
        if tool_name == "terminal":
            return self._execute_terminal(args)
        elif tool_name == "file_read":
            return self._execute_file_read(args)
        elif tool_name == "file_write":
            return self._execute_file_write(args)
        elif tool_name == "list_files":
            return self._execute_list_files(args)
        elif tool_name == "memory_status":
            return self._execute_memory_status(args)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _execute_terminal(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a terminal command safely."""
        command = args.get("command", "")
        if not command:
            return {"error": "No command provided"}
        
        try:
            # Use current working directory
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=os.getcwd()
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out (30s)"}
        except Exception as e:
            return {"error": str(e)}

    def _execute_file_read(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file safely."""
        path = args.get("path", "")
        if not path:
            return {"error": "No path provided"}
        
        try:
            # Ensure path is relative and safe
            abs_path = os.path.abspath(path)
            cwd = os.getcwd()
            
            # Ensure we're within the project directory
            if not abs_path.startswith(cwd):
                return {"error": "Path outside project directory not allowed"}
            
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "path": path}
        except FileNotFoundError:
            return {"error": f"File not found: {path}"}
        except Exception as e:
            return {"error": str(e)}

    def _execute_file_write(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file."""
        path = args.get("path", "")
        content = args.get("content", "")
        
        if not path:
            return {"error": "No path provided"}
        
        try:
            abs_path = os.path.abspath(path)
            cwd = os.getcwd()
            
            if not abs_path.startswith(cwd):
                return {"error": "Path outside project directory not allowed"}
            
            # Create directory if needed
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return {"status": "written", "path": path, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}

    def _execute_list_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List files in a directory."""
        path = args.get("path", ".")
        
        try:
            abs_path = os.path.abspath(path)
            cwd = os.getcwd()
            
            if not abs_path.startswith(cwd):
                return {"error": "Path outside project directory not allowed"}
            
            files = []
            for item in os.listdir(abs_path):
                item_path = os.path.join(abs_path, item)
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "path": os.path.join(path, item),
                    "is_dir": os.path.isdir(item_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })
            
            return {"files": files, "path": path, "count": len(files)}
        except Exception as e:
            return {"error": str(e)}

    def _execute_memory_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory system status."""
        try:
            from core.memory.backends.sqlite_backend import SQLiteBackend
            from core.memory.memory_repository import MemoryRepository
            
            backend = SQLiteBackend(db_path="atlas_memory.db")
            backend.open()
            repo = MemoryRepository(backend=backend)
            
            count = repo.count()
            stats = repo.get_stats() if hasattr(repo, 'get_stats') else {}
            
            backend.close()
            
            return {
                "total_memories": count,
                "stats": stats,
                "backend": "SQLite",
            }
        except Exception as e:
            return {"error": f"Memory check failed: {str(e)}"}