from core.models.model_registry import ModelRegistry


class ModelResolver:

    def __init__(self):

        self.registry = ModelRegistry()


    def resolve(self, model_name):

        models = self.registry.get_models()

        if model_name not in models:
            raise ValueError(
                f"Unknown model: {model_name}"
            )

        model = models[model_name]

        return {

            "model": model_name,

            "providers": model["providers"],

            "cost": model["cost"],

            "context": model["context"],

            "skills": model["skills"]

        }


    def best_provider(self, model_name):

        info = self.resolve(model_name)

        return info["providers"][0]
