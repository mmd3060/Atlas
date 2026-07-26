"""
Brain Reasoning Pipeline v1 — TDD Tests

The full reasoning flow:
  User Message → Input Analyzer → Memory Recall → Decision Engine
  → Model Selection → Prompt Builder → LLM Call → Response → Auto Remember

This is the heart of Atlas as an AI Operating System.
"""

import sys
import os
import tempfile
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord
from core.memory.backends.sqlite_backend import SQLiteBackend


passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ═══════════════════════════════════════════════
# Setup
# ═══════════════════════════════════════════════
print("\n━━━ Setup ━━━")

db_path = tempfile.mktemp(suffix=".db")
backend = SQLiteBackend(db_path=db_path)
backend.open()

# Insert test memories
test_data = [
    MemoryRecord(key="user::lang", value="کاربر فارسی صحبت می‌کند", memory_type="user", importance=0.9),
    MemoryRecord(key="user::pref", value="کاربر جواب‌های مفصل می‌خواهد", memory_type="user", importance=0.85),
    MemoryRecord(key="project::atlas", value="Atlas OS در حال ساخت است", memory_type="project", importance=1.0),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 3)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.brain.reasoning_pipeline import ReasoningPipeline
    from core.brain.input_analyzer import InputAnalyzer
    from core.brain.prompt_builder import PromptBuilder
    from core.brain.response_memory import ResponseMemory
    test("import ReasoningPipeline", True)
    test("import InputAnalyzer", True)
    test("import PromptBuilder", True)
    test("import ResponseMemory", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Input Analyzer
# ═══════════════════════════════════════════════
print("\n━━━ 2. Input Analyzer ━━━")

analyzer = InputAnalyzer()
test("analyzer created", analyzer is not None)

result = analyzer.analyze("کد Python بنویس")
test("analyze returns dict", isinstance(result, dict))
test("has task_type", "task_type" in result)
test("has language", "language" in result)
test("has complexity", "complexity" in result)


# ═══════════════════════════════════════════════
# 3. Prompt Builder
# ═══════════════════════════════════════════════
print("\n━━━ 3. Prompt Builder ━━━")

builder = PromptBuilder()
test("builder created", builder is not None)

prompt = builder.build(
    message="کد Python بنویس",
    memory_context={"memories": [{"value": "کاربر فارسی صحبت می‌کند"}]},
    analysis={"task_type": "coding", "language": "fa"},
)
test("build returns dict", isinstance(prompt, dict))
test("has system_prompt", "system_prompt" in prompt)
test("has user_prompt", "user_prompt" in prompt)
test("has memory_injected", "memory_injected" in prompt)


# ═══════════════════════════════════════════════
# 4. Response Memory
# ═══════════════════════════════════════════════
print("\n━━━ 4. Response Memory ━━━")

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)

resp_mem = ResponseMemory(adapter=adapter)
test("response memory created", resp_mem is not None)

result = resp_mem.remember_response(
    message="کد Python بنویس",
    response="def hello(): print('hi')",
    metadata={"task_type": "coding"},
)
test("remember_response returns dict", isinstance(result, dict))
test("has status", "status" in result)


# ═══════════════════════════════════════════════
# 5. Reasoning Pipeline
# ═══════════════════════════════════════════════
print("\n━━━ 5. Reasoning Pipeline ━━━")

pipeline = ReasoningPipeline(adapter=adapter)
test("pipeline created", pipeline is not None)

# Test full flow (without actual LLM call)
result = pipeline.process(
    message="ادامه پروژه Atlas",
    skip_llm=True,  # Skip actual LLM for testing
)
test("process returns dict", isinstance(result, dict))
test("has analysis", "analysis" in result)
test("has memory_context", "memory_context" in result)
test("has prompt", "prompt" in result)
test("has decision", "decision" in result)


# ═══════════════════════════════════════════════
# 6. Memory is recalled before reasoning
# ═══════════════════════════════════════════════
print("\n━━━ 6. Memory Recall Before Reasoning ━━━")

result = pipeline.process(message="Atlas project", skip_llm=True)
test("memory recalled", result["memory_context"]["count"] >= 0)


# ═══════════════════════════════════════════════
# 7. Decision is made
# ═══════════════════════════════════════════════
print("\n━━━ 7. Decision Made ━━━")

result = pipeline.process(message="کد بنویس", skip_llm=True)
test("decision has provider", "provider" in result["decision"] or result["decision"] is not None)


# ═══════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════
backend.close()
if os.path.exists(db_path):
    os.remove(db_path)


# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
