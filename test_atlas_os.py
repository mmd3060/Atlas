#!/usr/bin/env python3
"""
Atlas OS v4 — Comprehensive Test Suite
Tests all major systems: Memory, Tools, Agents, Voice, Web Search, etc.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASSED = 0
FAILED = 0

def test(name, condition):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}")

# ==========================================
# 1. Tool System
# ==========================================
print("\n=== Tool System ===")
from core.tools.tool_system import ToolSystem
from core.tools.file_manager import FileManager
from core.tools.web_search import WebSearchTool
from core.tools.code_executor import CodeExecutor
from core.tools.permission_manager import PermissionManager

ts = ToolSystem()
tools = ts.list_tools()
test("ToolSystem created", ts is not None)
test("Has 9+ tools", len(tools) >= 9)
test("terminal tool exists", "terminal" in tools)
test("web_search tool exists", "web_search" in tools)
test("code_exec tool exists", "code_exec" in tools)
test("search_files tool exists", "search_files" in tools)
test("file_read tool exists", "file_read" in tools)
test("file_write tool exists", "file_write" in tools)
test("list_files tool exists", "list_files" in tools)
test("remove_background tool exists", "remove_background" in tools)
test("fetch_url tool exists", "fetch_url" in tools)

pm = PermissionManager()
test("PermissionManager created", pm is not None)
r = pm.check_permission("file_read", {})
test("file_read is safe", r["allowed"])
r2 = pm.check_permission("terminal", {"command": "rm -rf /"})
test("rm -rf is blocked", not r2["allowed"])

fm = FileManager()
test("FileManager created", fm is not None)
test("File search works", "files" in fm.search("*.py"))

ce = CodeExecutor()
result = ce.evaluate("2 + 2")
test("CodeExecutor works", result["result"] == "4")
result2 = ce.execute_python("print('hello atlas')")
test("Python exec works", result2["status"] == "success")

ws = WebSearchTool()
test("WebSearchTool created", ws is not None)

# ==========================================
# 2. Agents
# ==========================================
print("\n=== Agents ===")
from core.agents.agent_manager import AgentManager
from core.agents.orchestrator import AgentOrchestrator
from core.agents.self_modifying_agent import SelfModifyingAgent

am = AgentManager()
agents = am.list_agents()
test("AgentManager created", am is not None)
test("Has 4 agents", len(agents) == 4)
test("Coder agent exists", "coder" in agents)
test("Researcher agent exists", "researcher" in agents)
test("Planner agent exists", "planner" in agents)
test("Reviewer agent exists", "reviewer" in agents)
test("Dispatch works", "coder" in am.dispatch("coder", "write code"))

ao = AgentOrchestrator()
test("Orchestrator created", ao is not None)
result = ao.solve("Build a REST API")
test("Orchestrator decomposes goals", len(result["sub_tasks"]) >= 2)
test("Orchestrator has final answer", "final" in result)

sma = SelfModifyingAgent()
test("SelfModifyingAgent created", sma is not None)
test("Read code works", "content" in sma.read_code("main.py"))
test("List backups works", isinstance(sma.list_backups(), list))

# ==========================================
# 3. Memory
# ==========================================
print("\n=== Advanced Memory ===")
from core.memory.episodic_memory import EpisodicMemory
from core.memory.semantic_memory import SemanticMemory
from core.memory.procedural_memory import ProceduralMemory
from core.memory.advanced_memory import AdvancedMemory

em = EpisodicMemory()
ep = em.record_event("conversation", "User said hello", {"user": "MMD"})
test("Episodic record works", ep is not None)
test("Episodic recall works", len(em.recall("hello")) > 0)

sm = SemanticMemory()
sm.add_fact("Atlas", "is", "an OS")
test("Semantic add works", len(sm.query("atlas")) > 0)

pm2 = ProceduralMemory()
pm2.record_procedure("deploy", ["git push", "run tests"])
test("Procedural works", len(pm2.get_steps("deploy")) == 2)

am2 = AdvancedMemory()
am2.remember_event("action", "Built tool system", {"user": "MMD"})
am2.remember_fact("Atlas", "has", "memory")
am2.remember_procedure("test", ["run pytest"])
result = am2.recall_full("Atlas")
test("AdvancedMemory works", "episodes" in result)
test("Facts stored", len(result.get("facts", {})) > 0)

# ==========================================
# 4. Intelligence
# ==========================================
print("\n=== Intelligence Engine ===")
from core.intelligence.execution_engine import ExecutionEngine
from core.intelligence.consensus_engine import ConsensusEngine

ee = ExecutionEngine()
test("ExecutionEngine created", ee is not None)
test("Has execute method", hasattr(ee, "execute"))

ce2 = ConsensusEngine()
test("ConsensusEngine created", ce2 is not None)

# ==========================================
# 5. Voice Gateway
# ==========================================
print("\n=== Voice & Vision ===")
from core.interfaces.voice_gateway import VoiceGateway

vg = VoiceGateway()
test("VoiceGateway created", vg is not None)
test("detect_language works", vg.detect_language("سلام دنیا") == "fa")
test("detect_language en", vg.detect_language("hello world") == "en")

# ==========================================
# 6. Cron Scheduler
# ==========================================
print("\n=== Cron Scheduler ===")
from core.tools.cron_scheduler import CronScheduler

cs = CronScheduler()
test("CronScheduler created", cs is not None)
test("No jobs initially", len(cs.list_jobs()) == 0)
cs.register("test_job", 60, lambda: "ok")
test("Job registered", len(cs.list_jobs()) == 1)

# ==========================================
# 7. Main Entry Points
# ==========================================
print("\n=== Entry Points ===")
test("main.py exists", os.path.exists("main.py"))
test("telegram_bot.py exists", os.path.exists("telegram_bot.py"))
test("requirements.txt exists", os.path.exists("requirements.txt"))
test("README.md exists", os.path.exists("README.md"))
test(".env exists", os.path.exists(".env"))

# ==========================================
# Results
# ==========================================
print("\n" + "=" * 50)
total = PASSED + FAILED
print(f"📊 Results: {PASSED} passed, {FAILED} failed, {total} total")
print("=" * 50)

if FAILED > 0:
    sys.exit(1)
else:
    print("🎉 ALL TESTS PASSED!")
    sys.exit(0)