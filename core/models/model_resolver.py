from core.models.model_registry import ModelRegistry


class ModelResolver:
    """
    Resolves a model into executable information.

    Model first architecture:
    Model -> available execution routes
    """

    def __init__(self):

        self.registry = ModelRegistry()


    def resolve(self, model_name):

        model = self.registry.get_model(
            model_name
        )


        if not model:

            raise ValueError(
                f"Unknown model: {model_name}"
            )


        return {

            "model": model.name,

            "providers": model.providers,

            "capabilities": model.capabilities,

            "context_window": model.context_window,

            "speed": model.speed,

            "cost": model.cost,

            "tags": model.tags,

        }



    def available_routes(self, model_name):

        model = self.resolve(
            model_name
        )


        return model["providers"]



    def best_provider(self, model_name):

        routes = self.available_routes(
            model_name
        )


        if not routes:

            return None


        return routes[0]
