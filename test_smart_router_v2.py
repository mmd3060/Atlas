"""
Smart Router v2 — TDD Tests

Atlas selects the BEST MODEL for each task, not just provider.

Flow:
  Input → Task Classifier → Model Registry → Score Models → Select Best

Features:
  - Model Registry with capabilities
  - Task classification (code/math/text/vision/voice)
  - Multi-factor scoring
  - Failover
  - Cost optimization
  - Memory influence
"""

import sys
import os
import tempfile
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
    from core.router.model_registry import ModelRegistry, ModelProfile
    from core.router.task_classifier import TaskClassifier
    from core.router.smart_router_v2 import SmartRouterV2
    test("import ModelRegistry", True)
    test("import TaskClassifier", True)
    test("import SmartRouterV2", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Model Registry
# ═══════════════════════════════════════════════
print("\n━━━ 2. Model Registry ━━━")

registry = ModelRegistry()
test("registry created", registry is not None)

# Check default models loaded
models = registry.get_all()
test("has models", len(models) >= 3)

# Get model by name
llama = registry.get_model("llama-3.3-70b")
test("llama found", llama is not None)
test("llama has coding score", llama.coding > 0)
test("llama has reasoning score", llama.reasoning > 0)

# Get models for task
coding_models = registry.get_for_task("coding")
test("coding models found", len(coding_models) >= 2)


# ═══════════════════════════════════════════════
# 3. Task Classifier
# ═══════════════════════════════════════════════
print("\n━━━ 3. Task Classifier ━━━")

classifier = TaskClassifier()
test("classifier created", classifier is not None)

# Classify coding task
result = classifier.classify("این کد پایتون چرا خطا میده؟")
test("coding detected", result["type"] == "code")
test("has complexity", "complexity" in result)
test("needs_reasoning set", "needs_reasoning" in result)

# Classify math task
result = classifier.classify("محاسبه انتگرال تابع x^2")
test("math detected", result["type"] == "math")

# Classify text task
result = classifier.classify("این متن رو ترجمه کن")
test("text detected", result["type"] == "text")


# ═══════════════════════════════════════════════
# 4. Smart Router v2
# ═══════════════════════════════════════════════
print("\n━━━ 4. Smart Router v2 ━━━")

router = SmartRouterV2(registry=registry)
test("router created", router is not None)

# Route a coding task
result = router.route("این کد پایتون چرا خطا میده؟")
test("route returns dict", isinstance(result, dict))
test("has model", "model" in result)
test("has provider", "provider" in result)
test("has score", "score" in result)
test("has reasons", "reasons" in result)
test("has alternatives", "alternatives" in result)

# Route a math task
result = router.route("محاسبه انتگرال")
test("math routed", result["model"] is not None)

# Route a simple task
result = router.route("سلام")
test("simple routed", result["model"] is not None)


# ═══════════════════════════════════════════════
# 5. Scoring
# ═══════════════════════════════════════════════
print("\n━━━ 5. Scoring ━━━")

scores = router.score_models("این کد رو دیباگ کن")
test("score_models returns dict", isinstance(scores, dict))
test("has multiple scores", len(scores) >= 2)


# ═══════════════════════════════════════════════
# 6. Failover
# ═══════════════════════════════════════════════
print("\n━━━ 6. Failover ━━━")

result = router.route("کد بنویس", exclude=["github-copilot"])
test("failover works", result["model"] != "github-copilot" or len(registry.get_all()) <= 1)


# ═══════════════════════════════════════════════
# 7. Memory Influence
# ═══════════════════════════════════════════════
print("\n━━━ 7. Memory Influence ━━━")

from core.brain.memory_adapter import MemoryAdapter
adapter = MemoryAdapter(backend=backend)

router_with_mem = SmartRouterV2(registry=registry, adapter=adapter)
result = router_with_mem.route("کد Python بنویس")
test("memory-aware routing works", result["model"] is not None)


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
