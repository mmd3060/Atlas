class ModelDecisionEngine:


    def calculate_score(
        self,
        model,
        task,
        complexity
    ):


        skill = model["skills"].get(
            task,
            5
        )


        score = skill


        # کارهای بزرگ مدل با Context بالا بهترند

        if complexity == "large":

            score += model.get(
                "context",
                5
            ) * 0.1



        # هزینه کمتر امتیاز اضافه می‌گیرد

        score += model.get(
            "cost",
            5
        ) * 0.05



        return score




    def choose_best(
        self,
        models,
        task,
        complexity
    ):


        best_model = None

        best_score = -1



        for name, data in models.items():


            score = self.calculate_score(

                data,

                task,

                complexity

            )


            if score > best_score:

                best_score = score

                best_model = name



        return {

            "model": best_model,

            "score": round(
                best_score,
                2
            )

        }
