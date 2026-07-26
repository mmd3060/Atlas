from core.models.model_registry import ModelRegistry



class DecisionEngine:


    def __init__(self):

        self.registry = ModelRegistry()



    def decide(
        self,
        analysis
    ):


        task = analysis["task"]

        ranked = analysis["ranked_models"]



        best_model = ranked[0]



        # پیدا کردن مدل‌های نزدیک

        backup_models = []


        for model in ranked[1:]:


            if (
                best_model["score"]
                -
                model["score"]
                <= 3
            ):

                backup_models.append(
                    model["model"]
                )



        score_gap = 0


        if len(ranked) > 1:

            score_gap = (
                best_model["score"]
                -
                ranked[1]["score"]
            )



        # اطلاعات مدل از Registry

        model_info = self.registry.get_model(
            best_model["model"]
        )


        provider = None


        if model_info:

            provider = model_info.get(
                "provider"
            )



        decision = {


            "model": best_model["model"],


            "provider": provider,


            "score": best_model["score"],


            "backup_models": backup_models,


            "score_gap": score_gap,


            "task_type": task["type"],


            "difficulty": task["difficulty"],


            "requires_tool": task["requires_tool"],


            "use_multi_model": False,


            "mode": "single",


            "reason": ""

        }



        # -------------------------
        # Decision Logic
        # -------------------------


        if task["requires_tool"]:


            decision["reason"] = (
                "Task requires external tool"
            )



        elif task["difficulty"] == "high":


            decision["use_multi_model"] = True

            decision["mode"] = (
                "multi_reasoning"
            )


            decision["reason"] = (
                "High difficulty task requires "
                "multiple model reasoning"
            )



        elif score_gap <= 1 and backup_models:


            decision["use_multi_model"] = True

            decision["mode"] = (
                "verification"
            )


            decision["reason"] = (
                "Models have similar scores, "
                "verification recommended"
            )



        else:


            decision["reason"] = (
                "Best model selected by intelligence score"
            )



        return decision
