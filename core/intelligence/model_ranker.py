from core.models.model_registry import ModelRegistry


class ModelRanker:


    def __init__(self):

        self.registry = ModelRegistry()



    def calculate_score(
        self,
        model_name,
        task_type,
        difficulty="normal"
    ):


        model = self.registry.get_model(
            model_name
        )


        if model is None:

            return 0



        capabilities = model.get(
            "capabilities",
            {}
        )


        score = 0



        # -------------------------
        # Task Capability
        # -------------------------

        score += (
            capabilities.get(
                task_type,
                5
            )
            * 5
        )



        # -------------------------
        # Reasoning Intelligence
        # -------------------------

        score += (
            capabilities.get(
                "reasoning",
                5
            )
            * 2
        )



        # -------------------------
        # Cost Efficiency
        # -------------------------

        score += model.get(
            "cost",
            5
        )



        # -------------------------
        # Speed Optimization
        # -------------------------

        if difficulty == "low":

            score += model.get(
                "speed",
                5
            )



        # -------------------------
        # Context For Complex Tasks
        # -------------------------

        if difficulty == "high":

            score += model.get(
                "context",
                5
            )



        return round(
            score,
            2
        )



    def rank(
        self,
        task_type,
        difficulty="normal"
    ):


        results = []



        models = self.registry.list_models()



        for model_name in models:


            score = self.calculate_score(
                model_name,
                task_type,
                difficulty
            )


            results.append({

                "model": model_name,

                "score": score

            })



        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        return results



    def best_model(
        self,
        task_type,
        difficulty="normal"
    ):


        ranked = self.rank(
            task_type,
            difficulty
        )


        return ranked[0]
