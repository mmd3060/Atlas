import os

from providers.github import GitHubProvider
from providers.nvidia import NvidiaProvider
from providers.openrouter import OpenRouterProvider


def get_provider():
    provider = os.getenv("DEFAULT_PROVIDER", "github").lower()

    providers = {
        "github": GitHubProvider,
        "nvidia": NvidiaProvider,
        "openrouter": OpenRouterProvider,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")

    return providers[provider]()
