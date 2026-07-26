"""
Memory Governance v1 — TDD Tests

Governance decides what to do with each memory:
  - KEEP: high quality, confident
  - PROMOTE: important, high quality, frequently used
  - ARCHIVE: old, low quality, unused
  - DELETE: duplicate or corrupted
  - CONFLICT: contradictory memories detected

Usage:
    gov = MemoryGovernance()
    decision = gov.evaluate(memory)
    # {action: "keep", confidence: 0.92, reason: "..."}

    detector = ConflictDetector()
    conflicts = detector.find_conflicts(memories)
"""

import sys
import os
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord


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
# 1. Import
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import ━━━")

try:
    from core.memory.governance import MemoryGovernance, ConflictDetector, GovernanceRules
    test("import MemoryGovernance", True)
except ImportError as e:
    test("import MemoryGovernance", False)
    print(f"    Error: {e}")
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Governance Rules
# ═══════════════════════════════════════════════
print("\n━━━ 2. Governance Rules ━━━")

rules = GovernanceRules()
test("rules created", rules is not None)
test("has quality threshold", rules.quality_threshold > 0)
test("has confidence threshold", rules.confidence_threshold > 0)
test("has promote threshold", rules.promote_threshold > 0)


# ═══════════════════════════════════════════════
# 3. Keep Decision
# ═══════════════════════════════════════════════
print("\n━━━ 3. Keep Decision ━━━")

gov = MemoryGovernance()

# High quality memory (below promote threshold for access)
result = gov.evaluate(importance=0.9, quality=0.9, confidence=0.8, access_count=2)
test("high quality → keep", result["action"] == "keep")
test("has confidence", "confidence" in result)
test("has reason", "reason" in result)

# Medium quality
result = gov.evaluate(importance=0.6, quality=0.65, confidence=0.6, access_count=3)
test("medium quality → keep", result["action"] == "keep")


# ═══════════════════════════════════════════════
# 4. Promote Decision
# ═══════════════════════════════════════════════
print("\n━━━ 4. Promote Decision ━━━")

result = gov.evaluate(importance=0.95, quality=0.9, confidence=0.9, access_count=10)
test("very high quality → promote", result["action"] == "promote")

result = gov.evaluate(importance=0.85, quality=0.85, confidence=0.85, access_count=8)
test("high quality + high access → promote", result["action"] == "promote")


# ═══════════════════════════════════════════════
# 5. Archive Decision
# ═══════════════════════════════════════════════
print("\n━━━ 5. Archive Decision ━━━")

result = gov.evaluate(importance=0.1, quality=0.1, confidence=0.1, access_count=0)
test("bad memory → archive", result["action"] == "archive")

result = gov.evaluate(importance=0.2, quality=0.15, confidence=0.2, access_count=0, age_days=30)
test("old bad memory → archive", result["action"] == "archive")


# ═══════════════════════════════════════════════
# 6. Delete Decision
# ═══════════════════════════════════════════════
print("\n━━━ 6. Delete Decision ━━━")

result = gov.evaluate(importance=0.0, quality=0.0, confidence=0.0, access_count=0, is_duplicate=True)
test("duplicate → delete", result["action"] == "delete")

result = gov.evaluate(importance=0.0, quality=0.0, confidence=0.0, access_count=0, is_corrupted=True)
test("corrupted → delete", result["action"] == "delete")


# ═══════════════════════════════════════════════
# 7. Conflict Detection
# ═══════════════════════════════════════════════
print("\n━━━ 7. Conflict Detection ━━━")

detector = ConflictDetector()

# Conflicting values
memory1 = {"key": "project_version", "value": "v1"}
memory2 = {"key": "project_version", "value": "v2"}
test("detects conflict", detector.has_conflict(memory1, memory2))

# Same values
memory3 = {"key": "project_version", "value": "v1"}
test("no conflict same value", not detector.has_conflict(memory1, memory3))

# Different keys
memory4 = {"key": "other_key", "value": "v2"}
test("no conflict different keys", not detector.has_conflict(memory1, memory4))

# Find all conflicts
memories = [
    {"key": "cpu", "value": "i3 9100"},
    {"key": "cpu", "value": "i5 14400"},
    {"key": "ram", "value": "16GB"},
    {"key": "ram", "value": "32GB"},
]
conflicts = detector.find_conflicts(memories)
test("finds multiple conflicts", len(conflicts) >= 2)


# ═══════════════════════════════════════════════
# 8. Batch Governance
# ═══════════════════════════════════════════════
print("\n━━━ 8. Batch Governance ━━━")

memories = [
    {"importance": 0.9, "quality": 0.9, "confidence": 0.8, "access_count": 5},
    {"importance": 0.1, "quality": 0.1, "confidence": 0.1, "access_count": 0},
    {"importance": 0.95, "quality": 0.9, "confidence": 0.9, "access_count": 10},
]
decisions = gov.evaluate_batch(memories)
test("batch returns list", isinstance(decisions, list))
test("batch correct count", len(decisions) == 3)
test("batch has actions", all("action" in d for d in decisions))


# ═══════════════════════════════════════════════
# 9. Governance Stats
# ═══════════════════════════════════════════════
print("\n━━━ 9. Governance Stats ━━━")

decisions = gov.evaluate_batch(memories)
stats = gov.get_stats(decisions)
test("stats has keep", "keep" in stats)
test("stats has promote", "promote" in stats)
test("stats has archive", "archive" in stats)
test("stats has delete", "delete" in stats)


# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
