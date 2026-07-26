"""
SQLite Backend Tests — TDD Approach

Tests that SQLiteBackend implements MemoryBackend correctly
and persists data across restarts.

Test flow:
  1. Write tests FIRST
  2. Run tests → all FAIL
  3. Implement SQLiteBackend
  4. Run tests → all PASS
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend


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
# 1. Import & Interface
# ═══════════════════════════════════════════════
print("\n━━━ 1. Import & Interface ━━━")

try:
    from core.memory.backends.sqlite_backend import SQLiteBackend
    test("import SQLiteBackend", True)
except ImportError as e:
    test("import SQLiteBackend", False)
    print(f"    Error: {e}")
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    sys.exit(1)

# Check it implements MemoryBackend
test("implements MemoryBackend", issubclass(SQLiteBackend, MemoryBackend))


# ═══════════════════════════════════════════════
# 2. Lifecycle
# ═══════════════════════════════════════════════
print("\n━━━ 2. Lifecycle ━━━")

db_path = tempfile.mktemp(suffix=".db")
backend = SQLiteBackend(db_path=db_path)

test("not healthy before open", not backend.health())
backend.open()
test("healthy after open", backend.health())
backend.close()
test("not healthy after close", not backend.health())


# ═══════════════════════════════════════════════
# 3. CRUD Operations
# ═══════════════════════════════════════════════
print("\n━━━ 3. CRUD Operations ━━━")

backend = SQLiteBackend(db_path=db_path)
backend.open()

# PUT
rec = MemoryRecord(key="user::name", value="MMD", memory_type="user", importance=0.9)
backend.put(rec)
test("put + get", backend.get("user", "user::name").value == "MMD")

# GET missing
test("get missing", backend.get("user", "nonexistent") is None)

# UPDATE
rec2 = MemoryRecord(key="user::name", value="Mohammad", memory_type="user", importance=0.95)
backend.update(rec2)
test("update", backend.get("user", "user::name").value == "Mohammad")

# DELETE
deleted = backend.delete("user", "user::name")
test("delete exists", deleted)
test("get after delete", backend.get("user", "user::name") is None)
test("delete missing", not backend.delete("user", "nonexistent"))


# ═══════════════════════════════════════════════
# 4. Multiple Memory Types
# ═══════════════════════════════════════════════
print("\n━━━ 4. Multiple Memory Types ━━━")

backend.put(MemoryRecord(key="user::name", value="MMD", memory_type="user", importance=0.9))
backend.put(MemoryRecord(key="short::temp", value="temp data", memory_type="short", importance=0.2))
backend.put(MemoryRecord(key="project::atlas", value="Atlas OS", memory_type="project", importance=0.8))
backend.put(MemoryRecord(key="experience::error", value="403 error", memory_type="experience", importance=0.7))

test("count user", backend.count("user") >= 1)
test("count short", backend.count("short") >= 1)
test("count project", backend.count("project") >= 1)
test("count experience", backend.count("experience") >= 1)
test("count all", backend.count() >= 4)


# ═══════════════════════════════════════════════
# 5. List Records
# ═══════════════════════════════════════════════
print("\n━━━ 5. List Records ━━━")

records = backend.list_records(memory_type="user")
test("list_records user", len(records) >= 1)
test("list_records type", records[0].memory_type == "user")

records = backend.list_records(limit=2)
test("list_records limit", len(records) <= 2)

records = backend.list_records()
test("list_records all", len(records) >= 4)


# ═══════════════════════════════════════════════
# 6. Search
# ═══════════════════════════════════════════════
print("\n━━━ 6. Search ━━━")

results = backend.search("MMD")
test("search finds MMD", len(results) >= 1)

results = backend.search("atlas", memory_types=["project"])
test("search filtered by type", len(results) >= 1)

results = backend.search("nonexistent_xyz")
test("search no results", len(results) == 0)

results = backend.search("MMD", min_importance=0.5)
test("search with min_importance", len(results) >= 1)

results = backend.search("MMD", min_importance=0.99)
test("search high min_importance", len(results) == 0)


# ═══════════════════════════════════════════════
# 7. Expiry / TTL
# ═══════════════════════════════════════════════
print("\n━━━ 7. Expiry / TTL ━━━")

# Insert expired record
expired = MemoryRecord(
    key="short::expired", value="old data",
    memory_type="short", importance=0.1,
    ttl=0.001, created_at=0,  # expired long ago
)
backend.put(expired)
test("expired record stored", backend.get("short", "short::expired") is not None)

# purge_expired
count = backend.purge_expired()
test("purge_expired removes", count >= 1)
test("expired record gone", backend.get("short", "short::expired") is None)


# ═══════════════════════════════════════════════
# 8. Clear
# ═══════════════════════════════════════════════
print("\n━━━ 8. Clear ━━━")

backend.put(MemoryRecord(key="user::temp", value="temp", memory_type="user", importance=0.3))
count_before = backend.count("user")
backend.clear("user")
test("clear category", backend.count("user") == 0)
test("other categories intact", backend.count("project") >= 1)


# ═══════════════════════════════════════════════
# 9. Persistence (THE KEY TEST)
# ═══════════════════════════════════════════════
print("\n━━━ 9. Persistence ━━━")

# Save data
backend.put(MemoryRecord(key="user::persistent", value="survives restart", memory_type="user", importance=0.9))
backend.close()

# Reopen — data should survive
backend2 = SQLiteBackend(db_path=db_path)
backend2.open()
record = backend2.get("user", "user::persistent")
test("survives restart", record is not None)
test("value preserved", record.value == "survives restart")
backend2.close()


# ═══════════════════════════════════════════════
# 10. Metadata & Tags
# ═══════════════════════════════════════════════
print("\n━━━ 10. Metadata & Tags ━━━")

backend3 = SQLiteBackend(db_path=db_path)
backend3.open()

rec = MemoryRecord(
    key="user::tagged", value="with metadata",
    memory_type="user", importance=0.8,
    tags=["important", "verified"],
    metadata={"source": "telegram", "version": 2},
)
backend3.put(rec)
fetched = backend3.get("user", "user::tagged")
test("tags preserved", fetched.tags == ["important", "verified"])
test("metadata preserved", fetched.metadata == {"source": "telegram", "version": 2})

backend3.close()


# ═══════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════
if os.path.exists(db_path):
    os.remove(db_path)


# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
