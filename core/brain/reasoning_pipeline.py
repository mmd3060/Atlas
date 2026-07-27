"""
Enhanced Reasoning Pipeline with Tool Calling Support.

Flow:
    User -> Analyze -> Decision (Tool or LLM) -> Execute -> Synthesize -> Respond
"""

import json
import re
from typing import Any, Dict, List, Optional

from core.brain.input_analyzer import InputAnalyzer
from core.brain.prompt_builder import PromptBuilder
from core.brain.response_memory import ResponseMemory
from core.brain.memory_context import MemoryContext
from core.brain.tool_integration import ToolIntegration
from core.tools.tool_system import ToolSystem


class ReasoningPipeline:
    """
    Enhanced reasoning pipeline with tool calling capability.
    """

    def __init__(self, adapter=None):
        self._adapter = adapter
        self._analyzer = InputAnalyzer()
        self._memory_context = MemoryContext(adapter=adapter) if adapter else None
        self._prompt_builder = PromptBuilder()
        self._response_memory = ResponseMemory(adapter=adapter) if adapter else None
        self._tool_system = ToolSystem()

    def process(self, message: str) -> Dict[str, Any]:
        """
        Full reasoning pipeline with tool calling.
        """
        # Step 1: Analyze input
        analysis = self._analyzer.analyze(message)
        
        # Step 2: Recall relevant memories
        memory_ctx = {}
        if self._memory_context:
            memory_ctx = self._memory_context.build(message)

        # Step 3: Decide - Tool or Direct LLM?
        decision = self._make_decision(message, analysis)
        
        response = None
        tool_results = []
        
        if decision.get("use_tool"):
            # Tool calling path
            tool_name = decision.get("tool")
            tool_args = decision.get("args", {})
            
            # Execute via ToolSystem
            result = self._execute_tool_safely(tool_name, tool_args)
            tool_results.append(result)
            
            # If tool succeeded, synthesize response with tool result
            if result.get("status") == "success":
                response = self._synthesize_with_tool(message, result)
            else:
                response = f"Tool execution failed: {result.get('reason', 'Unknown error')}"
        else:
            # Direct LLM path (placeholder for now)
            response = self._get_llm_response(message, analysis, memory_ctx)

        # Store response in memory
        if self._response_memory and response:
            self._response_memory.remember_response(
                message=message,
                response=str(response),
                metadata={"task_type": analysis.get("task_type")},
            )

        return {
            "analysis": analysis,
            "memory_context": memory_ctx,
            "decision": decision,
            "tool_results": tool_results,
            "response": response,
        }

    def _make_decision(self, message: str, analysis: Dict) -> Dict[str, Any]:
        """
        Decide: Use tool or direct LLM?
        """
        task_type = analysis.get("task_type", "general")
        msg_lower = message.lower()

        # Explicit tool commands
        tool_triggers = {
            "file_read": ["بخوان", "بخواند", "محتوی", "read file", "cat "],
            "file_write": ["بنویس در فایل", "ذخیره در فایل", "write file", "save to file"],
            "terminal": ["اجرا", "دستور", "run ", "execute ", "bash "],
            "list_files": ["لیست فایل", "فایل‌ها", "ls ", "list files"],
        }

        for tool, triggers in tool_triggers.items():
            if any(t in msg_lower for t in triggers):
                # Extract arguments
                args = self._extract_tool_args(message, tool)
                return {
                    "use_tool": True,
                    "tool": tool,
                    "args": args,
                    "reason": f"Detected {tool} trigger",
                }

        # Coding task - might need file operations
        if analysis.get("task_type") == "coding":
            return {
                "use_tool": False,
                "reason": "Direct LLM for coding",
            }

        return {
            "use_tool": False,
            "reason": "General conversation - direct LLM",
        }

    def _extract_tool_args(self, message: str, tool: str) -> Dict[str, Any]:
        """Extract arguments from natural language."""
        args = {}
        
        if tool == "file_read" or tool == "file_write":
            # Try to extract file path
            import re
            # Look for file paths
            paths = re.findall(r'[\w/.-]+\.(py|txt|md|json|yaml|yml|sh)', message)
            if paths:
                args["path"] = paths[0]
            else:
                # Try to find quoted strings
                quoted = re.findall(r'["\']([^"\']+)["\']', message)
                if quoted:
                    args["path"] = quoted[0]
        
        if tool == "terminal":
            # Extract command after trigger words
            import re
            match = re.search(r'(اجرا|دستور|run|execute|bash)\s+(.+)', message, re.IGNORECASE)
            if match:
                args["command"] = match.group(2).strip()
        
        if tool == "file_write":
            # Try to extract content
            import re
            content_match = re.search(r'(?:با محتوای|content|متن)\s*[:\-]\s*(.+)', message, re.IGNORECASE)
            if content_match:
                args["content"] = content_match.group(1).strip()
        
        return args

    def _execute_tool_safely(self, tool_name: str, args: Dict) -> Dict:
        """Execute tool via ToolSystem with permission check."""
        from core.tools.tool_system import ToolSystem
        tool_system = ToolSystem()
        return tool_system.execute(tool_name, args)

    def _synthesize_with_tool(self, message: str, tool_result: Dict) -> str:
        """Create response incorporating tool result."""
        result = tool_result.get("result", {})
        
        if result.get("stdout") is not None:
            return f"✅ Command executed:\n```\n{result.get('stdout', '')}\n```"
        
        if result.get("content") is not None:
            content = result.get("content", "")
            return f"📄 File content:\n```\n{content[:2000]}\n```"
        
        if result.get("files") is not None:
            files = result.get("files", [])
            out = f"📁 Directory listing ({len(files)} items):\n"
            for f in files[:20]:
                icon = "📁" if f.get("is_dir") else "📄"
                out += f"  {icon} {f['name']}\n"
            return out
        
        if result.get("total_memories") is not None:
            return f"💾 Memory Status: {result.get('total_memories')} memories stored."
        
        return f"Tool executed: {result}"

    def _get_llm_response(self, message: str, analysis: Dict, memory_ctx: Dict) -> str:
        """Get response from LLM (placeholder - uses Engine)."""
        # This would call ExecutionEngine in production
        return f"[LLM Response for: {message[:50]}...]"