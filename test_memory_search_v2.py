"""
Memory Search Engine v2 — Modular Architecture Tests

Tests the modular search system:
    QueryParser → KeywordSearch → MemoryRanker → Results
"""

import sys
import os
import tempfile
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord
from core.memory.backends.sqlite_backend import SQLiteBackend
from core.memory.search import MemorySearchEngine, QueryParser, KeywordSearch, MemoryRanker


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
    MemoryRecord(key="user::name", value="محمد کاربر اصلی Atlas است", memory_type="user", importance=0.95, tags=["identity"]),
    MemoryRecord(key="project::atlas", value="Atlas OS یک سیستم‌عامل هوش مصنوعی است", memory_type="project", importance=1.0, tags=["project", "ai"]),
    MemoryRecord(key="project::memory", value="سیستم حافظه Atlas شامل Router و Pipeline است", memory_type="project", importance=0.9, tags=["architecture"]),
    MemoryRecord(key="experience::error", value="خطای 403 هنگام دسترسی به API رخ داد", memory_type="experience", importance=0.7, tags=["error"]),
    MemoryRecord(key="short::temp", value="اطلاعات موقت", memory_type="short", importance=0.2, tags=["temp"]),
    MemoryRecord(key="knowledge::python", value="Python یک زبان برنامه‌نویسی محبوب است", memory_type="knowledge", importance=0.6),
    MemoryRecord(key="user::lang", value="کاربر فارسی صحبت می‌کند", memory_type="user", importance=0.8, tags=["preference"]),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 7)


# ═══════════════════════════════════════════════
# 1. QueryParser
# ═══════════════════════════════════════════════
print("\n━━━ 1. QueryParser ━━━")

parser = QueryParser()

parsed = parser.parse("پروژه Atlas")
test("parse original", parsed["original"] == "پروژه Atlas")
test("parse keywords", len(parsed["keywords"]) == 2)
test("parse expanded has synonyms", len(parsed["expanded"]) > 2)
test("parse is_persian", parsed["is_persian"])

expanded = parser.expand("حافظه")
test("expand synonym", "memory" in expanded or "remember" in expanded)


# ═══════════════════════════════════════════════
# 2. KeywordSearch
# ═══════════════════════════════════════════════
print("\n━━━ 2. KeywordSearch ━━━")

kw_search = KeywordSearch(backend=backend)

results = kw_search.search(["Atlas"], memory_types=["project"])
test("keyword search finds Atlas", len(results) >= 1)
test("keyword search type filter", all(r.memory_type == "project" for r in results))

results = kw_search.search(["nonexistent_xyz"])
test("keyword search no results", len(results) == 0)


# ═══════════════════════════════════════════════
# 3. MemoryRanker
# ═══════════════════════════════════════════════
print("\n━━━ 3. MemoryRanker ━━━")

ranker = MemoryRanker()

records = [r for r in backend.list_records() if not r.is_expired()]
ranked = ranker.rank("Atlas", records)

test("ranker returns results", len(ranked) > 0)
test("ranker has scores", "score" in ranked[0])
test("ranker has breakdown", "breakdown" in ranked[0])
test("ranker has record", "record" in ranked[0])

scores = [r["score"] for r in ranked]
test("scores descending", scores == sorted(scores, reverse=True))

top = ranked[0]["breakdown"]
test("breakdown has similarity", "similarity" in top)
test("breakdown has importance", "importance" in top)
test("breakdown has recency", "recency" in top)


# ═══════════════════════════════════════════════
# 4. MemorySearchEngine (orchestrator)
# ═══════════════════════════════════════════════
print("\n━━━ 4. MemorySearchEngine ━━━")

engine = MemorySearchEngine(backend=backend)

results = engine.search("محمد")
test("engine search finds محمد", len(results) >= 1)
test("engine has score", "score" in results[0])
test("engine has breakdown", "breakdown" in results[0])

results = engine.search("Atlas OS", limit=2)
test("engine respects limit", len(results) <= 2)

results = engine.search("Atlas", memory_types=["project"])
test("engine type filter", all(r["record"].memory_type == "project" for r in results))


# ═══════════════════════════════════════════════
# 5. Context Export
# ═══════════════════════════════════════════════
print("\n━━━ 5. Context Export ━━━")

context = engine.get_relevant_context("Atlas OS")
test("context has memories", "memories" in context)
test("context has query", "query" in context)
test("context has total", "total_count" in context)
test("context has tokens", "approx_tokens" in context)


# ═══════════════════════════════════════════════
# 6. Architecture Rules
# ═══════════════════════════════════════════════
print("\n━━━ 6. Architecture Rules ━━━")

import inspect

# Each module has single responsibility
parser_src = inspect.getsource(QueryParser)
test("QueryParser: no search method", "def search" not in parser_src)
test("QueryParser: no rank method", "def rank" not in parser_src)

search_src = inspect.getsource(KeywordSearch)
test("KeywordSearch: no parse method", "def parse" not in search_src)
test("KeywordSearch: no rank method", "def rank" not in search_src)

ranker_src = inspect.getsource(MemoryRanker)
test("MemoryRanker: no search method", "def search" not in ranker_src)
test("MemoryRanker: no parse method", "def parse" not in ranker_src)


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
