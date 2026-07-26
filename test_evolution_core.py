"""
Agent Evolution Core v1 — TDD Tests

The self-improvement loop for Atlas.

Flow:
  Experience → Reflection → Hypothesis → Experiment → Evaluation → Change → Memory

Safety:
  - Max change per update = 0.05
  - Minimum confidence = 0.8
  - Need min experiences before update
  - Rollback capability
  - All changes logged

Usage:
    engine = EvolutionCore(adapter=memory_adapter, reflection=reflection_engine)
    result = engine.evolve(
        task="coding",
        lesson="github performs well",
        confidence=0.85,
    )
    # {status, change, rollback_id}
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

test("backend ready", backend.health())


# ═══════════════════════════════════════════════
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.evolution.weight_optimizer import WeightOptimizer
    from core.evolution.change_manager import ChangeManager
    from core.evolution.rollback_manager import RollbackManager
    from core.evolution.self_improvement_engine import SelfImprovementEngine
    test("import WeightOptimizer", True)
    test("import ChangeManager", True)
    test("import RollbackManager", True)
    test("import SelfImprovementEngine", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Weight Optimizer
# ═══════════════════════════════════════════════
print("\n━━━ 2. Weight Optimizer ━━━")

optimizer = WeightOptimizer()
test("optimizer created", optimizer is not None)

# Initial weight
w = optimizer.get_weight("coding", "github")
test("initial weight exists", w == 0.5)

# Update weight
optimizer.update(task="coding", provider="github", reward=0.9)
w_new = optimizer.get_weight("coding", "github")
test("weight updated", w_new > 0.5)
test("weight within max change", abs(w_new - 0.5) <= 0.06)


# ═══════════════════════════════════════════════
# 3. Change Manager
# ═══════════════════════════════════════════════
print("\n━━━ 3. Change Manager ━━━")

manager = ChangeManager()
test("manager created", manager is not None)

# Record a change
change_id = manager.record_change(
    target="github",
    task="coding",
    old_value=0.5,
    new_value=0.55,
    reason="high success rate",
    confidence=0.85,
)
test("change recorded", change_id is not None)
test("change has id", isinstance(change_id, str))


# ═══════════════════════════════════════════════
# 4. Rollback Manager
# ═══════════════════════════════════════════════
print("\n━━━ 4. Rollback Manager ━━━")

rollback = RollbackManager(optimizer=optimizer)
test("rollback manager created", rollback is not None)

# Set initial weight
optimizer.set_weight("coding", "github", 0.5)

# Save snapshot
snapshot_id = rollback.save_snapshot()
test("snapshot saved", snapshot_id is not None)

# Make a change
optimizer.update(task="coding", provider="github", reward=0.95)
w_after = optimizer.get_weight("coding", "github")
test("weight changed", w_after > 0.5)

# Rollback
rollback.restore_snapshot(snapshot_id)
w_restored = optimizer.get_weight("coding", "github")
test("rollback works", w_restored == 0.5)


# ═══════════════════════════════════════════════
# 5. Safety Rules
# ═══════════════════════════════════════════════
print("\n━━━ 5. Safety Rules ━━━")

from core.evolution.self_improvement_engine import EvolutionRules

rules = EvolutionRules()
test("rules created", rules is not None)
test("max change defined", rules.max_change > 0)
test("min confidence defined", rules.min_confidence > 0)
test("min experiences defined", rules.min_experiences > 0)


# ═══════════════════════════════════════════════
# 6. Self Improvement Engine
# ═══════════════════════════════════════════════
print("\n━━━ 6. Self Improvement Engine ━━━")

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)

engine = SelfImprovementEngine(
    adapter=adapter,
    optimizer=optimizer,
    change_manager=manager,
    rollback_manager=rollback,
)
test("engine created", engine is not None)


# ═══════════════════════════════════════════════
# 7. Evolve with High Confidence
# ═══════════════════════════════════════════════
print("\n━━━ 7. Evolve with High Confidence ━━━")

result = engine.evolve(
    task="coding",
    lesson="github performs well for coding",
    confidence=0.9,
    provider="github",
)
test("evolve returns dict", isinstance(result, dict))
test("has status", "status" in result)
test("has change", "change" in result)


# ═══════════════════════════════════════════════
# 8. Evolve with Low Confidence (rejected)
# ═══════════════════════════════════════════════
print("\n━━━ 8. Evolve with Low Confidence ━━━")

result = engine.evolve(
    task="coding",
    lesson="maybe gemini is okay",
    confidence=0.3,
    provider="gemini",
)
test("low confidence rejected", result["status"] == "rejected")


# ═══════════════════════════════════════════════
# 9. Evolution Stats
# ═══════════════════════════════════════════════
print("\n━━━ 9. Evolution Stats ━━━")

stats = engine.get_stats()
test("stats has total_changes", "total_changes" in stats)
test("stats has rollbacks", "rollbacks" in stats)


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
