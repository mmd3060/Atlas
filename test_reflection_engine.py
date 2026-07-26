"""
Agent Reflection Engine v1 — TDD Tests

Reflection Engine analyzes outcomes and extracts lessons.

Flow:
  Decision → Action → Result → Reflection → Lesson → Memory

Usage:
    engine = ReflectionEngine(adapter=memory_adapter, decision_logger=logger)
    result = engine.analyze(
        task="coding",
        decision={"provider": "github", "model": "llama"},
        outcome="success",
        feedback="answer was helpful",
    )
    # {lesson, confidence, action}
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

test_data = [
    MemoryRecord(key="user::lang", value="کاربر فارسی صحبت می‌کند", memory_type="user", importance=0.9),
    MemoryRecord(key="project::atlas", value="Atlas OS در حال ساخت است", memory_type="project", importance=1.0),
]

for rec in test_data:
    backend.put(rec)

test("test data inserted", backend.count() >= 2)


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.reflection.experience_record import ExperienceRecord
    from core.reflection.reflection_engine import ReflectionEngine
    test("import ExperienceRecord", True)
    test("import ReflectionEngine", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Experience Record
# ═══════════════════════════════════════════════
print("\n━━━ 2. Experience Record ━━━")

exp = ExperienceRecord(
    task="coding",
    decision={"provider": "github", "model": "llama"},
    outcome="success",
    feedback="answer was helpful",
)
test("record has task", exp.task == "coding")
test("record has decision", exp.decision["provider"] == "github")
test("record has outcome", exp.outcome == "success")
test("record has timestamp", exp.timestamp > 0)


# ═══════════════════════════════════════════════
# 3. Reflection Engine
# ═══════════════════════════════════════════════
print("\n━━━ 3. Reflection Engine ━━━")

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)

engine = ReflectionEngine(adapter=adapter)
test("engine created", engine is not None)


# ═══════════════════════════════════════════════
# 4. Analyze Success
# ═══════════════════════════════════════════════
print("\n━━━ 4. Analyze Success ━━━")

result = engine.analyze(
    task="coding",
    decision={"provider": "github", "model": "llama"},
    outcome="success",
    feedback="answer was helpful",
)
test("analyze returns dict", isinstance(result, dict))
test("has lesson", "lesson" in result)
test("has confidence", "confidence" in result)
test("has action", "action" in result)
test("success boosts provider", result["confidence"] >= 0.5)


# ═══════════════════════════════════════════════
# 5. Analyze Failure
# ═══════════════════════════════════════════════
print("\n━━━ 5. Analyze Failure ━━━")

result = engine.analyze(
    task="coding",
    decision={"provider": "gemini", "model": "gemini-pro"},
    outcome="failure",
    feedback="code was incomplete",
)
test("failure has lesson", "lesson" in result)
test("failure lower confidence", result["confidence"] <= 0.7)


# ═══════════════════════════════════════════════
# 6. Lesson Storage
# ═══════════════════════════════════════════════
print("\n━━━ 6. Lesson Storage ━━━")

# Analyze multiple times
engine.analyze(task="coding", decision={"provider": "github"}, outcome="success", feedback="good")
engine.analyze(task="coding", decision={"provider": "github"}, outcome="success", feedback="great")

lessons = engine.get_lessons(task="coding")
test("get_lessons returns list", isinstance(lessons, list))
test("lessons stored", len(lessons) >= 1)


# ═══════════════════════════════════════════════
# 7. Pattern Detection
# ═══════════════════════════════════════════════
print("\n━━━ 7. Pattern Detection ━━━")

patterns = engine.detect_patterns()
test("detect_patterns returns list", isinstance(patterns, list))


# ═══════════════════════════════════════════════
# 8. Get Stats
# ═══════════════════════════════════════════════
print("\n━━━ 8. Get Stats ━━━")

stats = engine.get_stats()
test("stats has total", "total" in stats)
test("stats has success_count", "success_count" in stats)
test("stats has failure_count", "failure_count" in stats)


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
