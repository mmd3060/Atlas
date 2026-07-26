"""
Brain Memory Adapter v1 — TDD Tests

The bridge between Brain and Memory.

Brain uses:
  adapter.recall(query)          → relevant memories for reasoning
  adapter.remember(value, ...)   → store new memory
  adapter.get_context(query)     → full context for prompt
  adapter.get_user_profile()     → user preferences/history

Brain does NOT see:
  - Memory Interface internals
  - SQLite, Backend, Governance, etc.
"""

import sys
import os
import tempfile
import time
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

# Insert test data
test_data = [
    MemoryRecord(key="user::name", value="محمد کاربر اصلی Atlas است", memory_type="user", importance=0.95, tags=["identity"]),
    MemoryRecord(key="user::pref_detail", value="کاربر جواب‌های مفصل با مثال می‌خواهد", memory_type="user", importance=0.9, tags=["preference"]),
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0, tags=["project"]),
    MemoryRecord(key="project::router", value="Memory Router v2.2 ساخته شد", memory_type="project", importance=0.9, tags=["architecture"]),
    MemoryRecord(key="experience::error", value="خطای 403 هنگام دسترسی به API", memory_type="experience", importance=0.7, tags=["error"]),
    MemoryRecord(key="knowledge::python", value="Python زبان اصلی Atlas است", memory_type="knowledge", importance=0.8),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 6)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.brain.memory_adapter import MemoryAdapter
    test("import MemoryAdapter", True)
except ImportError as e:
    test("import MemoryAdapter", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

adapter = MemoryAdapter(backend=backend)
test("adapter created", adapter is not None)


# ═══════════════════════════════════════════════
# 2. recall (Brain uses this before reasoning)
# ═══════════════════════════════════════════════
print("\n━━━ 2. recall ━━━")

memories = adapter.recall("Atlas router")
test("recall returns list", isinstance(memories, list))
test("recall finds results", len(memories) >= 1)
test("recall has key", "key" in memories[0])
test("recall has value", "value" in memories[0])
test("recall has relevance", "relevance" in memories[0])


# ═══════════════════════════════════════════════
# 3. remember (Brain uses this after learning)
# ═══════════════════════════════════════════════
print("\n━━━ 3. remember ━━━")

result = adapter.remember(
    value="کاربر فارسی صحبت می‌کند",
    memory_type="user",
    importance=0.85,
)
test("remember returns status", result["status"] == "stored")
test("remember has key", "key" in result)


# ═══════════════════════════════════════════════
# 4. get_context (Brain uses this for prompt)
# ═══════════════════════════════════════════════
print("\n━━━ 4. get_context ━━━")

ctx = adapter.get_context("Atlas project")
test("get_context returns dict", isinstance(ctx, dict))
test("has memories", "memories" in ctx)
test("has prompt_text", "prompt_text" in ctx)
test("prompt_text is string", isinstance(ctx["prompt_text"], str))
test("prompt_text is non-empty", len(ctx["prompt_text"]) > 0)


# ═══════════════════════════════════════════════
# 5. get_user_profile (Brain uses this for personalization)
# ═══════════════════════════════════════════════
print("\n━━━ 5. get_user_profile ━━━")

profile = adapter.get_user_profile()
test("get_user_profile returns dict", isinstance(profile, dict))


# ═══════════════════════════════════════════════
# 6. auto_remember (automatic memory capture)
# ═══════════════════════════════════════════════
print("\n━━━ 6. auto_remember ━━━")

result = adapter.auto_remember("من دوست دارم جواب‌های کوتاه باشند")
test("auto_remember returns status", "status" in result)
test("auto_remember classified", "memory_type" in result)


# ═══════════════════════════════════════════════
# 7. Brain should NOT see internals
# ═══════════════════════════════════════════════
print("\n━━━ 7. Brain should NOT see internals ━━━")

import inspect
adapter_src = inspect.getsource(MemoryAdapter)
test("no SQLite in source", "sqlite" not in adapter_src.lower())
test("no Backend in source", "SQLiteBackend" not in adapter_src)
test("no Governance in source", "governance" not in adapter_src.lower())
test("no Consolidation in source", "consolidation" not in adapter_src.lower())
test("no Repository in source", "memory_repository" not in adapter_src)


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
