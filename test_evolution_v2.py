"""
Agent Evolution Core v2 — Autonomous Experimentation — TDD Tests

Flow:
  Observation → Reflection → Hypothesis → Experiment → Evaluation → Adopt/Reject

This is where Atlas becomes a true evolutionary agent.
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
    from core.evolution.hypothesis_engine import HypothesisEngine
    from core.evolution.experiment_planner import ExperimentPlanner
    from core.evolution.experiment_runner import ExperimentRunner
    from core.evolution.evaluator import ExperimentEvaluator
    from core.evolution.evolution_memory import EvolutionMemory
    from core.evolution.evolution_controller import EvolutionController
    test("import HypothesisEngine", True)
    test("import ExperimentPlanner", True)
    test("import ExperimentRunner", True)
    test("import ExperimentEvaluator", True)
    test("import EvolutionMemory", True)
    test("import EvolutionController", True)
except ImportError as e:
    test("import modules", False)
    print(f"    Error: {e}")
    backend.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    sys.exit(1)


# ═══════════════════════════════════════════════
# 2. Hypothesis Engine
# ═══════════════════════════════════════════════
print("\n━━━ 2. Hypothesis Engine ━━━")

hyp_engine = HypothesisEngine()
test("hypothesis engine created", hyp_engine is not None)

# Generate hypothesis from observations
observations = [
    {"task": "coding", "provider": "github", "success": True},
    {"task": "coding", "provider": "github", "success": True},
    {"task": "coding", "provider": "github", "success": False},
    {"task": "coding", "provider": "gemini", "success": True},
    {"task": "coding", "provider": "gemini", "success": False},
    {"task": "coding", "provider": "gemini", "success": False},
]

hypothesis = hyp_engine.generate(observations)
test("hypothesis has statement", "statement" in hypothesis)
test("hypothesis has confidence", "confidence" in hypothesis)
test("hypothesis has target", "target" in hypothesis)
test("hypothesis confidence > 0", hypothesis["confidence"] > 0)


# ═══════════════════════════════════════════════
# 3. Experiment Planner
# ═══════════════════════════════════════════════
print("\n━━━ 3. Experiment Planner ━━━")

planner = ExperimentPlanner()
test("planner created", planner is not None)

plan = planner.plan(hypothesis)
test("plan has sample_size", "sample_size" in plan)
test("plan has control", "control" in plan)
test("plan has variant", "variant" in plan)
test("plan has duration", "duration" in plan)
test("sample_size reasonable", plan["sample_size"] >= 5)


# ═══════════════════════════════════════════════
# 4. Experiment Runner
# ═══════════════════════════════════════════════
print("\n━━━ 4. Experiment Runner ━━━")

runner = ExperimentRunner()
test("runner created", runner is not None)

# Simulate experiment results
results = runner.simulate(plan)
test("results has control", "control" in results)
test("results has variant", "variant" in results)
test("control has success_rate", "success_rate" in results["control"])
test("variant has success_rate", "success_rate" in results["variant"])


# ═══════════════════════════════════════════════
# 5. Evaluator
# ═══════════════════════════════════════════════
print("\n━━━ 5. Evaluator ━━━")

evaluator = ExperimentEvaluator()
test("evaluator created", evaluator is not None)

# Evaluate with variant winning
results_win = {"control": {"success_rate": 0.65}, "variant": {"success_rate": 0.82}}
decision = evaluator.evaluate(results_win)
test("evaluate returns dict", isinstance(decision, dict))
test("has verdict", "verdict" in decision)
test("variant wins", decision["verdict"] == "adopt")
test("has confidence", "confidence" in decision)

# Evaluate with no significant difference
results_tie = {"control": {"success_rate": 0.70}, "variant": {"success_rate": 0.71}}
decision2 = evaluator.evaluate(results_tie)
test("tie rejected", decision2["verdict"] == "reject")


# ═══════════════════════════════════════════════
# 6. Evolution Memory
# ═══════════════════════════════════════════════
print("\n━━━ 6. Evolution Memory ━━━")

evo_memory = EvolutionMemory()
test("evolution memory created", evo_memory is not None)

# Record evolution
evo_memory.record({
    "hypothesis": "github better for coding",
    "verdict": "adopt",
    "confidence": 0.85,
    "change": {"task": "coding", "provider": "github", "old": 0.5, "new": 0.55},
})
test("evolution recorded", evo_memory.count() >= 1)

# Get history
history = evo_memory.get_history()
test("history is list", isinstance(history, list))
test("history has entries", len(history) >= 1)


# ═══════════════════════════════════════════════
# 7. Evolution Controller (Full Cycle)
# ═══════════════════════════════════════════════
print("\n━━━ 7. Evolution Controller ━━━")

from core.evolution.weight_optimizer import WeightOptimizer
from core.brain.memory_adapter import MemoryAdapter

adapter = MemoryAdapter(backend=backend)
optimizer = WeightOptimizer()

controller = EvolutionController(
    adapter=adapter,
    optimizer=optimizer,
    hypothesis_engine=hyp_engine,
    planner=planner,
    runner=runner,
    evaluator=evaluator,
    evolution_memory=evo_memory,
)
test("controller created", controller is not None)

# Run full evolution cycle
result = controller.evolve(observations)
test("evolve returns dict", isinstance(result, dict))
test("has hypothesis", "hypothesis" in result)
test("has decision", "decision" in result)


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
