"""
Memory Search Engine v1 — TDD Tests

Tests the intelligent search layer that sits on top of Backend.

Architecture:
    User Query → SearchEngine → QueryAnalyzer
                                ├── Keyword Search (FTS5)
                                ├── Synonym Expansion
                                └── Memory Ranker
                                    ├── similarity
                                    ├── importance
                                    ├── recency
                                    ├── access_count
                                    └── memory_type_priority

Ranking Formula:
    Final Score = 0.35 similarity + 0.25 importance + 0.20 recency
                + 0.10 access_count + 0.10 memory_type_priority
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
# Setup: Create backend with test data
# ═══════════════════════════════════════════════
print("\n━━━ Setup: Creating test database ━━━")

db_path = tempfile.mktemp(suffix=".db")
backend = SQLiteBackend(db_path=db_path)
backend.open()

# Insert test memories
test_memories = [
    MemoryRecord(key="user::name", value="محمد کاربر اصلی Atlas است", memory_type="user", importance=0.95, source="user_message", tags=["identity"]),
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0, source="brain", tags=["project", "ai"]),
    MemoryRecord(key="project::memory", value="سیستم حافظه Atlas شامل Router و Pipeline است", memory_type="project", importance=0.9, source="brain", tags=["architecture"]),
    MemoryRecord(key="experience::error", value="خطای 403 هنگام دسترسی به API رخ داد", memory_type="experience", importance=0.7, source="tool", tags=["error"]),
    MemoryRecord(key="short::temp", value="اطلا暂时 ذخیره شده", memory_type="short", importance=0.2, tags=["temp"]),
    MemoryRecord(key="knowledge::python", value="Python یک زبان برنامه‌نویسی محبوب است", memory_type="knowledge", importance=0.6, source="user_message"),
    MemoryRecord(key="user::lang", value="کاربر فارسی صحبت می‌کند", memory_type="user", importance=0.8, tags=["preference"]),
]

for rec in test_memories:
    backend.put(rec)

test("test data inserted", backend.count() >= 7)
print(f"    Total records: {backend.count()}")


# ═══════════════════════════════════════════════
# 1. Import & Interface
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import & Interface ━━━")

try:
    from core.memory.memory_search import MemorySearchEngine
    test("import MemorySearchEngine", True)
except ImportError as e:
    test("import MemorySearchEngine", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

search = MemorySearchEngine(backend=backend)
test("search engine created", search is not None)


# ═══════════════════════════════════════════════
# 2. Basic Search
# ═══════════════════════════════════════════════
print("\n━━━ 2. Basic Search ━━━")

results = search.search("محمد")
test("search finds محمد", len(results) >= 1)
test("result has score", "score" in results[0] if results else False)
test("result has record", "record" in results[0] if results else False)

results = search.search("Atlas")
test("search finds Atlas", len(results) >= 1)

results = search.search("nonexistent_xyz_123")
test("search no results", len(results) == 0)


# ═══════════════════════════════════════════════
# 3. Filtered Search
# ═══════════════════════════════════════════════
print("\n━━━ 3. Filtered Search ━━━")

results = search.search("Atlas", memory_types=["project"])
test("filter by type project", len(results) >= 1)
test("all results are project", all(r["record"].memory_type == "project" for r in results))

results = search.search("error", memory_types=["experience"])
test("filter by type experience", len(results) >= 1)


# ═══════════════════════════════════════════════
# 4. Ranking
# ═══════════════════════════════════════════════
print("\n━━━ 4. Ranking ━━━")

results = search.search("Atlas OS")
test("ranking has scores", len(results) >= 1)
if results:
    scores = [r["score"] for r in results]
    test("scores are descending", scores == sorted(scores, reverse=True))
    test("top result is relevant", "atlas" in results[0]["record"].key.lower() or "atlas" in results[0]["record"].value.lower())


# ═══════════════════════════════════════════════
# 5. Score Breakdown
# ═══════════════════════════════════════════════
print("\n━━━ 5. Score Breakdown ━━━")

results = search.search("محمد")
if results:
    breakdown = results[0].get("breakdown", {})
    test("breakdown has similarity", "similarity" in breakdown)
    test("breakdown has importance", "importance" in breakdown)
    test("breakdown has recency", "recency" in breakdown)
    test("breakdown has access_count", "access_count" in breakdown)
    test("breakdown has type_priority", "type_priority" in breakdown)
    test("breakdown has total", "total" in breakdown)


# ═══════════════════════════════════════════════
# 6. Synonym Expansion
# ═══════════════════════════════════════════════
print("\n━━━ 6. Synonym Expansion ━━━")

# "پروژه" should also find "project" related memories
results = search.search("پروژه")
test("synonym search works", len(results) >= 1)


# ═══════════════════════════════════════════════
# 7. Context Export
# ═══════════════════════════════════════════════
print("\n━━━ 7. Context Export ━━━")

context = search.get_relevant_context("Atlas OS", max_tokens=500)
test("context export has memories", "memories" in context)
test("context export has query", "query" in context)
test("context export has total", "total_count" in context)


# ═══════════════════════════════════════════════
# 8. Top-K Search
# ═══════════════════════════════════════════════
print("\n━━━ 8. Top-K Search ━━━")

results = search.search("Atlas", limit=2)
test("top-k respects limit", len(results) <= 2)

results = search.search("Atlas", limit=1)
test("top-1 returns exactly 1", len(results) == 1)


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
