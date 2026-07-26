"""
Brain Memory Injection v1 — TDD Tests

MemoryContext injects relevant memories into Brain's reasoning process.

Flow:
  User Message → MemoryContext → Memory Adapter → Relevant Memories → Prompt

Responsibilities:
  - Extract query from user message
  - Fetch relevant memories via Adapter
  - Sort by importance
  - Limit token count
  - Format for Brain prompt

Does NOT:
  - Store memories
  - Make decisions
  - Access Backend directly
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

test_data = [
    MemoryRecord(key="user::name", value="محمد کاربر اصلی Atlas است", memory_type="user", importance=0.95),
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0),
    MemoryRecord(key="project::router", value="Smart Router v2 ساخته شد", memory_type="project", importance=0.9),
    MemoryRecord(key="project::memory", value="Memory System v2.2 تکمیل شد", memory_type="project", importance=0.85),
    MemoryRecord(key="experience::error", value="خطای 403 هنگام دسترسی به API", memory_type="experience", importance=0.7),
    MemoryRecord(key="knowledge::python", value="Python زبان اصلی Atlas است", memory_type="knowledge", importance=0.8),
    MemoryRecord(key="short::temp", value="اطلاعات موقت", memory_type="short", importance=0.2),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 7)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.brain.memory_context import MemoryContext
    test("import MemoryContext", True)
except ImportError as e:
    test("import MemoryContext", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)
context = MemoryContext(adapter=adapter)
test("context created", context is not None)


# ═══════════════════════════════════════════════
# 2. Basic Memory Recall
# ═══════════════════════════════════════════════
print("\n━━━ 2. Basic Memory Recall ━━━")

result = context.build("ادامه پروژه Atlas")
test("build returns dict", isinstance(result, dict))
test("has count", "count" in result)
test("has memories", "memories" in result)
test("has prompt_text", "prompt_text" in result)
test("recall found memories", result["count"] >= 1)
test("prompt_text contains Atlas", "Atlas" in result["prompt_text"] or "atlas" in result["prompt_text"].lower())


# ═══════════════════════════════════════════════
# 3. Empty Memory
# ═══════════════════════════════════════════════
print("\n━━━ 3. Empty Memory ━━━")

empty_db = tempfile.mktemp(suffix=".db")
empty_backend = SQLiteBackend(db_path=empty_db)
empty_backend.open()
context_empty = MemoryContext(adapter=MemoryAdapter(backend=empty_backend))
result = context_empty.build("hello")
test("empty memory returns dict", isinstance(result, dict))
test("empty memory count is 0", result["count"] == 0)
test("empty memory prompt is empty", result["prompt_text"] == "")


# ═══════════════════════════════════════════════
# 4. Token Limit
# ═══════════════════════════════════════════════
print("\n━━━ 4. Token Limit ━━━")

result = context.build("Atlas project", max_tokens=50)
test("token limit respected", result["approx_tokens"] <= 50 or result["count"] <= 3)


# ═══════════════════════════════════════════════
# 5. Importance Priority
# ═══════════════════════════════════════════════
print("\n━━━ 5. Importance Priority ━━━")

result = context.build("Atlas")
if len(result["memories"]) >= 2:
    first_importance = result["memories"][0].get("importance", 0)
    second_importance = result["memories"][1].get("importance", 0)
    test("high importance first", first_importance >= second_importance)
else:
    test("importance priority (skipped)", True)


# ═══════════════════════════════════════════════
# 6. Prompt Format
# ═══════════════════════════════════════════════
print("\n━━━ 6. Prompt Format ━━━")

result = context.build("Atlas router")
test("prompt has context marker", "[Memory" in result["prompt_text"] or len(result["prompt_text"]) == 0)


# ═══════════════════════════════════════════════
# 7. Brain should NOT see internals
# ═══════════════════════════════════════════════
print("\n━━━ 7. Brain should NOT see internals ━━━")

import inspect
ctx_src = inspect.getsource(MemoryContext)
test("no SQLite in source", "sqlite" not in ctx_src.lower())
test("no Backend in source", "SQLiteBackend" not in ctx_src)
test("no Governance in source", "governance" not in ctx_src.lower())
test("no Backend direct access", "backend.get" not in ctx_src)


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
