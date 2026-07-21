import os

from providers.github import GitHubProvider


def get_provider():
    provider = os.getenv("DEFAULT_PROVIDER", "github")

    if provider == "github":
        return GitHubProvider()

    raise ValueError(f"Unknown provider: {provider}")
