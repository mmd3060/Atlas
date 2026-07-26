from core.models.model_registry import ModelRegistry


registry = ModelRegistry()


print(
    registry.get_model(
        "gpt-4.1"
    )
)


print("================")


print(
    registry.all_models()
)
