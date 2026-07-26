from core.models.model_registry import ModelRegistry


class ModelRanker:

    def __init__(self):

        self.registry = ModelRegistry()

    def rank(
        self,
        task
    ):

        models = self.registry.models

        ranking = []

        for name, info in models.items():

            score = info["skills"].get(
                task,
                0
            )

            ranking.append({

                "model": name,

                "score": score,

                "providers": info["providers"]

            })

        ranking.sort(

            key=lambda x: x["score"],

            reverse=True

        )

        return ranking


    def best_model(
        self,
        task
    ):

        ranking = self.rank(
            task
        )

        if not ranking:

            return None

        return ranking[0]
