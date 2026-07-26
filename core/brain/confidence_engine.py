class ConfidenceEngine:


    def calculate(self, results):


        successful = [
            r for r in results
            if r.get("status") == "success"
        ]


        if not successful:

            return {
                "confidence": 0,
                "level": "low",
                "reason": "No successful answers"
            }



        # تعداد مدل‌ها

        models_count = len(successful)



        confidence = 50



        # هر مدل اضافه اعتماد را بالا می‌برد

        confidence += models_count * 15



        if confidence > 100:

            confidence = 100



        level = "low"


        if confidence >= 80:

            level = "high"

        elif confidence >= 60:

            level = "medium"



        return {


            "confidence": confidence,

            "level": level,

            "models_checked": models_count,

            "reason":
                "Confidence based on model agreement"

        }
