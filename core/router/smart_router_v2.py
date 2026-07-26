"""
Atlas Smart Router v2
Model First Architecture

Message
   |
Task Classifier
   |
Model Ranker
   |
Model Resolver
   |
Execution
"""

from typing import Dict, Any, List

from core.router.task_classifier import TaskClassifier
from core.models.model_ranker import ModelRanker


class SmartRouterV2:


    def __init__(self):

        self.classifier = TaskClassifier()
        self.ranker = ModelRanker()



    def route(
        self,
        message: str,
        exclude: List[str] = None
    ) -> Dict[str, Any]:


        exclude = exclude or []


        task = self.classifier.classify(
            message
        )


        task_type = task.get(
            "type",
            "reasoning"
        )


        ranking = self.ranker.rank(
            task_type
        )


        ranking = [
            x for x in ranking
            if x["model"] not in exclude
        ]



        if not ranking:

            return {
                "model": None,
                "reason": "no model available"
            }



        best = ranking[0]


        return {

            "model": best["model"],

            "score": best["score"],

            "capabilities": best["capabilities"],

            "alternatives": ranking[1:3],

            "task": task

        }
