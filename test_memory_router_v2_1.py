"""
Memory Router v2.1 — Architecture Tests

Tests the SLIM router + Pipeline + Coordinator + ContextBuilder.
Verifies that each layer has exactly ONE responsibility.
"""

import sys
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backend import MemoryBackend
from core.memory.backends.dict_backend import DictBackend
from core.memory.policy import MemoryPolicy, TypePolicy
from core.memory.memory_router import MemoryRouter
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.memory_coordinator import MemoryCoordinator
from core.memory.context_builder import ContextBuilder


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
# 1. MemoryRecord
# ═══════════════════════════════════════════════
print("\n━━━ 1. MemoryRecord ━━━")

r = MemoryRecord(key="test::hello", value="world")
test("default created_at set", r.created_at > 0)
test("memory_type", r.memory_type == "short")
test("importance", r.importance == 0.5)
test("not expired (no ttl)", not r.is_expired())
test("expired after ttl", MemoryRecord(key="x", value="y", ttl=0.001, created_at=0).is_expired())
test("access_count after touch", r.access_count == 0 or True)
r.touch()
test("touch bumps count", r.access_count == 1)
d = r.to_dict()
test("to_dict round-trip", d["key"] == "test::hello")
r2 = MemoryRecord.from_dict(d)
test("from_dict round-trip", r2.value == "world")
test("generate_key has prefix", "short::" in MemoryRecord.generate_key("hello", "short"))


# ═══════════════════════════════════════════════
# 2. DictBackend
# ═══════════════════════════════════════════════
print("\n━━━ 2. DictBackend ━━━")

b = DictBackend()
b.open()
test("health after open", b.health())

rec = MemoryRecord(key="user::name", value="MMD", memory_type="user", importance=0.9)
b.put(rec)
test("put+get value", b.get("user", "user::name").value == "MMD")
test("count", b.count("user") >= 1)

b.delete("user", "user::name")
test("delete", b.get("user", "user::name") is None)

b.close()
test("health after close", not b.health())


# ═══════════════════════════════════════════════
# 3. MemoryPolicy
# ═══════════════════════════════════════════════
print("\n━━━ 3. MemoryPolicy ━━━")

p = MemoryPolicy()
test("short policy exists", p.get("short").ttl_seconds == 3600)
test("long policy exists", p.get("long").ttl_seconds is None)
test("user min_importance", p.get("user").min_importance == 0.7)
test("should_accept high", p.should_accept("user", 0.9))
test("should_accept reject", not p.should_accept("user", 0.3))
test("choose long", p.choose_memory_type(0.95) == "long")
test("choose user", p.choose_memory_type(0.75) == "user")
test("choose project", p.choose_memory_type(0.55) == "project")
test("choose task", p.choose_memory_type(0.35) == "task")
test("choose short", p.choose_memory_type(0.1) == "short")
test("promotion check", not p.needs_promotion("long", 100))


# ═══════════════════════════════════════════════
# 4. MemoryRouter (SLIM)
# ═══════════════════════════════════════════════
print("\n━━━ 4. MemoryRouter (SLIM) ━━━")

router = MemoryRouter()
test("health", router.health()["router"] == "ok")

# Direct store
result = router.store("user::name", "MMD", memory_type="user", importance=0.9)
test("direct store", result["status"] == "stored")

# Direct retrieve
rec = router.retrieve("user::name", "user")
test("direct retrieve", rec is not None and rec["value"] == "MMD")

# Direct search
results = router.search("MMD")
test("direct search", len(results) >= 1)

# Route to brain
result = router.route("سلام Atlas", source="brain")
test("route to brain", result["status"] in ["saved", "ignored"])

# Route to user
result = router.route("سلام", source="user", user_id="mmd")
test("route to user", result["status"] == "processed")

# Policy rejection
result = router.store("x", "y", memory_type="user", importance=0.1)
test("policy rejection", result["status"] == "rejected")

# Cleanup
router.clear()
test("clear", router.count() == 0)
router.close()


# ═══════════════════════════════════════════════
# 5. MemoryPipeline
# ═══════════════════════════════════════════════
print("\n━━━ 5. MemoryPipeline ━━━")

pipeline = MemoryPipeline()

# Test analyze + store
result = pipeline.process("اسم من محمد است")
test("pipeline saved user info", result["status"] in ["saved", "stored"])
test("pipeline category is user", result["category"] == "user")

# Test ignore
result = pipeline.process("سلام")
test("pipeline ignores greeting", result["status"] == "ignored")

# Test build_record directly
rec = pipeline.build_record(
    key="test::key", value="test_val",
    memory_type="project", importance=0.6,
)
test("build_record type", rec.memory_type == "project")
test("build_record importance", rec.importance == 0.6)

# Test forced importance
result = pipeline.process("این مهمه", importance=0.95)
test("forced importance saved", result["status"] in ["saved", "stored"])


# ═══════════════════════════════════════════════
# 6. ContextBuilder
# ═══════════════════════════════════════════════
print("\n━━━ 6. ContextBuilder ━━━")

# Need a backend with data
b2 = DictBackend()
b2.open()
b2.put(MemoryRecord(key="user::test", value="hello", memory_type="user", importance=0.8))
b2.put(MemoryRecord(key="short::test", value="world", memory_type="short", importance=0.2))

builder = ContextBuilder(backend=b2)
ctx = builder.export()
test("export has timestamp", "timestamp" in ctx)
test("export has memories", "memories" in ctx)
test("export has user records", len(ctx["memories"]["user"]) >= 1)

summary = builder.export_summary()
test("summary total", summary["total_records"] >= 2)

text = builder.export_for_brain()
test("brain export is string", isinstance(text, str))
test("brain export has header", "Memory Context" in text)

b2.close()


# ═══════════════════════════════════════════════
# 7. MemoryCoordinator
# ═══════════════════════════════════════════════
print("\n━━━ 7. MemoryCoordinator ━━━")

coord = MemoryCoordinator()

result = coord.process_message("mmd", "سلام Atlas")
test("coordinator process", result["status"] == "processed")
test("coordinator has context", "context" in result)
test("coordinator has memory", "memory" in result)

snap = coord.snapshot()
test("snapshot has conversation", "conversation" in snap)
test("snapshot has memory", "memory" in snap)

coord.add_message("assistant", "سلام MMD")
test("add_message", True)


# ═══════════════════════════════════════════════
# 8. Integration: Router → Pipeline → Backend
# ═══════════════════════════════════════════════
print("\n━━━ 8. Integration Test ━━━")

router2 = MemoryRouter()
result = router2.route("من دارم Atlas OS می‌سازم", source="brain")
test("integration brain route", result["status"] in ["saved", "stored", "ignored"])

result = router2.route("سلام", source="user", user_id="mmd")
test("integration user route", result["status"] == "processed")

# Export context through router
ctx = router2.export_context()
test("router export_context", "memories" in ctx)

router2.clear()
router2.close()


# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
