from core.fallback.fallback_manager import FallbackManager
from core.health.provider_health import ProviderHealthMonitor



health = ProviderHealthMonitor()


health.register_provider("github")
health.register_provider("gemini")
health.register_provider("openrouter")



fallback = FallbackManager()



print("Normal:")

print(
    fallback.choose_provider(
        "code",
        health
    )
)



print("\nGitHub Failed:")


health.mark_error("github", "error")
health.mark_error("github", "error")
health.mark_error("github", "error")



print(
    fallback.choose_provider(
        "code",
        health
    )
)
