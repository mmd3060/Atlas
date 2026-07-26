"""
Memory Interface v1 — TDD Tests

The ONLY way Brain talks to Memory.

Brain should ONLY see:
  memory.get_context(query)      → relevant memories
  memory.search(query)           → search results
  memory.remember(data)          → store new memory
  memory.check_conflict(data)    → check for conflicts
  memory.get_stats()             → memory statistics

Brain should NOT see:
  - SQLite
  - Backend
  - Governance
  - Consolidation
  - Repository
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
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0, tags=["project"]),
    MemoryRecord(key="project::router", value="Memory Router v2.2 ساخته شد", memory_type="project", importance=0.9, tags=["architecture"]),
    MemoryRecord(key="experience::error", value="خطای 403 هنگام دسترسی به API", memory_type="experience", importance=0.7, tags=["error"]),
    MemoryRecord(key="short::temp", value="اطلاعات موقت", memory_type="short", importance=0.2),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 5)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.memory.memory_interface import MemoryInterface
    test("import MemoryInterface", True)
except ImportError as e:
    test("import MemoryInterface", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

memory = MemoryInterface(backend=backend)
test("memory interface created", memory is not None)


# ═══════════════════════════════════════════════
# 2. get_context (Brain uses this)
# ═══════════════════════════════════════════════
print("\n━━━ 2. get_context ━━━")

ctx = memory.get_context("Atlas project")
test("get_context returns dict", isinstance(ctx, dict))
test("has memories", "memories" in ctx)
test("has query", "query" in ctx)
test("has count", "count" in ctx)
test("has relevant memories", len(ctx["memories"]) >= 1)


# ═══════════════════════════════════════════════
# 3. search (Brain uses this)
# ═══════════════════════════════════════════════
print("\n━━━ 3. search ━━━")

results = memory.search("محمد")
test("search returns list", isinstance(results, list))
test("search finds results", len(results) >= 1)
test("result has key", "key" in results[0])
test("result has value", "value" in results[0])
test("result has score", "score" in results[0])


# ═══════════════════════════════════════════════
# 4. remember (Brain uses this)
# ═══════════════════════════════════════════════
print("\n━━━ 4. remember ━━━")

result = memory.remember(
    value="Atlas از Python ساخته شده",
    memory_type="knowledge",
    importance=0.8,
)
test("remember returns status", "status" in result)
test("remember success", result["status"] == "stored")

# Verify it was stored
rec = backend.get("knowledge", result.get("key", ""))
test("remember persists", rec is not None)


# ═══════════════════════════════════════════════
# 5. check_conflict (Brain uses this)
# ═══════════════════════════════════════════════
print("\n━━━ 5. check_conflict ━━━")

# Add conflicting memories (same key, different types)
backend.put(MemoryRecord(key="info::cpu", value="CPU سیستم i3 9100 است", memory_type="project", importance=0.9))
backend.put(MemoryRecord(key="info::cpu", value="CPU سیستم i5 14400 است", memory_type="experience", importance=0.95))

conflicts = memory.check_conflict()
test("check_conflict returns list", isinstance(conflicts, list))
test("finds conflicts", len(conflicts) >= 1)


# ═══════════════════════════════════════════════
# 6. get_stats (Brain uses this)
# ═══════════════════════════════════════════════
print("\n━━━ 6. get_stats ━━━")

stats = memory.get_stats()
test("get_stats returns dict", isinstance(stats, dict))
test("has total", "total" in stats)
test("has by_type", "by_type" in stats)


# ═══════════════════════════════════════════════
# 7. Brain should NOT see internals
# ═══════════════════════════════════════════════
print("\n━━━ 7. Brain should NOT see internals ━━━")

import inspect

interface_src = inspect.getsource(MemoryInterface)
test("no SQLite reference", "sqlite" not in interface_src.lower())
test("no Backend reference", "SQLiteBackend" not in interface_src)
test("no Governance reference", "governance" not in interface_src.lower())
test("no Consolidation reference", "consolidation" not in interface_src.lower())
test("no Repository import at module level", "from core.memory.memory_repository" not in open("/data/workspace/Atlas/core/memory/memory_interface.py").read())


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
