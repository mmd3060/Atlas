from core.models.model_registry import ModelRegistry


registry = ModelRegistry()


print(
    registry.get_model(
        "gpt-4.1"
    )
)


print("================")


print(
    registry.get_provider(
        "gemini-2.5-pro"
    )
)


print("================")


print(
    registry.list_models()
)
