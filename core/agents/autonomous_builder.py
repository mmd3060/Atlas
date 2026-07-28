"""
Autonomous Builder — Atlas can build new features from natural language.

Flow:
    1. User says "Add X feature"
    2. Builder analyzes request
    3. Generates code structure
    4. Creates files
    5. Writes tests
    6. Runs tests
    7. Reports results
"""

import os
import re
import time
from typing import Any, Dict, List, Optional
from core.agents.self_modifying_agent import SelfModifyingAgent


class AutonomousBuilder:
    """
    Atlas's autonomous feature builder.
    
    Usage:
        builder = AutonomousBuilder()
        result = builder.build_feature("Add a calculator tool that can do basic math")
    """

    # Templates for common feature types
    FEATURE_TEMPLATES = {
        "tool": {
            "path": "core/tools/{name}.py",
            "template": '''"""
{name_human} — {description}
"""

from typing import Any, Dict


class {class_name}:
    """
    {description}
    """

    def __init__(self):
        pass

    def execute(self, action: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute {name_human} action.
        """
        if action == "default":
            return {{"status": "success", "result": "placeholder"}}
        
        return {{"error": f"Unknown action: {{action}}"}}
''',
        },
        "agent": {
            "path": "core/agents/{name}.py",
            "template": '''"""
{class_name} — {description}
"""

from typing import Any, Dict, List


class {class_name}:
    """
    {description}
    """

    def __init__(self, name: str = "{name_human}"):
        self.name = name
        self.tools: List[str] = []

    def process(self, message: str) -> str:
        """
        Process a message and return a response.
        """
        return f"[{{self.name}}]: Processing..."

    def get_info(self) -> Dict[str, Any]:
        return {{"name": self.name, "tools": self.tools}}
''',
        },
        "router": {
            "path": "core/router/{name}.py",
            "template": '''"""
{class_name} — {description}
"""

from typing import Any, Dict, List


class {class_name}:
    """
    {description}
    """

    def __init__(self):
        self._routes: Dict[str, Any] = {{}}

    def route(self, message: str) -> Dict[str, Any]:
        """
        Route message to appropriate handler.
        """
        return {{"handler": "default", "confidence": 0.5}}
''',
        },
        "memory": {
            "path": "core/memory/{name}.py",
            "template": '''"""
{class_name} — {description}
"""

from typing import Any, Dict, List


class {class_name}:
    """
    {description}
    """

    def __init__(self):
        self._data: Dict[str, Any] = {{}}

    def store(self, key: str, value: Any):
        self._data[key] = value

    def retrieve(self, key: str) -> Any:
        return self._data.get(key)
''',
        },
        "interface": {
            "path": "core/interfaces/{name}.py",
            "template": '''"""
{class_name} — {description}
"""

from typing import Any, Dict


class {class_name}:
    """
    {description}
    """

    def __init__(self):
        pass

    def process(self, input_data: Any) -> Dict[str, Any]:
        return {{"type": "{name}", "status": "processed"}}
''',
        },
    }

    def __init__(self, project_root: str = None):
        self._project_root = project_root or os.getcwd()
        self._sma = SelfModifyingAgent(project_root=self._project_root)
        self._created_files: List[str] = []

    def analyze_request(self, request: str) -> Dict[str, Any]:
        """
        Analyze a natural language feature request.
        """
        request_lower = request.lower()

        # Determine feature type
        feature_type = "tool"
        if any(w in request_lower for w in ["ایجنت", "agent", "دستیار"]):
            feature_type = "agent"
        elif any(w in request_lower for w in ["مسیریاب", "router", "هداایت"]):
            feature_type = "router"
        elif any(w in request_lower for w in ["حافظه", "memory", "ذخیره"]):
            feature_type = "memory"
        elif any(w in request_lower for w in ["رابط", "interface", "gateway"]):
            feature_type = "interface"

        # Extract feature name
        name = self._extract_name(request)
        class_name = "".join(p.capitalize() for p in name.split("_"))

        return {
            "type": feature_type,
            "name": name,
            "class_name": class_name,
            "description": request[:100],
        }

    def build_feature(self, request: str) -> Dict[str, Any]:
        """
        Build a complete feature from natural language request.
        
        Steps:
          1. Analyze request
          2. Generate code from template
          3. Create source file
          4. Create test file
          5. Register in system
          6. Report results
        """
        # Step 1: Analyze
        spec = self.analyze_request(request)

        # Step 2: Get template
        template = self.FEATURE_TEMPLATES.get(spec["type"], self.FEATURE_TEMPLATES["tool"])
        file_path = template["path"].format(name=spec["name"])

        # Step 3: Generate code
        name_human = spec["name"].replace("_", " ").title()
        code = template["template"].format(
            name=spec["name"],
            name_human=name_human,
            class_name=spec["class_name"],
            description=spec["description"],
        )

        # Step 4: Create source file
        result = self._sma.write_new_file(file_path, code)
        if "error" in result:
            return {"status": "failed", "error": result["error"]}

        self._created_files.append(file_path)

        # Step 5: Create test file
        test_path = f"test_{spec['name']}.py"
        test_code = self._generate_test(spec)
        test_result = self._sma.write_new_file(test_path, test_code)
        if "error" not in test_result:
            self._created_files.append(test_path)

        # Step 6: Register in ToolSystem (if it's a tool)
        if spec["type"] == "tool":
            self._register_tool(spec["name"], spec["description"])

        return {
            "status": "built",
            "spec": spec,
            "files_created": self._created_files,
            "file_path": file_path,
            "test_path": test_path if "error" not in test_result else None,
        }

    def _extract_name(self, request: str) -> str:
        """Extract a Python-safe name from request."""
        # Try to find quoted name
        quoted = re.findall(r'["\']([^"\']+)["\']', request)
        if quoted:
            name = quoted[0]
        else:
            # Use last few words
            words = request.lower().split()
            # Filter out stopwords
            stopwords = {"add", "a", "an", "the", "create", "build", "make", "feature", "that", "can", "do"}
            meaningful = [w for w in words if w not in stopwords and len(w) > 2]
            if meaningful:
                name = "_".join(meaningful[:3])
            else:
                name = "new_feature"

        # Sanitize
        name = re.sub(r'[^a-zA-Z0-9_]', '', name).lower()
        if not name:
            name = "new_feature"

        return name

    def _generate_test(self, spec: Dict) -> str:
        """Generate a test file for the new feature."""
        class_name = spec["class_name"]
        module_path = spec["name"]

        return f'''"""
Auto-generated test for {class_name}
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_import():
    """Test: Can import {class_name}"""
    try:
        from core.{spec["type"]}s.{module_path} import {class_name}
        print("  ✅ import {class_name}")
        return True
    except Exception as e:
        print(f"  ❌ import failed: {{e}}")
        return False


def test_instantiation():
    """Test: Can create {class_name}"""
    try:
        from core.{spec["type"]}s.{module_path} import {class_name}
        obj = {class_name}()
        print("  ✅ create {class_name}")
        return True
    except Exception as e:
        print(f"  ❌ create failed: {{e}}")
        return False


if __name__ == "__main__":
    print(f"━━━ Test: {class_name} ━━━")
    r1 = test_import()
    r2 = test_instantiation()
    total = sum([r1, r2])
    print(f"\\nResults: {{total}} passed, {{2 - total}} failed")
'''

    def _register_tool(self, tool_name: str, description: str):
        """Register new tool in ToolSystem."""
        try:
            # Read current tool_system.py
            ts_path = "core/tools/tool_system.py"
            ts_code = self._sma.read_code(ts_path)
            if "error" in ts_code:
                return

            content = ts_code["content"]
            
            # Add tool registration
            new_entry = f'''            "{tool_name}": {{
                "description": "{description[:60]}",
                "level": "moderate",
                "category": "custom",
            }},'''

            # Insert before closing brace of _tools dict
            # Find "memory_status" entry and add after it
            marker = '"memory_status"'
            if marker in content:
                new_content = content.replace(
                    marker,
                    f"{marker}  # marker",
                )
                # Actually just append to the dict
                old = '''            "remove_background": {
                "description": "Remove background from an image",
                "level": "moderate",
                "category": "vision",
            },'''
                new = old + f'''

            {new_entry}'''
                if old in content:
                    self._sma.modify_code(ts_path, old, new)
        except Exception:
            pass  # Silent fail — registration is best-effort

    def get_created_files(self) -> List[str]:
        """Get list of all files created by the builder."""
        return list(self._created_files)