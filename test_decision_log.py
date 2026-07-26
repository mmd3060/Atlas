"""
Memory Decision Log v1 — TDD Tests

Decision Log records WHY each memory action was taken.
This enables Reflection Engine to review past decisions.

Usage:
    logger = DecisionLogger(backend=sqlite_backend)
    logger.log(memory_key="cpu", action="archive", reason="conflict with newer")
    history = logger.get_history(memory_key="cpu")
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, "/data/workspace/Atlas")

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
test("backend ready", backend.health())


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.memory.decision_log import DecisionLogger
    test("import DecisionLogger", True)
except ImportError as e:
    test("import DecisionLogger", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)

logger = DecisionLogger(backend=backend)
test("logger created", logger is not None)


# ═══════════════════════════════════════════════
# 2. Log a Decision
# ═══════════════════════════════════════════════
print("\n━━━ 2. Log Decision ━━━")

result = logger.log(
    memory_key="cpu",
    action="archive",
    reason="conflict with newer memory",
    confidence=0.85,
)
test("log returns success", result["status"] == "logged")
test("log has timestamp", "timestamp" in result)


# ═══════════════════════════════════════════════
# 3. Get History
# ═══════════════════════════════════════════════
print("\n━━━ 3. Get History ━━━")

history = logger.get_history(memory_key="cpu")
test("history is list", isinstance(history, list))
test("history has entries", len(history) >= 1)
test("entry has action", "action" in history[0])
test("entry has reason", "reason" in history[0])


# ═══════════════════════════════════════════════
# 4. Log Multiple Decisions
# ═══════════════════════════════════════════════
print("\n━━━ 4. Log Multiple Decisions ━━━")

logger.log(memory_key="cpu", action="keep", reason="high quality", confidence=0.9)
logger.log(memory_key="ram", action="promote", reason="frequently accessed", confidence=0.95)

history_cpu = logger.get_history(memory_key="cpu")
history_ram = logger.get_history(memory_key="ram")
test("cpu has 2 entries", len(history_cpu) >= 2)
test("ram has 1 entry", len(history_ram) >= 1)


# ═══════════════════════════════════════════════
# 5. Get All Logs
# ═══════════════════════════════════════════════
print("\n━━━ 5. Get All Logs ━━━")

all_logs = logger.get_all(limit=10)
test("get_all is list", isinstance(all_logs, list))
test("get_all has entries", len(all_logs) >= 3)


# ═══════════════════════════════════════════════
# 6. Filter by Action
# ═══════════════════════════════════════════════
print("\n━━━ 6. Filter by Action ━━━")

archive_logs = logger.get_by_action("archive")
test("filter by action archive", len(archive_logs) >= 1)

keep_logs = logger.get_by_action("keep")
test("filter by action keep", len(keep_logs) >= 1)


# ═══════════════════════════════════════════════
# 7. Decision Stats
# ═══════════════════════════════════════════════
print("\n━━━ 7. Decision Stats ━━━")

stats = logger.get_stats()
test("stats has total", "total" in stats)
test("stats has by_action", "by_action" in stats)
test("stats has archive count", "archive" in stats["by_action"])


# ═══════════════════════════════════════════════
# 8. Persistence
# ═══════════════════════════════════════════════
print("\n━━━ 8. Persistence ━━━")

logger.close()

# Open the backend so _conn is available
backend2 = SQLiteBackend(db_path=db_path)
backend2.open()
logger2 = DecisionLogger(backend=backend2)
history = logger2.get_history(memory_key="cpu")
test("logs persist after reopen", len(history) >= 2)
logger2.close()
backend2.close()


# ═══════════════════════════════════════════════
# 9. Reflection Helper
# ═══════════════════════════════════════════════
print("\n━━━ 9. Reflection Helper ━━━")

backend3 = SQLiteBackend(db_path=db_path)
backend3.open()
logger3 = DecisionLogger(backend=backend3)
recent = logger3.get_recent_decisions(hours=24)
test("get_recent_decisions is list", isinstance(recent, list))
logger3.close()
backend3.close()


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
