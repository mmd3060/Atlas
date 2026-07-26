from core.intelligence.model_executor import ModelExecutor


class MultiModelExecutor:


    def __init__(self):

        self.executor = ModelExecutor()



    def execute(
        self,
        decision,
        messages
    ):


        results = []


        models = [
            decision["model"]
        ]


        models.extend(
            decision.get(
                "backup_models",
                []
            )
        )


        print(
            "🧠 Multi Model Execution"
        )


        for model in models:


            print(
                f"🤖 Running: {model}"
            )


            model_decision = {

                "model": model

            }


            result = self.executor.execute(
                model_decision,
                messages
            )


            results.append(
                result
            )


        return results
