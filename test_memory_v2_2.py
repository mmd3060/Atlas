"""
Memory System v2.2 — Architecture Tests

Tests the CLEAN architecture:
    Brain → Coordinator → Router → Pipeline → Repository → Backend

Each layer has exactly ONE responsibility.
"""

import sys
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
# 1. MemoryRepository (replaces MemoryEngine)
# ═══════════════════════════════════════════════
print("\n━━━ 1. MemoryRepository ━━━")

repo = MemoryRepository()
repo.open()

repo.save("user", "name", "MMD")
test("save + load", repo.load("user", "name") == "MMD")
test("exists", repo.exists("user", "name"))
test("count", repo.count("user") >= 1)
test("list_keys", "name" in repo.list_keys("user"))

repo.update("user", "name", "Mohammad")
test("update", repo.load("user", "name") == "Mohammad")

repo.delete("user", "name")
test("delete", not repo.exists("user", "name"))
test("load missing", repo.load("user", "x", "default") == "default")

ctx = repo.get_context()
test("get_context", isinstance(ctx, dict))

repo.close()
test("health after close", not repo.health())


# ═══════════════════════════════════════════════
# 2. MemoryPipeline (decision maker)
# ═══════════════════════════════════════════════
print("\n━━━ 2. MemoryPipeline ━━━")

pipeline = MemoryPipeline()

# Test analyze + store
result = pipeline.process("اسم من محمد است")
test("pipeline saved user info", result["status"] in ["saved", "stored"])
test("pipeline category is user", result["category"] == "user")

# Test ignore
result = pipeline.process("سلام")
test("pipeline ignores greeting", result["status"] == "ignored")

# Test forced importance
result = pipeline.process("این مهمه", importance=0.95)
test("forced importance saved", result["status"] in ["saved", "stored"])

# Test build_record (private method, but Pipeline's responsibility)
rec = pipeline._build_record(key="test::key", value="val", memory_type="project", importance=0.6)
test("build_record type", rec.memory_type == "project")
test("build_record importance", rec.importance == 0.6)

# Pipeline should NOT have: route(), export_context(), process_message()
test("no route method", not hasattr(pipeline, 'route'))
test("no export_context method", not hasattr(pipeline, 'export_context'))
test("no process_message method", not hasattr(pipeline, 'process_message'))


# ═══════════════════════════════════════════════
# 3. MemoryRouter (PURE SWITCH)
# ═══════════════════════════════════════════════
print("\n━━━ 3. MemoryRouter (PURE SWITCH) ━━━")

p = MemoryPipeline()
r = MemoryRouter(pipeline=p)

result = r.route("سلام Atlas", source="brain")
test("route brain → pipeline", result["status"] in ["saved", "stored", "ignored"])

result = r.route("test", source="tool")
test("route tool → pipeline", result["status"] in ["saved", "stored", "ignored"])

result = r.route("test", source="agent")
test("route agent → pipeline", result["status"] in ["saved", "stored", "ignored"])

# Router should NOT have: store(), retrieve(), search(), MemoryRecord, Policy
test("no store method", not hasattr(r, 'store'))
test("no retrieve method", not hasattr(r, 'retrieve'))
test("no search method", not hasattr(r, 'search'))
test("no export_context method", not hasattr(r, 'export_context'))
test("no process_message method", not hasattr(r, 'process_message'))


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
test("process_brain_request", result["status"] in ["saved", "stored", "ignored"])

# Tool output
result = coord.process_tool_output("tool output")
test("process_tool_output", result["status"] in ["saved", "stored", "ignored"])

# Route delegation
result = coord.route("test", source="brain")
test("route delegation", result["status"] in ["saved", "stored", "ignored"])

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
# 5. ContextBuilder (context snapshots)
# ═══════════════════════════════════════════════
print("\n━━━ 5. ContextBuilder ━━━")

b = DictBackend()
b.open()
b.put(MemoryRecord(key="user::test", value="hello", memory_type="user", importance=0.8))

builder = ContextBuilder(backend=b)
ctx = builder.export()
test("export has timestamp", "timestamp" in ctx)
test("export has memories", "memories" in ctx)
test("export has user records", len(ctx["memories"]["user"]) >= 1)

summary = builder.export_summary()
test("summary total", summary["total_records"] >= 1)

text = builder.export_for_brain()
test("brain export is string", isinstance(text, str))

b.close()


# ═══════════════════════════════════════════════
# 6. Architecture Rules — verify separation
# ═══════════════════════════════════════════════
print("\n━━━ 6. Architecture Rules ━━━")

# Router should be thin
import inspect
router_source = inspect.getsource(MemoryRouter)
test("Router has no MemoryRecord import", "MemoryRecord" not in router_source)
test("Router has no Policy import", "MemoryPolicy" not in router_source)
test("Router has no Backend import", "MemoryBackend" not in router_source)

# Pipeline builds records
pipeline_source = inspect.getsource(MemoryPipeline)
test("Pipeline has MemoryRecord", "MemoryRecord" in pipeline_source)
test("Pipeline has Policy", "MemoryPolicy" in pipeline_source)

# Coordinator is the entry point
coord_source = inspect.getsource(MemoryCoordinator)
test("Coordinator has process_message", "def process_message" in coord_source)
test("Coordinator has process_brain_request", "def process_brain_request" in coord_source)


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
test("full flow brain", result["status"] in ["saved", "stored", "ignored"])

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
