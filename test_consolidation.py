"""
Memory Consolidation v1 — TDD Tests

Memory Consolidation is like how the human brain works:
  - Short-term memories get promoted to long-term
  - Duplicate memories get merged
  - Important patterns get extracted
  - Old/unimportant memories get demoted

Architecture:
    Short Memory → ConsolidationEngine → Long Memory
    Duplicate Memories → Merge → Single Memory
    Old Long Memories → Demote → Archive

Flow:
    1. Find short memories eligible for promotion
    2. Check importance threshold
    3. Promote to long-term
    4. Find duplicates → merge
    5. Demote old long memories
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord, MEMORY_TYPES
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
    # Short memories (candidates for promotion)
    MemoryRecord(key="short::atlas1", value="Atlas OS یک پروژه مهم است", memory_type="short", importance=0.9, created_at=time.time()-3600),
    MemoryRecord(key="short::atlas2", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="short", importance=0.85, created_at=time.time()-7200),
    MemoryRecord(key="short::temp", value="اطلاعات موقت", memory_type="short", importance=0.2, created_at=time.time()-100),

    # Long memories (candidates for demotion)
    MemoryRecord(key="long::old", value="اطلاعات قدیمی", memory_type="long", importance=0.3, updated_at=time.time()-86400*30),
    MemoryRecord(key="long::recent", value="اطلاعات جدید", memory_type="long", importance=0.8, updated_at=time.time()-3600),

    # Potential duplicates
    MemoryRecord(key="user::name", value="محمد کاربر Atlas است", memory_type="user", importance=0.9),
    MemoryRecord(key="short::name2", value="نام کاربر محمد است", memory_type="short", importance=0.7),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 7)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.memory.consolidation import MemoryConsolidator
    test("import MemoryConsolidator", True)
except ImportError as e:
    test("import MemoryConsolidator", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

consolidator = MemoryConsolidator(backend=backend)
test("consolidator created", consolidator is not None)


# ═══════════════════════════════════════════════
# 2. Find Candidates for Promotion
# ═══════════════════════════════════════════════
print("\n━━━ 2. Promotion Candidates ━━━")

candidates = consolidator.find_promotion_candidates(min_importance=0.5)
test("find candidates", len(candidates) >= 1)
test("candidates are short", all(r.memory_type == "short" for r in candidates))
test("candidates meet importance", all(r.importance >= 0.5 for r in candidates))


# ═══════════════════════════════════════════════
# 3. Promote Memory
# ═══════════════════════════════════════════════
print("\n━━━ 3. Promote Memory ━━━")

count_before = backend.count("long")
result = consolidator.promote("short::atlas1")
test("promote returns success", result["status"] == "promoted")
test("promote target is long", result["target_type"] == "long")

# Check it's no longer in short
rec = backend.get("short", "short::atlas1")
test("removed from short", rec is None)

# Check it's in long (key stays the same, just type changes)
rec = backend.get("long", "short::atlas1")
test("added to long", rec is not None)


# ═══════════════════════════════════════════════
# 4. Find Duplicates
# ═══════════════════════════════════════════════
print("\n━━━ 4. Find Duplicates ━━━")

duplicates = consolidator.find_duplicates()
test("find duplicates", isinstance(duplicates, list))


# ═══════════════════════════════════════════════
# 5. Merge Memories
# ═══════════════════════════════════════════════
print("\n━━━ 5. Merge Memories ━━━")

# Add more test data for merging
backend.put(MemoryRecord(key="short::merge1", value="Atlas OS مهم است", memory_type="short", importance=0.7))
backend.put(MemoryRecord(key="short::merge2", value="Atlas OS یک پروژه است", memory_type="short", importance=0.6))

result = consolidator.merge("short::merge1", "short::merge2", target_type="long")
test("merge returns success", result["status"] == "merged")


# ═══════════════════════════════════════════════
# 6. Find Demotion Candidates
# ═══════════════════════════════════════════════
print("\n━━━ 6. Demotion Candidates ━━━")

demotion_candidates = consolidator.find_demotion_candidates(max_importance=0.4, min_age_days=7)
test("find demotion candidates", len(demotion_candidates) >= 1)
test("candidates are long", all(r.memory_type == "long" for r in demotion_candidates))


# ═══════════════════════════════════════════════
# 7. Demote Memory
# ═══════════════════════════════════════════════
print("\n━━━ 7. Demote Memory ━━━")

result = consolidator.demote("long::old")
test("demote returns success", result["status"] == "demoted")
test("demote target is archive", result["target_type"] in ["short", "archive"])


# ═══════════════════════════════════════════════
# 8. Consolidation Stats
# ═══════════════════════════════════════════════
print("\n━━━ 8. Consolidation Stats ━━━")

stats = consolidator.get_stats()
test("stats has short_count", "short_count" in stats)
test("stats has long_count", "long_count" in stats)
test("stats has total", "total_count" in stats)


# ═══════════════════════════════════════════════
# 9. Run Full Consolidation
# ═══════════════════════════════════════════════
print("\n━━━ 9. Full Consolidation ━━━")

result = consolidator.consolidate()
test("consolidate returns result", "promoted" in result)
test("consolidate returns merged", "merged" in result)
test("consolidate returns demoted", "demoted" in result)


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
