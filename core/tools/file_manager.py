"""
File Manager — Advanced file operations for Atlas OS.
"""

import os
import shutil
import glob
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class FileManager:
    """
    Advanced file operations:
    - search: find files by pattern
    - read/write: standard IO
    - copy/move/delete: file management
    - info: file metadata
    - tree: directory structure
    """

    def __init__(self, root: str = None):
        self._root = root or os.getcwd()

    def search(self, pattern: str, path: str = None) -> Dict[str, Any]:
        """Search files by glob pattern."""
        search_path = path or self._root
        try:
            full_pattern = os.path.join(search_path, pattern)
            matches = glob.glob(full_pattern, recursive=True)
            files = []
            for m in matches[:50]:
                stat = os.stat(m)
                files.append({
                    "path": os.path.relpath(m, self._root),
                    "is_dir": os.path.isdir(m),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            return {"files": files, "count": len(files), "pattern": pattern}
        except Exception as e:
            return {"error": str(e), "files": [], "count": 0}

    def read_file(self, path: str) -> Dict[str, Any]:
        """Read file content with line numbers."""
        abs_path = self._safe_path(path)
        if not abs_path:
            return {"error": "Path outside project"}
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            content = "".join(lines)
            return {
                "path": path,
                "content": content,
                "lines": len(lines),
                "size": len(content),
            }
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        abs_path = self._safe_path(path)
        if not abs_path:
            return {"error": "Path outside project"}
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"status": "written", "path": path, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}

    def copy_file(self, source: str, dest: str) -> Dict[str, Any]:
        """Copy a file."""
        src = self._safe_path(source)
        dst = self._safe_path(dest)
        if not src or not dst:
            return {"error": "Path outside project"}
        try:
            shutil.copy2(src, dst)
            return {"status": "copied", "source": source, "dest": dest}
        except Exception as e:
            return {"error": str(e)}

    def move_file(self, source: str, dest: str) -> Dict[str, Any]:
        """Move a file."""
        src = self._safe_path(source)
        dst = self._safe_path(dest)
        if not src or not dst:
            return {"error": "Path outside project"}
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            return {"status": "moved", "source": source, "dest": dest}
        except Exception as e:
            return {"error": str(e)}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file (moved to trash conceptually, but actually deleted)."""
        abs_path = self._safe_path(path)
        if not abs_path:
            return {"error": "Path outside project"}
        try:
            if os.path.isfile(abs_path):
                os.remove(abs_path)
                return {"status": "deleted", "path": path}
            elif os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
                return {"status": "deleted_dir", "path": path}
            return {"error": "File not found"}
        except Exception as e:
            return {"error": str(e)}

    def file_info(self, path: str) -> Dict[str, Any]:
        """Get detailed file information."""
        abs_path = self._safe_path(path)
        if not abs_path:
            return {"error": "Path outside project"}
        try:
            stat = os.stat(abs_path)
            return {
                "path": path,
                "is_file": os.path.isfile(abs_path),
                "is_dir": os.path.isdir(abs_path),
                "size": stat.st_size,
                "size_human": self._human_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
            }
        except Exception as e:
            return {"error": str(e)}

    def directory_tree(self, path: str = None, max_depth: int = 3) -> Dict[str, Any]:
        """Generate directory tree."""
        target = self._safe_path(path or ".")
        if not target:
            return {"error": "Path outside project"}
        try:
            tree = {"name": os.path.basename(target), "type": "dir", "children": []}
            self._build_tree(target, tree["children"], max_depth, 0)
            return tree
        except Exception as e:
            return {"error": str(e)}

    def _build_tree(self, path: str, children: List, max_depth: int, current_depth: int):
        if current_depth >= max_depth:
            return
        try:
            items = sorted(os.listdir(path))
            for item in items:
                full = os.path.join(path, item)
                node = {"name": item, "type": "dir" if os.path.isdir(full) else "file"}
                if os.path.isdir(full):
                    node["children"] = []
                    self._build_tree(full, node["children"], max_depth, current_depth + 1)
                else:
                    node["size"] = os.path.getsize(full)
                children.append(node)
        except PermissionError:
            pass

    def grep(self, pattern: str, path: str = None, file_glob: str = "*.py") -> Dict[str, Any]:
        """Search file contents (like grep)."""
        import re
        search_path = path or self._root
        matches = []
        try:
            for root, dirs, files in os.walk(search_path):
                # Skip hidden dirs and __pycache__
                dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
                for fname in files:
                    if glob.fnmatch.fnmatch(fname, file_glob):
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                                for i, line in enumerate(f, 1):
                                    if re.search(pattern, line):
                                        matches.append({
                                            "file": os.path.relpath(fpath, self._root),
                                            "line": i,
                                            "content": line.strip()[:120],
                                        })
                        except Exception:
                            pass
                if len(matches) > 100:
                    break
        except Exception as e:
            return {"error": str(e), "matches": matches}
        return {"matches": matches, "count": len(matches), "pattern": pattern}

    def _safe_path(self, path: str) -> Optional[str]:
        abs_path = os.path.abspath(os.path.join(self._root, path))
        if not abs_path.startswith(self._root):
            return None
        return abs_path

    def _human_size(self, size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"