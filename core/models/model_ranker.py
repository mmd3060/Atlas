from typing import List, Dict, Any

from core.models.model_registry import ModelRegistry


class ModelRanker:
    """
    Atlas OS Model Intelligence

    انتخاب بهترین مدل بدون وابستگی به Provider
    """

    def __init__(self):
        self.registry = ModelRegistry()


    def rank(
        self,
        task: str
    ) -> List[Dict[str, Any]]:

        results = []


        for model in self.registry.get_all():

            caps = model.capabilities


            capability_map = {

                "coding": caps.coding,
                "code": caps.coding,

                "math": caps.math,

                "reasoning": caps.reasoning,

                "text": caps.text,

                "writing": caps.text,

                "vision": caps.vision,

            }


            task_score = capability_map.get(
                task,
                caps.reasoning
            )


            score = (

                task_score * 0.60

                +

                model.speed * 0.15

                +

                model.cost * 0.10

                +

                caps.reasoning * 0.15

            )


            results.append({

                "model": model.name,

                "score": round(
                    score,
                    4
                ),

                "capabilities": {

                    "coding": caps.coding,

                    "math": caps.math,

                    "reasoning": caps.reasoning,

                    "text": caps.text,

                    "vision": caps.vision,

                }

            })


        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )


        return results



    def best_model(
        self,
        task: str
    ):

        ranking = self.rank(task)

        if not ranking:
            return None

        return ranking[0]
