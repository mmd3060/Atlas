"""
Execution Engine v1 — TDD Tests

Orchestrates AI execution:
  - Takes model/provider from Router
  - Resolves to actual Provider instance
  - Executes chat
  - Future: Multi-brain support
"""

import sys
import os
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, "/data/workspace/Atlas")

class TestExecutionEngine(unittest.TestCase):

    def setUp(self):
        # اینجا فعلاً به صورت دستی ماژول رو Mock می‌کنیم تا مرحله قرمز رو ببینیم
        try:
            from core.intelligence.execution_engine import ExecutionEngine
            self.engine = ExecutionEngine()
        except ImportError:
            self.engine = None

    def test_engine_exists(self):
        self.assertIsNotNone(self.engine, "ExecutionEngine should be implemented")

    def test_basic_execution(self):
        if self.engine is None:
            return
        
        # Mocking the actual executor to avoid API calls during unit test
        self.engine._executor = MagicMock()
        self.engine._executor.execute.return_value = "Mocked Response"

        response = self.engine.execute(
            model_name="llama-3.3-70b",
            provider="openrouter",
            messages=[{"role": "user", "content": "سلام"}]
        )
        
        self.assertEqual(response, "Mocked Response")
        self.engine._executor.execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()
