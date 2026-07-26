"""
Memory Evaluation v1 — TDD Tests

MemoryEvaluator analyzes memory quality and provides insights:
  - Per-memory quality score
  - Duplicate detection
  - Usage statistics
  - Health report
  - Recommendations for consolidation

Usage:
    evaluator = MemoryEvaluator(backend=sqlite_backend)
    report = evaluator.evaluate()
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

# Test data
test_data = [
    # High quality memories
    MemoryRecord(key="user::name", value="محمد کاربر اصلی Atlas است", memory_type="user", importance=0.95, access_count=10, updated_at=time.time()-3600),
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0, access_count=15, updated_at=time.time()-7200),

    # Low quality memories
    MemoryRecord(key="short::temp", value="اطلاعات موقت", memory_type="short", importance=0.1, access_count=0, updated_at=time.time()-86400*10),
    MemoryRecord(key="short::old", value="چیز قدیمی", memory_type="short", importance=0.2, access_count=1, updated_at=time.time()-86400*30),

    # Potential duplicates
    MemoryRecord(key="user::name2", value="نام کاربر محمد است", memory_type="user", importance=0.8, access_count=5),
    MemoryRecord(key="short::name3", value="کاربر: محمد", memory_type="short", importance=0.6, access_count=2),

    # Medium quality
    MemoryRecord(key="experience::error", value="خطای 403 رخ داد", memory_type="experience", importance=0.7, access_count=3, updated_at=time.time()-86400*2),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 7)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.memory.evaluation import MemoryEvaluator
    test("import MemoryEvaluator", True)
except ImportError as e:
    test("import MemoryEvaluator", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

evaluator = MemoryEvaluator(backend=backend)
test("evaluator created", evaluator is not None)


# ═══════════════════════════════════════════════
# 2. Evaluate Single Memory
# ═══════════════════════════════════════════════
print("\n━━━ 2. Evaluate Single Memory ━━━")

quality = evaluator.evaluate_memory("user", "user::name")
test("evaluate returns score", "score" in quality)
test("score is float", isinstance(quality["score"], float))
test("has factors", "factors" in quality)


# ═══════════════════════════════════════════════
# 3. Full Evaluation
# ═══════════════════════════════════════════════
print("\n━━━ 3. Full Evaluation ━━━")

report = evaluator.evaluate()
test("report has total", "total_count" in report)
test("report has by_type", "by_type" in report)
test("report has quality_distribution", "quality_distribution" in report)
test("report has recommendations", "recommendations" in report)


# ═══════════════════════════════════════════════
# 4. Duplicate Detection
# ═══════════════════════════════════════════════
print("\n━━━ 4. Duplicate Detection ━━━")

duplicates = evaluator.find_duplicates()
test("find_duplicates returns list", isinstance(duplicates, list))
test("find duplicates found", len(duplicates) >= 1)


# ═══════════════════════════════════════════════
# 5. Quality Distribution
# ═══════════════════════════════════════════════
print("\n━━━ 5. Quality Distribution ━━━")

dist = evaluator.get_quality_distribution()
test("distribution has high", "high" in dist)
test("distribution has medium", "medium" in dist)
test("distribution has low", "low" in dist)
test("distribution sums to total", sum(dist.values()) == backend.count())


# ═══════════════════════════════════════════════
# 6. Recommendations
# ═══════════════════════════════════════════════
print("\n━━━ 6. Recommendations ━━━")

recs = evaluator.get_recommendations()
test("recommendations is list", isinstance(recs, list))
test("has recommendations", len(recs) >= 1)
test("each has action", all("action" in r for r in recs))


# ═══════════════════════════════════════════════
# 7. Stats
# ═══════════════════════════════════════════════
print("\n━━━ 7. Stats ━━━")

stats = evaluator.get_stats()
test("stats has total", "total" in stats)
test("stats has avg_quality", "avg_quality" in stats)
test("stats has oldest_hours", "oldest_hours" in stats)


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
