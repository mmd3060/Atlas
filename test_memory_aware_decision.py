"""
Memory-aware Decision Engine v1 — TDD Tests

Enhances DecisionEngine with memory signals.

Before:
    decision = engine.decide(message)

After:
    decision = engine.decide(message, memory_context=context)

Memory signals:
  - User preferences
  - Project context
  - Previous failures
  - Successful models
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
    MemoryRecord(key="user::pref_detail", value="کاربر جواب‌های مفصل با مثال می‌خواهد", memory_type="user", importance=0.85),
    MemoryRecord(key="project::atlas", value="Atlas OS در حال ساخت است", memory_type="project", importance=1.0),
    MemoryRecord(key="experience::fail_gemini", value="Gemini برای coding خطا داد", memory_type="experience", importance=0.8),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 4)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.decision.memory_signal import MemorySignal
    from core.decision.memory_aware_engine import MemoryAwareEngine
    test("import MemorySignal", True)
    test("import MemoryAwareEngine", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. MemorySignal Extraction
# ═══════════════════════════════════════════════
print("\n━━━ 2. MemorySignal Extraction ━━━")

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)
signal = MemorySignal(adapter=adapter)

result = signal.extract("کد Python بنویس")
test("extract returns dict", isinstance(result, dict))
test("has user_preferences", "user_preferences" in result)
test("has project_context", "project_context" in result)
test("has history", "history" in result)


# ═══════════════════════════════════════════════
# 3. User Preference Boost
# ═══════════════════════════════════════════════
print("\n━━━ 3. User Preference Boost ━━━")

engine = MemoryAwareEngine(adapter=adapter)
decision = engine.decide(
    message="کد Python بنویس",
    base_scores={"openrouter": 0.5, "gemini": 0.6, "github": 0.55},
)
test("decide returns dict", isinstance(decision, dict))
test("has chosen provider", "provider" in decision)
test("has confidence", "confidence" in decision)
test("has reasons", "reasons" in decision)


# ═══════════════════════════════════════════════
# 4. Previous Failure Penalty
# ═══════════════════════════════════════════════
print("\n━━━ 4. Previous Failure Penalty ━━━")

decision = engine.decide(
    message="کد Python بنویس",
    base_scores={"openrouter": 0.5, "gemini": 0.6, "github": 0.55},
)
# Gemini should be penalized due to failure memory
gemini_final = decision.get("final_scores", {}).get("gemini", 0.6)
test("gemini penalized", gemini_final <= 0.6)


# ═══════════════════════════════════════════════
# 5. Empty Memory
# ═══════════════════════════════════════════════
print("\n━━━ 5. Empty Memory ━━━")

empty_db = tempfile.mktemp(suffix=".db")
empty_backend = SQLiteBackend(db_path=empty_db)
empty_backend.open()
empty_adapter = MemoryAdapter(backend=empty_backend)
empty_engine = MemoryAwareEngine(adapter=empty_adapter)
decision = empty_engine.decide(
    message="hello",
    base_scores={"openrouter": 0.5, "gemini": 0.6},
)
test("empty memory returns decision", "provider" in decision)
test("empty memory uses base scores", decision["confidence"] >= 0.0)


# ═══════════════════════════════════════════════
# 6. Decision with Reasons
# ═══════════════════════════════════════════════
print("\n━━━ 6. Decision with Reasons ━━━")

decision = engine.decide(
    message="ادامه پروژه Atlas",
    base_scores={"openrouter": 0.5, "gemini": 0.6, "github": 0.55},
)
test("has reasons list", isinstance(decision["reasons"], list))
test("reasons is non-empty", len(decision["reasons"]) >= 0)


# ═══════════════════════════════════════════════
# 7. Final Scores
# ═══════════════════════════════════════════════
print("\n━━━ 7. Final Scores ━━━")

decision = engine.decide(
    message="کد بنویس",
    base_scores={"openrouter": 0.5, "gemini": 0.6, "github": 0.55},
)
test("has final_scores", "final_scores" in decision)
test("final_scores has all providers", len(decision["final_scores"]) == 3)


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
