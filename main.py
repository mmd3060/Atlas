#!/usr/bin/env python3
"""
Atlas OS v4 — Full Kernel with Multi-Agent, Consensus, Self-Improvement,
Vision Tools (FeyNoBg), and Self-Modifying Agent.
"""

import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core Systems
from core.intelligence.execution_engine import ExecutionEngine
from core.memory.advanced_memory import AdvancedMemory
from core.brain.reasoning_pipeline_v2 import ReasoningPipelineV2
from core.brain.tool_integration import ToolIntegration
from core.tools.tool_system import ToolSystem
from core.interfaces.gateway_manager import GatewayManager
from core.intelligence.consensus_engine import ConsensusEngine
from core.agents.agent_manager import AgentManager
from core.agents.self_modifying_agent import SelfModifyingAgent
from memory.chat_memory import add_message
from stats.token_tracker import get_usage_report
from providers.manager import ProviderManager

# ==========================================
# Atlas OS v4 Kernel Boot
# ==========================================

def boot_atlas():
    print("="*60)
    print("⚡ Atlas OS v4 KERNEL BOOTING...")
    print("="*60)

    systems = {}

    # 1. Engine
    engine = ExecutionEngine()
    print("  [OK] ExecutionEngine v1")

    # 2. Memory (3-layer)
    memory = AdvancedMemory(adapter=None)
    print("  [OK] AdvancedMemory (Episodic + Semantic + Procedural)")

    # 3. Brain Pipeline
    pipeline = ReasoningPipelineV2()
    print("  [OK] ReasoningPipelineV2 (Multi-Memory Integration)")

    # 4. Consensus Engine
    consensus = ConsensusEngine()
    print("  [OK] ConsensusEngine (Multi-Model Voting)")

    # 5. Tool System with FeyNoBg Vision
    tools = ToolSystem()
    print("  [OK] ToolSystem (terminal, file_io, remove_background)")

    # 6. Agent Manager (Multi-Agent)
    agents = AgentManager()
    print("  [OK] AgentManager (Coder, Researcher, Planner, Reviewer)")

    # 7. Self-Modifying Agent (Atlas modifies its OWN code)
    sma = SelfModifyingAgent()
    print("  [OK] SelfModifyingAgent (auto-fix & optimize)")

    # 8. Provider
    provider = ProviderManager()
    provider.set_provider("gemini")
    systems["provider"] = provider

    print("="*60)
    print("🚀 ATLAS OS v4 — FULLY ONLINE")
    print(f"  Provider      : {provider.current_name()}")
    print("  Memory        : 3-Layer (Episodic + Semantic + Procedural)")
    print("  Brain         : Multi-Memory Pipeline v2")
    print("  Tools         : terminal, file_read, file_write, list_files, remove_background")
    print("  Agents        : Coder, Researcher, Planner, Reviewer, Self-Mody")
    print("  Consensus     : Multi-Model Voting Ready")
    print("  Evolution     : Self-Improvement v2 (Active)")
    print("  Autonomy      : Self-Modifying Code")
    print("="*60)

    systems.update({
        "engine": engine,
        "memory": memory,
        "pipeline": pipeline,
        "consensus": consensus,
        "tools": tools,
        "agents": agents,
        "self_modifying": sma,
    })

    return systems


def run(atlas):
    print("\n🗣️  Atlas: سلام MMD! آماده‌ام 🚀")

    provider = atlas.get("provider")

    while True:
        try:
            user_input = input("\n🧑 MMD: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n🛑 Atlas: می‌بینمت دوباره! 🦔⚡")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "shutdown"):
            print("🛑 Atlas: می‌بینمت! خداحافظ 🦔⚡")
            break

        # --- System Commands ---
        if user_input.lower() in ("/status", "status"):
            print(f"  Provider: {provider.current_name()}")
            tools_info = atlas["tools"].list_tools()
            print(f"  Tools: {len(tools_info)} available")
            agents_info = atlas["agents"].list_agents()
            print(f"  Agents: {', '.join(agents_info.keys())}")
            continue

        if user_input.lower() == "/agents":
            for name, info in atlas["agents"].list_agents().items():
                print(f"  🤖 {name}: {info['role']}")
            continue

        if user_input.lower() == "/memory":
            print("  💾 Memory Systems: Episodic + Semantic + Procedural")
            # Try to get episodic recalls
            mem = atlas["memory"]
            recent = mem.episodic.get_recent(hours=1)
            print(f"  Recent events:  {len(recent)}")
            continue

        if user_input.lower() == "/consensus":
            print("  🧠 Consensus Engine: Active")
            print("  Modes: single | dual | triple | debate | voting")
            continue

        if user_input.lower() == "/tools":
            for name, info in atlas["tools"].list_tools().items():
                print(f"  🔧 {name}: {info['description']}")
            continue

        # Provider Switch
        if user_input.lower().startswith("/provider"):
            parts = user_input.split()
            if len(parts) >= 2:
                try:
                    p = ProviderManager()
                    p.set_provider(parts[1])
                    print(f"  ✅ Provider changed to: {p.current_name()}")
                    provider = p
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            else:
                print(f"  Usage: /provider <name>")
            continue

        # Self-Modify Command
        if user_input.lower().startswith("/modify"):
            parts = user_input.split(" ", 2)
            if len(parts) < 2:
                print("  Usage: /modify <file_path>")
                continue
            file_path = parts[1]
            file_data = atlas["self_modifying"].read_code(file_path)
            if "error" in file_data:
                print(f"  ❌ {file_data['error']}")
            else:
                print(f"  📄 {file_path}: {file_data['lines']} lines, {file_data['size']} bytes")
            continue

        # --- Main Inference (via ExecutionEngine) ---
        print("  ⚡ Atlas is thinking...", end=" ", flush=True)
        start = time.time()

        try:
            add_message("user", user_input)

            # Check if this triggers a vision tool
            if "حذف" in user_input and ("پس‌زمینه" in user_input or "background" in user_input.lower()):
                response = "🖼️  Vision tool ready! Send me an image path with /remove_bg <file> to use FeyNoBg."
            else:
                # Normal response via pipeline
                # (In production, this calls the actual ExecutionEngine)
                response = (
                    f"🧠 Atlas v4: پیام شما دریافت شد. "
                    f"مدل: {provider.current_name()}. "
                    f"ابزارهای فعال: {len(atlas['tools'].list_tools())}. "
                    f"سیستم‌عامل Atlas OS فعال است."
                )

            elapsed = time.time() - start
            print(f"\r  ⚡ Atlas ({elapsed:.2f}s):\n  {response}")
            add_message("assistant", response)

        except Exception as e:
            print(f"\n  ❌ Kernel Error: {e}")


if __name__ == "__main__":
    print("🚀 Atlas OS v4 - Full Autonomy Boot")
    atlas_system = boot_atlas()
    run(atlas_system)
    print("\n👋 Atlas OS Halted.")