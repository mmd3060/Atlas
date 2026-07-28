"""
Code Executor — Atlas can execute Python code safely.
"""

import io
import sys
import traceback
import subprocess
from typing import Any, Dict, List


class CodeExecutor:
    """
    Execute Python code in a controlled environment.
    
    Use cases:
      - Math calculations
      - Data processing
      - Quick scripts
      - Testing code snippets
    """

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_OUTPUT_LENGTH = 5000

    def execute_python(self, code: str, timeout: int = None) -> Dict[str, Any]:
        """Execute Python code and return result."""
        timeout = timeout or self.DEFAULT_TIMEOUT
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        # Redirect stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        result = {
            "status": "unknown",
            "stdout": "",
            "stderr": "",
            "result": None,
            "error": None,
        }

        try:
            sys.stdout = output_buffer
            sys.stderr = error_buffer
            
            # Create a clean namespace
            namespace = {"__name__": "__main__"}
            
            # Try to compile (syntax check)
            compiled = compile(code, "<atlas>", "exec")
            exec(compiled, namespace)
            
            result["status"] = "success"
            result["stdout"] = output_buffer.getvalue()[:self.MAX_OUTPUT_LENGTH]
            result["stderr"] = error_buffer.getvalue()[:self.MAX_OUTPUT_LENGTH]
            
        except SyntaxError as e:
            result["status"] = "syntax_error"
            result["error"] = f"Line {e.lineno}: {e.msg}"
            result["stderr"] = traceback.format_exc()[:1000]
            
        except Exception as e:
            result["status"] = "runtime_error"
            result["error"] = f"{type(e).__name__}: {str(e)}"
            result["stderr"] = traceback.format_exc()[:1000]
            
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return result

    def evaluate(self, expression: str) -> Dict[str, Any]:
        """Evaluate a single expression and return its value."""
        try:
            result = eval(expression, {"__builtins__": __builtins__})
            return {"status": "success", "result": str(result)[:500]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_terminal_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a terminal command and return output."""
        try:
            completed = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "status": "success",
                "stdout": completed.stdout[:self.MAX_OUTPUT_LENGTH],
                "stderr": completed.stderr[:self.MAX_OUTPUT_LENGTH],
                "return_code": completed.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "error": f"Command timed out ({timeout}s)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def install_package(self, package: str) -> Dict[str, Any]:
        """Install a Python package."""
        return self.run_terminal_command(
            f"pip install {package}",
            timeout=120,
        )