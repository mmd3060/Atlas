from core.models.model_registry import ModelRegistry


registry = ModelRegistry()


print(
    registry.get_models()
)
