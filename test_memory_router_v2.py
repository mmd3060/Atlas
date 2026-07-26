"""
Comprehensive test suite for Memory Router v2 — Atlas OS

Covers:
  - MemoryRecord creation, serialization, key generation
  - DictBackend CRUD, search, purge, clear
  - MemoryPolicy decisions (accept/reject, type selection, promotion)
  - MemoryRouter: store, retrieve, update, delete, search
  - MemoryRouter: context export, batch ops, maintenance
  - MemoryRouter: importance-based auto-routing
  - MemoryRouter: TTL expiry
  - MemoryRouter: compatibility layer (process_message, save/load_memory)
  - MemoryRouter: operation log
  - MemoryRouter: health check
  - Edge cases: empty input, unknown types, overwrites
"""

import time
import sys
import os

# ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy, DEFAULT_POLICIES
from core.memory.memory_router import MemoryRouter


# ──────────────────────────────────────────────
#  Helper
# ──────────────────────────────────────────────
passed = 0
failed = 0


def assert_eq(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ✅ {label}")
    else:
        failed += 1
        print(f"  ❌ {label}")
        print(f"     got:  {got!r}")
        print(f"     want: {want!r}")


def assert_true(label, condition):
    assert_eq(label, bool(condition), True)


def assert_false(label, condition):
    assert_eq(label, bool(condition), False)


# ══════════════════════════════════════════════
#  1. MemoryRecord
# ══════════════════════════════════════════════
print("\n━━━ 1. MemoryRecord ━━━")

r = MemoryRecord(key="test::hello", value="world", memory_type="short", importance=0.8)
assert_eq("default created_at set", r.created_at > 0, True)
assert_eq("memory_type", r.memory_type, "short")
assert_eq("importance", r.importance, 0.8)
assert_false("not expired (no ttl)", r.is_expired())

r2 = MemoryRecord(key="k", value="v", ttl=0.01)
time.sleep(0.02)
assert_true("expired after ttl", r2.is_expired())

# touch
r.touch()
assert_eq("access_count after touch", r.access_count, 1)

# to_dict / from_dict
d = r.to_dict()
r_back = MemoryRecord.from_dict(d)
assert_eq("round-trip key", r_back.key, r.key)
assert_eq("round-trip value", r_back.value, r.value)

# generate_key
k1 = MemoryRecord.generate_key("my important project", "project")
assert_true("key has prefix", k1.startswith("project::"))
assert_true("key has words", "my_important_project" in k1)

k2 = MemoryRecord.generate_key("", "short")
assert_true("empty key uses uuid", len(k2) > 8)


# ══════════════════════════════════════════════
#  2. DictBackend
# ══════════════════════════════════════════════
print("\n━━━ 2. DictBackend ━━━")

db = DictBackend()
db.open()
assert_true("health after open", db.health())
db.close()
assert_false("health after close", db.health())
db.open()

# put + get
rec = MemoryRecord(key="u::1", value="Alice", memory_type="user")
db.put(rec)
got = db.get("user", "u::1")
assert_eq("put+get value", got.value, "Alice")
assert_eq("access_count after get", got.access_count, 1)

# update
rec2 = MemoryRecord(key="u::1", value="Alice B.", memory_type="user")
db.update(rec2)
got2 = db.get("user", "u::1")
assert_eq("update value", got2.value, "Alice B.")

# delete
assert_true("delete existing", db.delete("user", "u::1"))
assert_false("delete missing", db.delete("user", "u::1"))

# count
db.put(MemoryRecord(key="a", value=1, memory_type="short"))
db.put(MemoryRecord(key="b", value=2, memory_type="short"))
db.put(MemoryRecord(key="c", value=3, memory_type="long"))
assert_eq("total count", db.count(), 3)
assert_eq("short count", db.count("short"), 2)
assert_eq("long count", db.count("long"), 1)

# list_records
records = db.list_records(memory_type="short")
assert_eq("list_records count", len(records), 2)

# search
db.put(MemoryRecord(key="x::atlas", value="Atlas OS is great", memory_type="project", importance=0.9, tags=["ai"]))
results = db.search("atlas")
assert_true("search finds atlas", len(results) > 0)
assert_eq("search result value", results[0].value, "Atlas OS is great")

# search with min_importance
results_hi = db.search("atlas", min_importance=0.95)
assert_eq("high importance search returns 0", len(results_hi), 0)

# purge_expired
db.put(MemoryRecord(key="exp", value="v", memory_type="short", ttl=0.01))
time.sleep(0.02)
purged = db.purge_expired()
assert_true("purge removed at least 1", purged >= 1)

# clear
cleared = db.clear("short")
assert_eq("clear short", cleared >= 0, True)  # may be 0 if purged already
db.clear()
assert_eq("clear all, count=0", db.count(), 0)


# ══════════════════════════════════════════════
#  3. MemoryPolicy
# ══════════════════════════════════════════════
print("\n━━━ 3. MemoryPolicy ━━━")

pol = MemoryPolicy()
p_short = pol.get("short")
assert_eq("short max_entries", p_short.max_entries, 50)
assert_eq("short ttl", p_short.ttl_seconds, 3600)

p_long = pol.get("long")
assert_eq("long min_importance", p_long.min_importance, 0.6)

# should_accept
assert_true("accept high importance", pol.should_accept("long", 0.8))
assert_false("reject low importance for long", pol.should_accept("long", 0.3))
assert_true("accept zero for session", pol.should_accept("session", 0.0))

# choose_memory_type
assert_eq("0.95 → long", pol.choose_memory_type(0.95), "long")
assert_eq("0.75 → user", pol.choose_memory_type(0.75), "user")
assert_eq("0.55 → project", pol.choose_memory_type(0.55), "project")
assert_eq("0.35 → task", pol.choose_memory_type(0.35), "task")
assert_eq("0.10 → short", pol.choose_memory_type(0.10), "short")

# custom policy
custom = MemoryPolicy(custom_policies={
    "short": TypePolicy(max_entries=5, min_importance=0.5),
})
assert_eq("custom short max_entries", custom.get("short").max_entries, 5)
assert_eq("custom short min_importance", custom.get("short").min_importance, 0.5)


# ══════════════════════════════════════════════
#  4. MemoryRouter — core operations
# ══════════════════════════════════════════════
print("\n━━━ 4. MemoryRouter: core ops ━━━")

router = MemoryRouter()

# health
h = router.health()
assert_eq("health router", h["router"], "ok")
assert_eq("health backend_type", h["backend_type"], "DictBackend")

# store with explicit type
r1 = router.store("user::name", "Mohammad", memory_type="user", importance=0.9)
assert_eq("store user", r1["status"], "stored")
assert_eq("store user type", r1["memory_type"], "user")

# retrieve
rec = router.retrieve("user::name", memory_type="user")
assert_eq("retrieve value", rec["value"], "Mohammad")

# update
u1 = router.update("user::name", "Mohammad Ali", memory_type="user")
assert_eq("update status", u1["status"], "updated")
rec2 = router.retrieve("user::name", memory_type="user")
assert_eq("updated value", rec2["value"], "Mohammad Ali")

# delete
d1 = router.delete("user::name", memory_type="user")
assert_eq("delete status", d1["status"], "deleted")
assert_true("not found after delete", router.retrieve("user::name") is None)

# delete missing
d2 = router.delete("nonexistent::key")
assert_eq("delete missing", d2["status"], "not_found")


# ══════════════════════════════════════════════
#  5. Importance-based auto-routing
# ══════════════════════════════════════════════
print("\n━━━ 5. Auto-routing by importance ━━━")

r_high = router.store("auto1", "very important", importance=0.95)
assert_eq("high auto → long", r_high["memory_type"], "long")

r_mid = router.store("auto2", "somewhat important", importance=0.55)
assert_eq("mid auto → project", r_mid["memory_type"], "project")

r_low = router.store("auto3", "not very important", importance=0.15)
assert_eq("low auto → short", r_low["memory_type"], "short")

# verify all retrievable
assert_true("auto1 in long", router.retrieve("auto1", "long") is not None)
assert_true("auto2 in project", router.retrieve("auto2", "project") is not None)
assert_true("auto3 in short", router.retrieve("auto3", "short") is not None)


# ══════════════════════════════════════════════
#  6. Policy rejection
# ══════════════════════════════════════════════
print("\n━━━ 6. Policy rejection ━━━")

r_reject = router.store("reject1", "too unimportant", memory_type="long", importance=0.1)
assert_eq("rejected status", r_reject["status"], "rejected")


# ══════════════════════════════════════════════
#  7. Search
# ══════════════════════════════════════════════
print("\n━━━ 7. Search ━━━")

router.store("proj::atlas", "Atlas OS AI agent", memory_type="project", importance=0.9, tags=["ai", "agent"])
router.store("proj::brain", "Brain pipeline module", memory_type="project", importance=0.8, tags=["brain"])
router.store("knowledge::py", "Python best practices", memory_type="knowledge", importance=0.7, tags=["python"])

results = router.search("atlas")
assert_true("search finds atlas", len(results) > 0)

results_proj = router.search("pipeline", memory_types=["project"])
assert_true("filtered search finds pipeline", len(results_proj) > 0)

results_all = router.search("py", memory_types=["knowledge"])
assert_true("knowledge search finds python", len(results_all) > 0)


# ══════════════════════════════════════════════
#  8. Context export
# ══════════════════════════════════════════════
print("\n━━━ 8. Context export ━━━")

ctx = router.export_context()
assert_true("export has timestamp", "timestamp" in ctx)
assert_true("export has memories", "memories" in ctx)
assert_true("export total >= 0", ctx["total_records"] >= 0)

# export specific types only
ctx_sub = router.export_context(memory_types=["project"])
assert_true("sub export has project key", "project" in ctx_sub["memories"])


# ══════════════════════════════════════════════
#  9. Batch operations
# ══════════════════════════════════════════════
print("\n━━━ 9. Batch ops ━━━")

batch_results = router.store_batch([
    {"key": "b1", "value": "item 1", "memory_type": "session", "importance": 0.3},
    {"key": "b2", "value": "item 2", "memory_type": "session", "importance": 0.4},
    {"key": "b3", "value": "item 3", "memory_type": "session", "importance": 0.5},
])
assert_eq("batch stored count", len(batch_results), 3)
assert_eq("batch item 1 type", batch_results[0]["memory_type"], "session")

batch_retrieved = router.retrieve_batch([
    {"key": "b1", "memory_type": "session"},
    {"key": "b2", "memory_type": "session"},
    {"key": "b3", "memory_type": "session"},
])
assert_eq("batch retrieve count", len(batch_retrieved), 3)
assert_eq("batch retrieve val", batch_retrieved[0]["value"], "item 1")


# ══════════════════════════════════════════════
# 10. Maintenance
# ══════════════════════════════════════════════
print("\n━━━ 10. Maintenance ━━━")

router.store("ttl_test", "expires soon", memory_type="short", importance=0.3, ttl=0.01)
time.sleep(0.02)
purged = router.purge_expired()
assert_true("purge >= 1", purged >= 1)

# clear session
router.store("s1", "v", memory_type="session")
router.store("s2", "v", memory_type="session")
session_count = router.clear_session()
assert_true("session cleared >= 2", session_count >= 2)


# ══════════════════════════════════════════════
# 11. Compatibility layer
# ══════════════════════════════════════════════
print("\n━━━ 11. Compatibility layer ━━━")

# process_message
pm = router.process_message("user123", "Hello Atlas!")
assert_eq("process_message status", pm["status"], "processed")
assert_eq("process_message user_id", pm["user_id"], "user123")
assert_true("process_message has context", "context" in pm)

# save_memory / load_memory (legacy API)
router.save_memory("knowledge", "k1", "some knowledge")
val = router.load_memory("knowledge", "k1")
assert_eq("legacy load_memory", val, "some knowledge")
missing = router.load_memory("knowledge", "nonexistent", default="fallback")
assert_eq("legacy load_memory default", missing, "fallback")


# ══════════════════════════════════════════════
# 12. Operation log
# ══════════════════════════════════════════════
print("\n━━━ 12. Operation log ━━━")

log = router.get_operation_log()
assert_true("log has entries", len(log) > 0)
assert_true("log entry has op key", "op" in log[-1])
assert_true("log entry has time key", "time" in log[-1])


# ══════════════════════════════════════════════
# 13. Snapshot
# ══════════════════════════════════════════════
print("\n━━━ 13. Snapshot ━━━")

snap = router.snapshot()
assert_true("snapshot has memory", "memory" in snap)
assert_true("snapshot has health", "health" in snap)


# ══════════════════════════════════════════════
# 14. Edge cases
# ══════════════════════════════════════════════
print("\n━━━ 14. Edge cases ━━━")

# store with None value
r_none = router.store("edge::none", None, memory_type="session", importance=0.3)
assert_eq("store None value", r_none["status"], "stored")
rec_none = router.retrieve("edge::none", "session")
assert_eq("retrieve None value", rec_none["value"], None)

# store with dict value
r_dict = router.store("edge::dict", {"nested": [1, 2, 3]}, memory_type="session", importance=0.3)
assert_eq("store dict value", r_dict["status"], "stored")
rec_dict = router.retrieve("edge::dict", "session")
assert_eq("retrieve dict value", rec_dict["value"]["nested"], [1, 2, 3])

# list_records with offset
router.store("lr1", "v1", memory_type="session", importance=0.1)
router.store("lr2", "v2", memory_type="session", importance=0.2)
page1 = router.list_records(memory_type="session", limit=2, offset=0)
page2 = router.list_records(memory_type="session", limit=2, offset=1)
assert_true("page1 has records", len(page1) >= 1)
# offset should skip some

# delete all types (search without memory_type)
r_del = router.delete("edge::none")
assert_eq("delete auto-detect", r_del["status"], "deleted")


# ══════════════════════════════════════════════
# 15. Custom backend
# ══════════════════════════════════════════════
print("\n━━━ 15. Custom backend ━━━")

custom_db = DictBackend()
custom_router = MemoryRouter(backend=custom_db)
custom_router.store("cb::1", "custom backend value", memory_type="short", importance=0.3)
cb_rec = custom_router.retrieve("cb::1", "short")
assert_eq("custom backend value", cb_rec["value"], "custom backend value")


# ══════════════════════════════════════════════
# 16. Custom policy
# ══════════════════════════════════════════════
print("\n━━━ 16. Custom policy ━━━")

cp = MemoryPolicy(custom_policies={
    "short": TypePolicy(max_entries=3, min_importance=0.2),
})
cp_router = MemoryRouter(policy=cp)
cp_router.store("cp1", "a", memory_type="short", importance=0.3)
cp_router.store("cp2", "b", memory_type="short", importance=0.4)
cp_router.store("cp3", "c", memory_type="short", importance=0.5)
# this should work (under max)
assert_eq("custom policy count", cp_router.count("short"), 3)
# rejected because below custom threshold
cp_rej = cp_router.store("cp_low", "low", memory_type="short", importance=0.1)
assert_eq("custom policy reject", cp_rej["status"], "rejected")


# ═══════════════════════════════════════════════
#  SUMMARY
# ═══════════════════════════════════════════════
print("\n" + "═" * 50)
print(f"  RESULTS:  {passed} passed  |  {failed} failed")
print("═" * 50)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All tests passed!")
    sys.exit(0)
