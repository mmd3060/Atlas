from core.health.provider_health import ProviderHealthMonitor


health = ProviderHealthMonitor()


health.register_provider("gemini")
health.register_provider("github")


print(health.show_all())


health.mark_error(
    "gemini",
    "Rate limit"
)

health.mark_error(
    "gemini",
    "Timeout"
)


print("\nAfter errors:")
print(health.get_status("gemini"))
