from core.models.model_registry import ModelRegistry
from core.decision.model_decision import ModelDecisionEngine


registry = ModelRegistry()

brain = ModelDecisionEngine()


models = registry.get_models()


print(
    brain.choose_best(
        models,
        "math",
        "small"
    )
)


print(
    brain.choose_best(
        models,
        "code",
        "medium"
    )
)
