class DecisionEngine:


    def __init__(self):


        self.task_weights = {


            "code": {

                "quality": 0.5,
                "speed": 0.2,
                "cost": 0.1,
                "health": 0.2

            },


            "math": {

                "quality": 0.6,
                "speed": 0.1,
                "cost": 0.1,
                "health": 0.2

            },


            "text": {

                "quality": 0.3,
                "speed": 0.4,
                "cost": 0.2,
                "health": 0.1

            },


            "long_generation": {

                "quality": 0.4,
                "speed": 0.1,
                "cost": 0.2,
                "health": 0.3

            }

        }



    def calculate_score(
        self,
        provider,
        task,
        complexity
    ):


        weights = self.task_weights.get(
            task,
            self.task_weights["text"]
        )


        score = (

            provider["quality"] * weights["quality"]

            +

            provider["speed"] * weights["speed"]

            +

            provider["cost"] * weights["cost"]

            +

            provider["health"] * weights["health"]

        )


        # مدل‌های دارای context بیشتر برای کارهای بزرگ بهترند

        if complexity == "large":

            score += provider.get(
                "context",
                5
            ) * 0.1



        return score




    def choose_best(
        self,
        providers,
        task,
        complexity="small"
    ):


        best_provider = None

        best_score = -1



        for name, data in providers.items():


            score = self.calculate_score(

                data,

                task,

                complexity

            )



            if score > best_score:

                best_score = score

                best_provider = name



        return {

            "provider": best_provider,

            "score": round(
                best_score,
                2
            )

        }
