from core.models.model_resolver import ModelResolver


resolver = ModelResolver()

print(
    resolver.resolve(
        "gemini-2.5-pro"
    )
)

print()

print(
    resolver.best_provider(
        "gemini-2.5-pro"
    )
)
