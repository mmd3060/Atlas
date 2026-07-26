from core.intelligence.task_analyzer import TaskAnalyzer
from core.intelligence.model_ranker import ModelRanker
from core.intelligence.decision_engine import DecisionEngine



class IntelligenceEngine:


    def __init__(self):

        self.analyzer = TaskAnalyzer()

        self.ranker = ModelRanker()

        self.decision = DecisionEngine()



    def analyze(self, message):


        # -------------------------
        # Step 1
        # Task Understanding
        # -------------------------

        task = self.analyzer.analyze(
            message
        )


        task_type = task["type"]



        # -------------------------
        # Step 2
        # Model Ranking
        # -------------------------

        ranked_models = self.ranker.rank(
            task_type
        )



        best = ranked_models[0]



        # -------------------------
        # Confidence
        # -------------------------

        if best["score"] >= 70:

            confidence = "high"


        elif best["score"] >= 50:

            confidence = "medium"


        else:

            confidence = "low"



        analysis = {


            "task": task,


            "ranked_models": ranked_models,


            "recommended_model": best["model"],


            "score": best["score"],


            "confidence": confidence

        }



        # -------------------------
        # Step 3
        # Final Decision
        # -------------------------

        decision = self.decision.decide(
            analysis
        )



        analysis["decision"] = decision



        return analysis
