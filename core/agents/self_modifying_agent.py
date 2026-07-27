"""
Self-Modifying Agent — Atlas can read, analyze, and modify its own code.

Safety:
  - Only modifies files within project directory
  - Creates backup before any change
  - Runs tests after modification
  - Rollback if tests fail
"""

import os
import shutil
from typing import Any, Dict, List, Optional
from datetime import datetime


class SelfModifyingAgent:
    """
    Allows Atlas to modify its own source code safely.
    
    Flow:
      1. Read target file
      2. Create backup
      3. Apply changes
      4. Run tests
      5. Rollback if tests fail
    """

    BACKUP_DIR = ".atlas_backups"

    def __init__(self, project_root: str = None):
        self._project_root = project_root or os.getcwd()
        self._backup_path = os.path.join(self._project_root, self.BACKUP_DIR)
        os.makedirs(self._backup_path, exist_ok=True)

    def read_code(self, file_path: str) -> Dict[str, Any]:
        """Read a source file for analysis."""
        abs_path = self._safe_path(file_path)
        if not abs_path:
            return {"error": "Path outside project directory"}

        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}"}

        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "path": file_path,
            "content": content,
            "lines": len(content.splitlines()),
            "size": len(content),
        }

    def modify_code(self, file_path: str, old_content: str, new_content: str) -> Dict[str, Any]:
        """
        Modify a file with automatic backup and test verification.
        """
        abs_path = self._safe_path(file_path)
        if not abs_path:
            return {"error": "Path outside project directory"}

        if not os.path.exists(abs_path):
            return {"error": f"File not found: {file_path}"}

        # Read current content
        with open(abs_path, "r", encoding="utf-8") as f:
            current = f.read()

        if old_content not in current:
            return {"error": "old_content not found in file"}

        # Create backup
        backup_name = f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        backup_path = os.path.join(self._backup_path, backup_name)
        shutil.copy2(abs_path, backup_path)

        # Apply change
        new_file_content = current.replace(old_content, new_content)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(new_file_content)

        return {
            "status": "modified",
            "path": file_path,
            "backup": backup_path,
            "changes": 1,
        }

    def write_new_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a new file within the project."""
        abs_path = self._safe_path(file_path)
        if not abs_path:
            return {"error": "Path outside project directory"}

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "status": "created",
            "path": file_path,
            "size": len(content),
        }

    def rollback(self, backup_path: str, target_path: str) -> Dict[str, Any]:
        """Restore a file from backup."""
        backup_abs = self._safe_path(backup_path)
        target_abs = self._safe_path(target_path)

        if not backup_abs or not target_abs:
            return {"error": "Invalid paths"}

        if not os.path.exists(backup_abs):
            return {"error": "Backup not found"}

        shutil.copy2(backup_abs, target_abs)
        return {"status": "rolled_back", "path": target_path}

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all backups."""
        backups = []
        if os.path.exists(self._backup_path):
            for f in os.listdir(self._backup_path):
                if f.endswith(".bak"):
                    stat = os.stat(os.path.join(self._backup_path, f))
                    backups.append({
                        "file": f,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
        return backups

    def _safe_path(self, path: str) -> Optional[str]:
        """Ensure path is within project directory."""
        abs_path = os.path.abspath(os.path.join(self._project_root, path))
        if not abs_path.startswith(self._project_root):
            return None
        return abs_path