"""
Memory System v2.2 — Final Architecture Tests

Architecture:
    Brain → Coordinator → Router → Pipeline → Repository → Backend

Each layer has exactly ONE responsibility.
No circular dependencies.
No Backend access from higher layers.
"""

import sys
import inspect
sys.path.insert(0, "/data/workspace/Atlas")

from core.memory.types import MemoryRecord, MEMORY_TYPES
from core.memory.backends.dict_backend import DictBackend
from core.memory.memory_repository import MemoryRepository
from core.memory.memory_pipeline import MemoryPipeline
from core.memory.memory_router import MemoryRouter
from core.memory.memory_coordinator import MemoryCoordinator
from core.memory.context_builder import ContextBuilder
from core.memory.policy import MemoryPolicy


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
# 1. MemoryRepository (upsert)
# ═══════════════════════════════════════════════
print("\n━━━ 1. MemoryRepository (upsert) ━━━")

repo = MemoryRepository()
repo.open()

# Test upsert
rec1 = MemoryRecord(key="user::name", value="MMD", memory_type="user", importance=0.9)
action = repo.upsert(rec1)
test("upsert insert", action == "stored")
test("upsert value", repo.load("user", "user::name") == "MMD")

# Upsert update
rec2 = MemoryRecord(key="user::name", value="Mohammad", memory_type="user", importance=0.95)
action = repo.upsert(rec2)
test("upsert update", action == "updated")
test("upsert updated value", repo.load("user", "user::name") == "Mohammad")

# save/load still works
repo.save("user", "user::test", "hello")
test("save + load", repo.load("user", "user::test") == "hello")

# exists
test("exists", repo.exists("user", "user::name"))

# count
test("count", repo.count("user") >= 1)

# list_keys
test("list_keys", "user::name" in repo.list_keys("user"))

# delete
repo.delete("user", "user::test")
test("delete", not repo.exists("user", "user::test"))

# get_context
ctx = repo.get_context()
test("get_context", isinstance(ctx, dict))

repo.close()


# ═══════════════════════════════════════════════
# 2. MemoryPipeline (uses upsert)
# ═══════════════════════════════════════════════
print("\n━━━ 2. MemoryPipeline ━━━")

pipeline = MemoryPipeline()

# Test analyze + store
result = pipeline.process("اسم من محمد است")
test("pipeline saved", result["status"] in ["saved", "stored", "updated"])
test("pipeline category", result["category"] == "user")

# Test ignore
result = pipeline.process("سلام")
test("pipeline ignores", result["status"] == "ignored")

# Test forced importance
result = pipeline.process("این مهمه", importance=0.95)
test("forced importance", result["status"] in ["saved", "stored", "updated"])

# Pipeline should NOT have: route(), export_context(), process_message()
test("no route", not hasattr(pipeline, 'route'))
test("no export_context", not hasattr(pipeline, 'export_context'))
test("no process_message", not hasattr(pipeline, 'process_message'))


# ═══════════════════════════════════════════════
# 3. MemoryRouter (PURE SWITCH — no Coordinator dependency)
# ═══════════════════════════════════════════════
print("\n━━━ 3. MemoryRouter (PURE SWITCH) ━━━")

p = MemoryPipeline()
r = MemoryRouter(pipeline=p)

result = r.route("سلام Atlas", source="brain")
test("route brain", result["status"] in ["saved", "stored", "updated", "ignored"])

result = r.route("test", source="tool")
test("route tool", result["status"] in ["saved", "stored", "updated", "ignored"])

result = r.route("test", source="agent")
test("route agent", result["status"] in ["saved", "stored", "updated", "ignored"])

# Router should NOT have: store(), retrieve(), search(), Coordinator
test("no store", not hasattr(r, 'store'))
test("no retrieve", not hasattr(r, 'retrieve'))
test("no search", not hasattr(r, 'search'))
test("no export_context", not hasattr(r, 'export_context'))
test("no process_message", not hasattr(r, 'process_message'))

# Verify no Coordinator import
router_source = inspect.getsource(MemoryRouter)
test("no Coordinator import", "Coordinator" not in router_source)
test("no MemoryRecord import", "MemoryRecord" not in router_source)
test("no Policy import", "MemoryPolicy" not in router_source)


# ═══════════════════════════════════════════════
# 4. MemoryCoordinator (THE ONLY entry point)
# ═══════════════════════════════════════════════
print("\n━━━ 4. MemoryCoordinator (ENTRY POINT) ━━━")

coord = MemoryCoordinator()

# User message
result = coord.process_message("mmd", "سلام Atlas")
test("process_message", result["status"] == "processed")
test("has context", "context" in result)
test("has memory", "memory" in result)

# Brain request
result = coord.process_brain_request("من دارم Atlas OS می‌سازم")
test("process_brain_request", result["status"] in ["saved", "stored", "updated", "ignored"])

# Tool output
result = coord.process_tool_output("tool output")
test("process_tool_output", result["status"] in ["saved", "stored", "updated", "ignored"])

# Route delegation
result = coord.route("test", source="brain")
test("route delegation", result["status"] in ["saved", "stored", "updated", "ignored"])

# Context export
ctx = coord.export_context()
test("export_context", "memories" in ctx)

brain_ctx = coord.export_context_for_brain()
test("export_context_for_brain", isinstance(brain_ctx, str))

# Direct memory ops
coord.save_memory("user", "test_key", "test_val")
test("save_memory", coord.load_memory("user", "test_key") == "test_val")

# Snapshot
snap = coord.snapshot()
test("snapshot", "conversation" in snap and "memory" in snap)


# ═══════════════════════════════════════════════
# 5. ContextBuilder (uses Repository, not Backend)
# ═══════════════════════════════════════════════
print("\n━━━ 5. ContextBuilder ━━━")

repo2 = MemoryRepository()
repo2.open()
repo2.save("user", "user::test", "hello")

builder = ContextBuilder(repository=repo2)
ctx = builder.export()
test("export has timestamp", "timestamp" in ctx)
test("export has memories", "memories" in ctx)
test("export has user records", len(ctx["memories"]["user"]) >= 1)

summary = builder.export_summary()
test("summary total", summary["total_records"] >= 1)

text = builder.export_for_brain()
test("brain export is string", isinstance(text, str))

# ContextBuilder should NOT import Backend
builder_source = inspect.getsource(ContextBuilder)
test("no Backend import", "MemoryBackend" not in builder_source)
test("no DictBackend import", "DictBackend" not in builder_source)

repo2.close()


# ═══════════════════════════════════════════════
# 6. Architecture Rules
# ═══════════════════════════════════════════════
print("\n━━━ 6. Architecture Rules ━━━")

# Router is thin
test("Router has no MemoryRecord", "MemoryRecord" not in inspect.getsource(MemoryRouter))
test("Router has no Policy", "MemoryPolicy" not in inspect.getsource(MemoryRouter))
test("Router has no Backend", "MemoryBackend" not in inspect.getsource(MemoryRouter))
test("Router has no Coordinator", "Coordinator" not in inspect.getsource(MemoryRouter))

# Pipeline builds records
test("Pipeline has MemoryRecord", "MemoryRecord" in inspect.getsource(MemoryPipeline))
test("Pipeline has Policy", "MemoryPolicy" in inspect.getsource(MemoryPipeline))

# Coordinator is entry point
test("Coordinator has process_message", "def process_message" in inspect.getsource(MemoryCoordinator))
test("Coordinator has process_brain_request", "def process_brain_request" in inspect.getsource(MemoryCoordinator))

# ContextBuilder uses Repository
test("ContextBuilder has repository", "repository" in inspect.getsource(ContextBuilder))
test("ContextBuilder has no Backend", "MemoryBackend" not in inspect.getsource(ContextBuilder))


# ═══════════════════════════════════════════════
# 7. Integration: Full flow
# ═══════════════════════════════════════════════
print("\n━━━ 7. Integration Test ━━━")

full_coord = MemoryCoordinator()

# User message → full pipeline
result = full_coord.process_message("mmd", "من دارم Atlas OS می‌سازم")
test("full flow user", result["status"] == "processed")

# Brain request → pipeline
result = full_coord.process_brain_request("این مهمه")
test("full flow brain", result["status"] in ["saved", "stored", "updated", "ignored"])

# Export context
ctx = full_coord.export_context()
test("full flow context", "memories" in ctx)

# Cleanup
full_coord.repository.clear()
test("cleanup", full_coord.repository.count() == 0)


# ═══════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
