"""
Router Package

Modules:
    smart_router.py      — Original Smart Router (v1)
    smart_router_v2.py   — Smart Router v2 (model-level selection)
    model_registry.py    — Model profiles with capabilities
    task_classifier.py   — Classify input tasks
"""

from core.router.smart_router import SmartRouter


def get_provider(message):
    """Get provider for a message (legacy interface)."""
    router = SmartRouter()
    decision = router.route(message)
    provider_name = decision.get("execution_provider") or decision.get("provider")
    try:
        from providers.manager import ProviderManager
        manager = ProviderManager()
        manager.set_provider(provider_name)
        return manager
    except ImportError:
        return {"provider": provider_name}
