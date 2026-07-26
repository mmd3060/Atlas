class ResponseSynthesizer:


    def synthesize(
        self,
        results
    ):


        # پشتیبانی از MultiModelExecutor

        if isinstance(results, dict):

            if results.get("mode") == "multi":

                results = results.get(
                    "results",
                    []
                )



        successful = [

            r for r in results

            if r.get("status") == "success"

            and r.get("answer")

        ]



        if not successful:

            return {

                "status": "failed",

                "answer": None,

                "reason": "No successful responses"

            }



        # امتیازدهی ساده نسخه v2

        for result in successful:


            score = 0



            # وجود پاسخ

            score += 40



            # طول مناسب پاسخ

            answer = result.get(
                "answer",
                ""
            )


            if len(answer) > 100:

                score += 20



            # زمان پاسخ

            response_time = result.get(
                "time",
                999
            )


            if response_time < 30:

                score += 20



            # بدون خطا

            if not result.get(
                "error"
            ):

                score += 20



            result["_score"] = score




        # انتخاب بهترین پاسخ

        best = max(

            successful,

            key=lambda x: x.get(
                "_score",
                0
            )

        )



        return {


            "status": "success",

            "model": best.get(
                "model"
            ),

            "provider": best.get(
                "provider"
            ),

            "score": best.get(
                "_score"
            ),

            "answer": best.get(
                "answer"
            ),

            "models_compared": len(
                successful
            )

        }
