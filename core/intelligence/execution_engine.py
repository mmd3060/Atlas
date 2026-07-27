"""
Execution Engine v1 — The Core Orchestrator for AI Inference.

This is the kernel of Atlas OS.
All requests pass through here.

Flow:
    User -> SmartRouter -> resolve_provider() -> execute() -> response
"""

import os
from typing import Any, Dict, List, Optional


class ExecutionEngine:
    """
    Core executor for all AI tasks.
    """

    def __init__(self, adapter=None):
        self._adapter = adapter
        self._provider_manager = None
        self._initialized = False
        self._current_provider = "auto"

    def _ensure_init(self):
        """Lazy init to avoid circular imports."""
        if self._initialized:
            return
        try:
            from providers.manager import ProviderManager
            self._provider_manager = ProviderManager
        except ImportError:
            self._provider_manager = None
        self._initialized = True

    def resolve_provider(self, provider_name: str = None):
        """
        Resolve provider name to a ProviderManager instance.
        """
        self._ensure_init()
        if self._provider_manager is None:
            return None
            
        manager = self._provider_manager()
        
        if provider_name:
            try:
                manager.set_provider(provider_name.lower())
            except (ValueError, AttributeError):
                manager.reset()
        else:
            # Use SmartRouter to decide
            try:
                from core.router.smart_router_v2 import SmartRouterV2
                router = SmartRouterV2()
                decision = router.route("general query")
                provider = decision.get("provider", "gemini")
                manager.set_provider(provider)
                self._current_provider = provider
            except Exception:
                manager.reset()
                self._current_provider = manager.current_name()
        
        return manager

    def execute(self, message: str, provider_name: str = None) -> str:
        """
        Execute a chat request via a resolved provider.

        Args:
            message: User message string
            provider_name: Optional specific provider name

        Returns:
            Response string from the AI model
        """
        manager = self.resolve_provider(provider_name)
        
        if manager is None:
            return "Execution Engine: Providers not available."
        
        # Format messages for LLM
        messages = [{"role": "user", "content": message}]
        
        try:
            response = manager.chat(messages)
            return response
        except Exception as e:
            # Fallback to next provider
            try:
                manager.next_provider()
                self._current_provider = manager.current_name()
                return manager.chat(messages)
            except Exception:
                return f"Kernel Execution Error: {str(e)}"